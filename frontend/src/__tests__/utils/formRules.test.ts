import { describe, it, expect, vi, beforeEach } from 'vitest';
import { email, phone } from '@/utils/formRules';

describe('formRules', () => {
  beforeEach(() => {
    // 重置所有 mock
    vi.clearAllMocks();
  });

  describe('email', () => {
    it('should accept valid email', async () => {
      const rule = email[0];
      if (rule.validator) {
        await expect(rule.validator({}, 'test@example.com')).resolves.toBeUndefined();
      }
    });

    it('should reject invalid email format', async () => {
      const rule = email[0];
      if (rule.validator) {
        await expect(rule.validator({}, 'invalid-email')).rejects.toThrow();
      }
    });

    it('should allow empty email', async () => {
      const rule = email[0];
      if (rule.validator) {
        await expect(rule.validator({}, '')).resolves.toBeUndefined();
        await expect(rule.validator({}, null)).resolves.toBeUndefined();
      }
    });

    it('should reject email longer than 100 characters', async () => {
      const rule = email[0];
      if (rule.validator) {
        const longEmail = 'a'.repeat(90) + '@example.com';
        await expect(rule.validator({}, longEmail)).rejects.toThrow();
      }
    });
  });

  describe('phone', () => {
    it('should accept valid phone number', async () => {
      const rule = phone[0];
      if (rule.validator) {
        await expect(rule.validator({}, '13800138000')).resolves.toBeUndefined();
        await expect(rule.validator({}, '15900159000')).resolves.toBeUndefined();
      }
    });

    it('should reject invalid phone number format', async () => {
      const rule = phone[0];
      if (rule.validator) {
        // 不是 11 位
        await expect(rule.validator({}, '1234567890')).rejects.toThrow();
        // 不是以 1[3-9] 开头
        await expect(rule.validator({}, '12800128000')).rejects.toThrow();
        // 包含非数字字符
        await expect(rule.validator({}, '1380013800a')).rejects.toThrow();
      }
    });

    it('should allow empty phone', async () => {
      const rule = phone[0];
      if (rule.validator) {
        await expect(rule.validator({}, '')).resolves.toBeUndefined();
        await expect(rule.validator({}, null)).resolves.toBeUndefined();
      }
    });
  });
});

