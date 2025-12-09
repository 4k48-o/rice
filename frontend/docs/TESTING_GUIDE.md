# 前端自动化测试方案

## 测试策略

本项目采用**分层测试策略**：

1. **单元测试**：测试工具函数、Hooks、组件逻辑
2. **集成测试**：测试组件交互、表单验证
3. **E2E 测试**：测试完整用户流程

## 技术栈

- **Vitest**：快速、轻量的单元测试框架（与 Vite 完美集成）
- **React Testing Library**：React 组件测试工具
- **Playwright**：E2E 测试框架（支持多浏览器）

## 目录结构

```
frontend/
├── src/
│   ├── __tests__/          # 测试文件目录
│   │   ├── components/     # 组件测试
│   │   ├── hooks/          # Hooks 测试
│   │   ├── utils/          # 工具函数测试
│   │   └── pages/          # 页面测试
│   └── ...
├── e2e/                    # E2E 测试目录
│   ├── tests/              # 测试用例
│   ├── fixtures/           # 测试数据
│   └── playwright.config.ts
├── vitest.config.ts        # Vitest 配置
└── package.json
```

## 安装依赖

```bash
# 单元测试依赖
npm install -D vitest @vitest/ui @testing-library/react @testing-library/jest-dom @testing-library/user-event jsdom

# E2E 测试依赖
npm install -D @playwright/test
```

## 配置 Vitest

创建 `vitest.config.ts`：

```typescript
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/__tests__/setup.ts',
    css: true,
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'src/__tests__/',
        '**/*.d.ts',
        '**/*.config.*',
        '**/mockData',
      ],
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
});
```

## 配置 Playwright

创建 `playwright.config.ts`：

```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e/tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});
```

## 测试示例

### 1. 工具函数测试

`src/__tests__/utils/formRules.test.ts`：

```typescript
import { describe, it, expect } from 'vitest';
import { email, phone, required } from '@/utils/formRules';

describe('formRules', () => {
  describe('email', () => {
    it('should accept valid email', async () => {
      const rule = email[0];
      if (rule.validator) {
        await expect(rule.validator({}, 'test@example.com')).resolves.toBeUndefined();
      }
    });

    it('should reject invalid email', async () => {
      const rule = email[0];
      if (rule.validator) {
        await expect(rule.validator({}, 'invalid-email')).rejects.toThrow();
      }
    });

    it('should allow empty email', async () => {
      const rule = email[0];
      if (rule.validator) {
        await expect(rule.validator({}, '')).resolves.toBeUndefined();
      }
    });
  });

  describe('phone', () => {
    it('should accept valid phone number', async () => {
      const rule = phone[0];
      if (rule.validator) {
        await expect(rule.validator({}, '13800138000')).resolves.toBeUndefined();
      }
    });

    it('should reject invalid phone number', async () => {
      const rule = phone[0];
      if (rule.validator) {
        await expect(rule.validator({}, '1234567890')).rejects.toThrow();
      }
    });
  });
});
```

### 2. 组件测试

`src/__tests__/components/SearchInput.test.tsx`：

```typescript
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import SearchInput from '@/components/SearchInput/SearchInput';

describe('SearchInput', () => {
  it('should render with placeholder', () => {
    render(<SearchInput placeholder="搜索..." />);
    expect(screen.getByPlaceholderText('搜索...')).toBeInTheDocument();
  });

  it('should call onSearch when button clicked', () => {
    const handleSearch = vi.fn();
    render(<SearchInput value="test" onSearch={handleSearch} />);
    
    const button = screen.getByRole('button');
    fireEvent.click(button);
    
    expect(handleSearch).toHaveBeenCalledWith('test');
  });

  it('should call onSearch when Enter pressed', () => {
    const handleSearch = vi.fn();
    render(<SearchInput value="test" onSearch={handleSearch} />);
    
    const input = screen.getByRole('textbox');
    fireEvent.keyDown(input, { key: 'Enter', code: 'Enter' });
    
    expect(handleSearch).toHaveBeenCalledWith('test');
  });
});
```

### 3. Hooks 测试

`src/__tests__/hooks/useDebounce.test.ts`：

```typescript
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { useDebounce } from '@/hooks/useDebounce';

describe('useDebounce', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('should debounce value changes', async () => {
    const { result, rerender } = renderHook(
      ({ value }) => useDebounce(value, 300),
      { initialProps: { value: 'initial' } }
    );

    expect(result.current).toBe('initial');

    rerender({ value: 'updated' });
    expect(result.current).toBe('initial'); // 还没更新

    vi.advanceTimersByTime(300);
    await waitFor(() => {
      expect(result.current).toBe('updated');
    });
  });
});
```

### 4. E2E 测试

`e2e/tests/user-management.spec.ts`：

```typescript
import { test, expect } from '@playwright/test';

test.describe('用户管理', () => {
  test.beforeEach(async ({ page }) => {
    // 登录
    await page.goto('/login');
    await page.fill('input[name="username"]', 'admin');
    await page.fill('input[name="password"]', 'admin123');
    await page.click('button[type="submit"]');
    await page.waitForURL('/');
  });

  test('应该能够创建新用户', async ({ page }) => {
    await page.goto('/user');
    
    // 点击新建按钮
    await page.click('button:has-text("新建")');
    
    // 填写表单
    await page.fill('input[name="username"]', 'testuser');
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="phone"]', '13800138000');
    
    // 提交
    await page.click('button:has-text("确定")');
    
    // 验证成功消息
    await expect(page.locator('.ant-message-success')).toBeVisible();
  });

  test('应该能够搜索用户', async ({ page }) => {
    await page.goto('/user');
    
    // 输入搜索关键词
    await page.fill('input[placeholder*="搜索"]', 'admin');
    await page.press('input[placeholder*="搜索"]', 'Enter');
    
    // 验证搜索结果
    await expect(page.locator('.ant-table-row')).toContainText('admin');
  });
});
```

## 运行测试

在 `package.json` 中添加脚本：

```json
{
  "scripts": {
    "test": "vitest",
    "test:ui": "vitest --ui",
    "test:coverage": "vitest --coverage",
    "test:e2e": "playwright test",
    "test:e2e:ui": "playwright test --ui",
    "test:e2e:debug": "playwright test --debug"
  }
}
```

运行命令：

```bash
# 运行单元测试（watch 模式）
npm run test

# 运行单元测试（UI 模式）
npm run test:ui

# 生成覆盖率报告
npm run test:coverage

# 运行 E2E 测试
npm run test:e2e

# 运行 E2E 测试（UI 模式）
npm run test:e2e:ui
```

## 测试最佳实践

### 1. 测试命名
- 使用描述性的测试名称
- 遵循 `should [expected behavior] when [condition]` 格式

### 2. 测试组织
- 使用 `describe` 块组织相关测试
- 每个测试只验证一个行为

### 3. 测试数据
- 使用 `fixtures` 管理测试数据
- 避免硬编码，使用常量

### 4. Mock 和 Stub
- Mock API 调用
- 使用 `vi.mock()` 模拟模块

### 5. 覆盖率目标
- 工具函数：> 80%
- 组件：> 60%
- 整体：> 70%

## CI/CD 集成

在 GitHub Actions 中运行测试：

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm ci
      - run: npm run test:coverage
      - run: npm run test:e2e
```

## 参考资源

- [Vitest 文档](https://vitest.dev/)
- [React Testing Library](https://testing-library.com/react)
- [Playwright 文档](https://playwright.dev/)

