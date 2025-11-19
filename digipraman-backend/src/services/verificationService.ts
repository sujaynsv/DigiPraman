import { v4 as uuidv4 } from 'uuid';
import { getClient, query } from '../db';
import { AppError } from '../utils/AppError';
import { RequirementType, RequirementStatus, VerificationDetail, VerificationSummary } from '../types';

interface RequirementInput {
  label: string;
  type: RequirementType;
  required?: boolean;
  instructions?: string;
  sortOrder?: number;
}

const mapVerificationSummary = (row: any): VerificationSummary => ({
  id: row.id,
  loanId: row.loan_id,
  loanRefNo: row.loan_ref_no,
  schemeId: row.scheme_id,
  status: row.status,
  currentTier: row.current_tier || undefined,
  dueDate: row.due_date || undefined,
  createdAt: row.created_at,
  sanctionedAmount: Number(row.sanctioned_amount),
  purpose: row.purpose || undefined,
  risk: row.risk_score !== null ? {
    score: Number(row.risk_score),
    tier: row.risk_tier,
  } : undefined,
});

export const getBeneficiaryVerifications = async (beneficiaryId: string): Promise<VerificationSummary[]> => {
  const result = await query(
    `SELECT vr.id,
            vr.loan_id,
            vr.status,
            vr.current_tier,
            vr.due_date,
            vr.created_at,
            la.loan_ref_no,
            la.scheme_id,
            la.sanctioned_amount,
            la.purpose,
            ra.risk_score,
            ra.risk_tier
       FROM verification_requests vr
       JOIN loan_applications la ON la.id = vr.loan_id
  LEFT JOIN risk_analyses ra ON ra.verification_id = vr.id
      WHERE la.beneficiary_id = $1
      ORDER BY vr.created_at DESC`,
    [beneficiaryId],
  );

  return result.rows.map(mapVerificationSummary);
};

export const getVerificationDetail = async (verificationId: string): Promise<VerificationDetail> => {
  const detailsResult = await query(
    `SELECT vr.id,
            vr.loan_id,
            vr.status,
            vr.current_tier,
            vr.due_date,
            vr.thresholds_ref,
            vr.created_at,
            vr.initiated_by,
            la.loan_ref_no,
            la.scheme_id,
            la.org_id,
            la.sanctioned_amount,
            la.purpose,
            la.beneficiary_id,
            ra.risk_score,
            ra.risk_tier,
            ra.flags,
            ra.explanation,
            ra.recommended_action
       FROM verification_requests vr
       JOIN loan_applications la ON la.id = vr.loan_id
  LEFT JOIN risk_analyses ra ON ra.verification_id = vr.id
      WHERE vr.id = $1
      LIMIT 1`,
    [verificationId],
  );

  if (detailsResult.rowCount === 0) {
    throw new AppError('Verification not found', 404);
  }

  const [row] = detailsResult.rows;
  const requirementsPromise = query(
    `SELECT id,
            label,
            type,
            required,
            instructions,
            status,
            sort_order,
            created_at
       FROM verification_requirements
      WHERE verification_id = $1
      ORDER BY sort_order ASC`,
    [verificationId],
  );

  const evidencePromise = query(
    `SELECT id,
            verification_id,
            requirement_id,
            type,
            storage_url,
            file_key,
            ST_Y(gps::geometry) AS latitude,
            ST_X(gps::geometry) AS longitude,
            captured_at,
            uploaded_at,
            metadata
       FROM evidence_items
      WHERE verification_id = $1
      ORDER BY captured_at DESC NULLS LAST`,
    [verificationId],
  );

  const decisionsPromise = query(
    `SELECT id,
            officer_id,
            decision,
            notes,
            attachments,
            decided_at
       FROM decisions
      WHERE verification_id = $1
      ORDER BY decided_at DESC`,
    [verificationId],
  );

  const [requirements, evidence, decisions] = await Promise.all([
    requirementsPromise,
    evidencePromise,
    decisionsPromise,
  ]);

  return {
    id: row.id,
    loanId: row.loan_id,
    loanRefNo: row.loan_ref_no,
    schemeId: row.scheme_id,
    orgId: row.org_id,
    beneficiaryId: row.beneficiary_id,
    status: row.status,
    currentTier: row.current_tier || undefined,
    dueDate: row.due_date || undefined,
    initiatedBy: row.initiated_by || undefined,
    thresholdsRef: row.thresholds_ref || undefined,
    createdAt: row.created_at,
    sanctionedAmount: Number(row.sanctioned_amount),
    purpose: row.purpose || undefined,
    risk: row.risk_score !== null ? {
      score: Number(row.risk_score),
      tier: row.risk_tier,
      flags: row.flags || [],
      explanation: row.explanation || [],
      recommendedAction: row.recommended_action || undefined,
    } : undefined,
    requirements: requirements.rows.map((req) => ({
      id: req.id,
      label: req.label,
      type: req.type as RequirementType,
      required: req.required,
      instructions: req.instructions || undefined,
      status: req.status as RequirementStatus,
      sortOrder: req.sort_order,
      createdAt: req.created_at,
    })),
    evidence: evidence.rows.map((item) => ({
      id: item.id,
      requirementId: item.requirement_id || undefined,
      type: item.type as RequirementType,
      storageUrl: item.storage_url,
      fileKey: item.file_key,
      latitude: item.latitude !== null ? Number(item.latitude) : undefined,
      longitude: item.longitude !== null ? Number(item.longitude) : undefined,
      capturedAt: item.captured_at || undefined,
      uploadedAt: item.uploaded_at || undefined,
      metadata: item.metadata || undefined,
    })),
    decisions: decisions.rows.map((decision) => ({
      id: decision.id,
      officerId: decision.officer_id || undefined,
      decision: decision.decision,
      notes: decision.notes || undefined,
      attachments: decision.attachments || [],
      decidedAt: decision.decided_at,
    })),
  };
};

interface CreateVerificationPayload {
  loanId: string;
  initiatedBy?: string;
  dueDate?: string;
  requirements?: RequirementInput[];
}

export const createVerificationRequest = async (payload: CreateVerificationPayload) => {
  const client = await getClient();
  try {
    await client.query('BEGIN');
    const loanCheck = await client.query('SELECT id FROM loan_applications WHERE id = $1 LIMIT 1', [payload.loanId]);
    if (loanCheck.rowCount === 0) {
      throw new AppError('Loan not found', 404);
    }
    const verificationId = uuidv4();
    const insertResult = await client.query(
      `INSERT INTO verification_requests (id, loan_id, initiated_by, status, current_tier, thresholds_ref, due_date)
       VALUES ($1, $2, $3, 'pending', NULL, NULL, $4)
       RETURNING id, loan_id, status, due_date, created_at`,
      [verificationId, payload.loanId, payload.initiatedBy || null, payload.dueDate || null],
    );

    if (payload.requirements?.length) {
      // sequential insert keeps logic simple for now
      for (let index = 0; index < payload.requirements.length; index += 1) {
        const requirement = payload.requirements[index];
        await client.query(
          `INSERT INTO verification_requirements (id, verification_id, label, type, required, instructions, status, sort_order)
           VALUES ($1, $2, $3, $4, $5, $6, 'not_started', $7)`,
          [
            uuidv4(),
            verificationId,
            requirement.label,
            requirement.type,
            requirement.required ?? true,
            requirement.instructions || null,
            requirement.sortOrder ?? index,
          ],
        );
      }
    }

    await client.query('COMMIT');
    return insertResult.rows[0];
  } catch (error) {
    await client.query('ROLLBACK');
    throw error;
  } finally {
    client.release();
  }
};
