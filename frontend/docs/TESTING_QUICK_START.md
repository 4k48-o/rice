# 前端测试快速开始

## 安装依赖

```bash
cd frontend
npm install
```

## 运行测试

### 单元测试

```bash
# 运行所有单元测试（watch 模式）
npm run test

# 运行测试并打开 UI 界面
npm run test:ui

# 生成覆盖率报告
npm run test:coverage
```

### E2E 测试

```bash
# 安装 Playwright 浏览器（首次运行需要）
npx playwright install

# 运行所有 E2E 测试
npm run test:e2e

# 运行测试并打开 UI 界面
npm run test:e2e:ui

# 调试模式（逐步执行）
npm run test:e2e:debug
```

## 测试文件结构

```
frontend/
├── src/
│   └── __tests__/          # 单元测试
│       ├── setup.ts        # 测试环境配置
│       ├── components/     # 组件测试
│       ├── hooks/          # Hooks 测试
│       ├── utils/           # 工具函数测试
│       └── pages/           # 页面测试
├── e2e/                    # E2E 测试
│   └── tests/              # E2E 测试用例
└── vitest.config.ts        # Vitest 配置
```

## 编写测试

### 单元测试示例

创建 `src/__tests__/utils/yourUtil.test.ts`：

```typescript
import { describe, it, expect } from 'vitest';
import { yourFunction } from '@/utils/yourUtil';

describe('yourFunction', () => {
  it('should work correctly', () => {
    expect(yourFunction('input')).toBe('expected');
  });
});
```

### E2E 测试示例

创建 `e2e/tests/your-feature.spec.ts`：

```typescript
import { test, expect } from '@playwright/test';

test('should do something', async ({ page }) => {
  await page.goto('/');
  await expect(page.locator('h1')).toBeVisible();
});
```

## 更多信息

详细文档请查看：[TESTING_GUIDE.md](./TESTING_GUIDE.md)

