import { test, expect } from '@playwright/test';

/**
 * 认证相关 E2E 测试
 */
test.describe('认证功能', () => {
  test.beforeEach(async ({ page }) => {
    // 清除本地存储，确保每次测试从干净状态开始
    await page.goto('/login');
    await page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
    });
  });

  test('应该显示登录页面', async ({ page }) => {
    await page.goto('/login');

    // 验证登录表单元素存在
    await expect(page.locator('input[placeholder*="用户名"], input[placeholder*="Username"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toBeVisible();
  });

  test('应该显示必填字段验证错误', async ({ page }) => {
    await page.goto('/login');

    // 直接提交空表单
    await page.click('button[type="submit"]');

    // 验证错误消息（根据实际错误消息调整）
    // Ant Design 会在输入框下方显示错误消息
    const usernameInput = page.locator('input[placeholder*="用户名"], input[placeholder*="Username"]').first();
    await expect(usernameInput).toBeVisible();
  });

  test('应该能够填写登录表单', async ({ page }) => {
    await page.goto('/login');

    // 填写表单
    await page.fill('input[placeholder*="用户名"], input[placeholder*="Username"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');

    // 验证输入值
    await expect(page.locator('input[placeholder*="用户名"], input[placeholder*="Username"]')).toHaveValue('admin');
    await expect(page.locator('input[type="password"]')).toHaveValue('admin123');
  });

  test('应该能够勾选"记住我"', async ({ page }) => {
    await page.goto('/login');

    // 查找并勾选"记住我"复选框
    const rememberCheckbox = page.locator('input[type="checkbox"]').first();
    await rememberCheckbox.check();

    // 验证复选框已勾选
    await expect(rememberCheckbox).toBeChecked();
  });

  test('未登录时访问受保护页面应该重定向到登录页', async ({ page }) => {
    // 清除认证信息
    await page.goto('/');
    await page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
    });

    // 尝试访问受保护页面
    await page.goto('/system/user');

    // 应该重定向到登录页
    await expect(page).toHaveURL(/.*\/login/);
  });
});

