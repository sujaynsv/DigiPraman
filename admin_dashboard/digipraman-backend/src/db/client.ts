import { Pool, PoolClient, QueryResult } from 'pg';
import { dbConfig } from '../config';

const pool = new Pool(dbConfig);

pool.on('error', (error) => {
  console.error('Unexpected PG pool error', error);
  process.exit(1);
});

export const initDb = async () => {
  const client = await pool.connect();
  try {
    await client.query('SELECT 1');
    console.info('✅ Database connection established');
  } finally {
    client.release();
  }
};

export const query = <T>(text: string, params?: Array<string | number | boolean | null>) =>
  pool.query<T>(text, params);

export const getClient = async (): Promise<PoolClient> => pool.connect();

export type DbQueryResult<T> = QueryResult<T>;
