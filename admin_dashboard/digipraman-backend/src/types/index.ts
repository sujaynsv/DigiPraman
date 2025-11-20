export type Role = 'beneficiary' | 'officer' | 'admin';
export type VerificationStatus =
    | 'pending'
    | 'submitted'
    | 'scored'
    | 'routed'
    | 'needs_more'
    | 'approved'
    | 'rejected'
    | 'video_pending'
    | 'video_done';

export type RequirementType = 'photo' | 'video' | 'doc';
export type RequirementStatus = 'not_started' | 'in_progress' | 'completed';
export type DecisionType = 'approve' | 'reject' | 'request_more' | 'video_required';

export interface User {
    id: string;
    orgId: string | null;
    role: Role;
    name: string;
    mobile: string;
    email?: string;
    locale: string;
    status: string;
    createdAt: string;
}

export interface RiskSnapshot {
    score: number;
    tier: string;
    flags?: string[];
    explanation?: unknown;
    recommendedAction?: string;
}

export interface VerificationSummary {
    id: string;
    loanId: string;
    loanRefNo: string;
    schemeId: string | null;
    status: VerificationStatus;
    currentTier?: string;
    dueDate?: string;
    createdAt: string;
    sanctionedAmount: number;
    purpose?: string;
    risk?: RiskSnapshot;
}

export interface RequirementItem {
    id: string;
    label: string;
    type: RequirementType;
    required: boolean;
    instructions?: string;
    status: RequirementStatus;
    sortOrder: number;
    createdAt: string;
}

export interface EvidenceItem {
    id: string;
    requirementId?: string;
    type: RequirementType;
    storageUrl: string;
    fileKey: string;
    latitude?: number;
    longitude?: number;
    capturedAt?: string;
    uploadedAt?: string;
    metadata?: unknown;
}

export interface DecisionRecord {
    id: string;
    officerId?: string;
    decision: DecisionType;
    notes?: string;
    attachments?: unknown;
    decidedAt: string;
}

export interface VerificationDetail extends VerificationSummary {
    orgId: string | null;
    beneficiaryId: string;
    initiatedBy?: string;
    thresholdsRef?: unknown;
    requirements: RequirementItem[];
    evidence: EvidenceItem[];
    decisions: DecisionRecord[];
}