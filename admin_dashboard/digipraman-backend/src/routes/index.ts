import { Router } from 'express';
import authRoutes from './auth';
import verificationRoutes from './verifications';
import healthRoutes from './health';

const router = Router();

router.use('/auth', authRoutes);
router.use('/verifications', verificationRoutes);
router.use('/health', healthRoutes);

export default router;