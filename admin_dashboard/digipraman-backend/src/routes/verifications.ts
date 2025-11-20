import { Router } from 'express';
import { verificationController } from '../controllers';

const router = Router();

router.get('/my', verificationController.listMine);
router.get('/:id', verificationController.getDetail);
router.post('/', verificationController.create);

export default router;
