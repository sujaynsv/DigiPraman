import { Router } from 'express';
import { authController } from '../controllers';

const router = Router();

router.post('/otp/request', authController.requestOtp);
router.post('/otp/verify', authController.verifyOtp);

export default router;
