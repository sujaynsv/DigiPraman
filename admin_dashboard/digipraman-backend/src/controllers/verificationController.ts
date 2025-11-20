import { Request, Response, NextFunction } from 'express';
import { AppError } from '../utils/AppError';
import {
  createVerificationRequest,
  getBeneficiaryVerifications,
  getVerificationDetail,
} from '../services/verificationService';

class VerificationController {
  listMine = async (req: Request, res: Response, next: NextFunction) => {
    try {
      const beneficiaryId = (req.query.beneficiaryId as string) || (req.headers['x-beneficiary-id'] as string);
      if (!beneficiaryId) {
        throw new AppError('beneficiaryId is required', 400);
      }
      const items = await getBeneficiaryVerifications(beneficiaryId);
      res.json(items);
    } catch (error) {
      next(error);
    }
  };

  getDetail = async (req: Request, res: Response, next: NextFunction) => {
    try {
      const verification = await getVerificationDetail(req.params.id);
      res.json(verification);
    } catch (error) {
      next(error);
    }
  };

  create = async (req: Request, res: Response, next: NextFunction) => {
    try {
      const { loanId, initiatedBy, dueDate, requirements } = req.body;
      if (!loanId) {
        throw new AppError('loanId is required', 400);
      }
      const created = await createVerificationRequest({ loanId, initiatedBy, dueDate, requirements });
      res.status(201).json(created);
    } catch (error) {
      next(error);
    }
  };
}

export const verificationController = new VerificationController();
