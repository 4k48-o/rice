import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright E2E 测试配置
 * 
 * 运行测试：
 * - npm run test:e2e        # 运行所有测试
 * - npm run test:e2e:ui     # 运行测试并打开 UI
 * - npm run test:e2e:debug  # 调试模式
 */
export default defineConfig({
  testDir: './e2e/tests',
  
  // 并行执行
  fullyParallel: true,
  
  // CI 环境下禁止使用 .only
  forbidOnly: !!process.env.CI,
  
  // 失败重试次数
  retries: process.env.CI ? 2 : 0,
  
  // CI 环境下使用单 worker
  workers: process.env.CI ? 1 : undefined,
  
  // 报告器
  reporter: [
    ['html'],
    ['list'],
    ['json', { outputFile: 'test-results/results.json' }],
  ],
  
  // 共享配置
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    // 设置超时时间
    actionTimeout: 10000,
    navigationTimeout: 30000,
  },

  // 测试项目（不同浏览器）
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    // 可以根据需要添加更多浏览器
    // {
    //   name: 'firefox',
    //   use: { ...devices['Desktop Firefox'] },
    // },
    // {
    //   name: 'webkit',
    //   use: { ...devices['Desktop Safari'] },
    // },
  ],

  // 开发服务器配置
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120000,
  },
});

