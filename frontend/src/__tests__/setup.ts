/**
 * Vitest 测试环境配置
 */
import { expect, afterEach, vi } from 'vitest';
import { cleanup } from '@testing-library/react';
import * as matchers from '@testing-library/jest-dom/matchers';

// 扩展 Vitest 的 expect 方法
expect.extend(matchers);

// 每个测试后清理
afterEach(() => {
  cleanup();
});

// Mock i18n
vi.mock('@/i18n', () => ({
  default: {
    t: (key: string, options?: any) => {
      // 简单的 mock 实现，返回 key 或格式化后的字符串
      if (options) {
        return `${key} ${JSON.stringify(options)}`;
      }
      return key;
    },
    changeLanguage: vi.fn(),
    language: 'zh',
  },
}));

// Mock Ant Design 的 ConfigProvider（如果需要）
vi.mock('antd', async () => {
  const actual = await vi.importActual('antd');
  return {
    ...actual,
    ConfigProvider: ({ children }: any) => children,
  };
});

