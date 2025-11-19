import { Request, Response, NextFunction } from 'express';
import jwt from 'jsonwebtoken';
import { otpService } from '../services/otpService';
import { findOrCreateBeneficiary } from '../services/userService';
import { jwtConfig } from '../config';
import { AppError } from '../utils/AppError';

class AuthController {
  requestOtp = async (req: Request, res: Response, next: NextFunction) => {
    try {
      const { mobile } = req.body;
      if (!mobile) {
        throw new AppError('mobile is required', 400);
      }
      const payload = await otpService.requestOtp(mobile);
      res.json({ txnId: payload.txnId, expiresAt: payload.expiresAt });
    } catch (error) {
      next(error);
    }
  };

  verifyOtp = async (req: Request, res: Response, next: NextFunction) => {
    try {
      const { txnId, otp } = req.body;
      if (!txnId || !otp) {
        throw new AppError('txnId and otp are required', 400);
      }

      const { mobile } = await otpService.verifyOtp(txnId, otp);
      const user = await findOrCreateBeneficiary(mobile);
      const token = jwt.sign({ sub: user.id, role: user.role }, jwtConfig.secret, {
        expiresIn: jwtConfig.expiresIn,
      });

      res.json({ jwt: token, user });
    } catch (error) {
      next(error);
    }
  };
}

export const authController = new AuthController();
