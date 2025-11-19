import { config as loadEnv } from 'dotenv';

loadEnv();

const dbConfig = {
  host: process.env.DB_HOST || 'localhost',
  port: Number(process.env.DB_PORT) || 5432,
  database: process.env.DB_NAME || 'digipraman',
  user: process.env.DB_USER || 'postgres',
  password: process.env.DB_PASSWORD || 'password',
  ssl: process.env.DB_SSL === 'true'
    ? { rejectUnauthorized: false }
    : undefined,
  application_name: 'digipraman-backend',
};

const appConfig = {
  port: Number(process.env.APP_PORT) || 3000,
  env: process.env.NODE_ENV || 'development',
  corsOrigin: process.env.CORS_ORIGIN || '*',
};

const jwtConfig = {
  secret: process.env.JWT_SECRET || 'dev-secret',
  expiresIn: process.env.JWT_EXPIRES_IN || '1h',
};

const defaultOrgId = process.env.DEFAULT_ORG_ID || null;

export { dbConfig, appConfig, jwtConfig, defaultOrgId };