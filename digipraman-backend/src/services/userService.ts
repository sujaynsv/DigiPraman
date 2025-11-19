import { v4 as uuidv4 } from 'uuid';
import { query } from '../db';
import { defaultOrgId } from '../config';
import { AppError } from '../utils/AppError';
import { User } from '../types';

interface DbUser {
  id: string;
  org_id: string | null;
  role: string;
  name: string;
  mobile: string;
  email: string | null;
  locale: string | null;
  status: string;
  created_at: string;
}

const mapDbUser = (row: DbUser): User => ({
  id: row.id,
  orgId: row.org_id,
  role: row.role as User['role'],
  name: row.name,
  mobile: row.mobile,
  email: row.email || undefined,
  locale: row.locale || 'en',
  status: row.status,
  createdAt: row.created_at,
});

export const findUserByMobile = async (mobile: string): Promise<User | null> => {
  const result = await query<DbUser>(
    'SELECT id, org_id, role, name, mobile, email, locale, status, created_at FROM users WHERE mobile = $1 LIMIT 1',
    [mobile],
  );
  if (result.rowCount === 0) {
    return null;
  }
  return mapDbUser(result.rows[0]);
};

export const createBeneficiary = async (mobile: string, name?: string): Promise<User> => {
  const displayName = name || `Beneficiary ${mobile.slice(-4)}`;
  const result = await query<DbUser>(
    `INSERT INTO users (id, org_id, role, name, mobile, locale, status)
     VALUES ($1, $2, 'beneficiary', $3, $4, 'en', 'active')
     RETURNING id, org_id, role, name, mobile, email, locale, status, created_at`,
    [uuidv4(), defaultOrgId, displayName, mobile],
  );
  return mapDbUser(result.rows[0]);
};

export const findOrCreateBeneficiary = async (mobile: string, name?: string) => {
  const existing = await findUserByMobile(mobile);
  if (existing) {
    return existing;
  }
  return createBeneficiary(mobile, name);
};

export const getUserById = async (id: string) => {
  const result = await query<DbUser>(
    'SELECT id, org_id, role, name, mobile, email, locale, status, created_at FROM users WHERE id = $1 LIMIT 1',
    [id],
  );
  if (result.rowCount === 0) {
    throw new AppError('User not found', 404);
  }
  return mapDbUser(result.rows[0]);
};
