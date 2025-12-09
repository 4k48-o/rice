/**
 * 认证相关的测试 Fixtures
 * 提供登录、登出等常用操作的辅助函数
 */

import { Page } from '@playwright/test';

/**
 * 登录到系统
 * @param page Playwright Page 对象
 * @param username 用户名，默认为 'admin'
 * @param password 密码，默认为 'admin123'
 */
export async function login(
  page: Page,
  username: string = 'admin',
  password: string = 'admin123'
): Promise<void> {
  await page.goto('/login');
  
  // 清除存储
  await page.evaluate(() => {
    localStorage.clear();
    sessionStorage.clear();
  });

  // 填写登录表单
  await page.fill('input[placeholder*="用户名"], input[placeholder*="Username"]', username);
  await page.fill('input[type="password"]', password);
  
  // 提交表单
  await page.click('button[type="submit"]');
  
  // 等待登录完成（检查是否跳转到非登录页面）
  await page.waitForURL(/^(?!.*\/login)/, { timeout: 10000 });
  
  // 等待页面加载完成
  await page.waitForLoadState('networkidle');
}

/**
 * 登出系统
 * @param page Playwright Page 对象
 */
export async function logout(page: Page): Promise<void> {
  // 查找并点击登出按钮（根据实际 UI 调整选择器）
  const logoutButton = page.locator('button:has-text("退出"), button:has-text("登出"), [aria-label*="logout"]').first();
  
  if (await logoutButton.isVisible().catch(() => false)) {
    await logoutButton.click();
    
    // 等待重定向到登录页
    await page.waitForURL(/.*\/login/, { timeout: 5000 });
  } else {
    // 如果找不到登出按钮，直接清除存储并跳转
    await page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
    });
    await page.goto('/login');
  }
}

/**
 * 检查是否已登录
 * @param page Playwright Page 对象
 * @returns 是否已登录
 */
export async function isLoggedIn(page: Page): Promise<boolean> {
  const currentUrl = page.url();
  return !currentUrl.includes('/login');
}

