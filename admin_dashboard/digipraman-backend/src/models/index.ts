import { Sequelize } from 'sequelize';
import { User } from './User';
import { LoanApplication } from './LoanApplication';
import { VerificationRequest } from './VerificationRequest';
import { EvidenceItem } from './EvidenceItem';
import { RiskAnalysis } from './RiskAnalysis';
import { Decision } from './Decision';
import { AuditEntry } from './AuditEntry';
import { Notification } from './Notification';

// Initialize Sequelize with PostgreSQL
const sequelize = new Sequelize(process.env.DATABASE_URL, {
  dialect: 'postgres',
  dialectOptions: {
    // PostGIS support
    extensions: ['postgis'],
  },
});

// Export models
const models = {
  User: User(sequelize),
  LoanApplication: LoanApplication(sequelize),
  VerificationRequest: VerificationRequest(sequelize),
  EvidenceItem: EvidenceItem(sequelize),
  RiskAnalysis: RiskAnalysis(sequelize),
  Decision: Decision(sequelize),
  AuditEntry: AuditEntry(sequelize),
  Notification: Notification(sequelize),
};

// Sync models with the database
const syncModels = async () => {
  await sequelize.sync();
};

export { sequelize, models, syncModels };