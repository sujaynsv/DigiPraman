import { Router } from 'express';
import { query } from '../db';

const router = Router();

router.get('/', async (_req, res, next) => {
  try {
    const result = await query<{ now: string }>('SELECT NOW() as now');
    res.json({ status: 'ok', databaseTime: result.rows[0].now });
  } catch (error) {
    next(error);
  }
});

export default router;
