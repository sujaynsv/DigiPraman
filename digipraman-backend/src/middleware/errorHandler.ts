import { NextFunction, Request, Response } from 'express';
import { AppError } from '../utils/AppError';

export const errorHandler = (
  err: Error | AppError,
  _req: Request,
  res: Response,
  _next: NextFunction,
) => {
  const statusCode = err instanceof AppError ? err.statusCode : 500;
  const response = {
    message: err.message || 'Internal server error',
    ...(err instanceof AppError && err.details ? { details: err.details } : {}),
  };

  if (statusCode >= 500) {
    console.error('Unhandled error', err);
  }

  res.status(statusCode).json(response);
};
