import { randomInt } from 'crypto';
import { v4 as uuidv4 } from 'uuid';
import { AppError } from '../utils/AppError';

interface OtpRecord {
  txnId: string;
  otp: string;
  mobile: string;
  expiresAt: number;
}

const OTP_TTL_MS = 5 * 60 * 1000;

class OtpService {
  private readonly store = new Map<string, OtpRecord>();

  async requestOtp(mobile: string) {
    const txnId = uuidv4();
    const otp = randomInt(100000, 999999).toString();
    const expiresAt = Date.now() + OTP_TTL_MS;

    this.store.set(txnId, {
      txnId,
      otp,
      mobile,
      expiresAt,
    });

    // TODO: Integrate with SMS/notification service. For now we log to server.
    console.info(`OTP for ${mobile}: ${otp}`);

    return { txnId, expiresAt };
  }

  async verifyOtp(txnId: string, otp: string) {
    const record = this.store.get(txnId);
    if (!record) {
      throw new AppError('Invalid or expired transaction id', 400);
    }

    if (Date.now() > record.expiresAt) {
      this.store.delete(txnId);
      throw new AppError('OTP expired', 400);
    }

    if (record.otp !== otp) {
      throw new AppError('Invalid OTP', 400);
    }

    this.store.delete(txnId);
    return { mobile: record.mobile };
  }
}

export const otpService = new OtpService();
