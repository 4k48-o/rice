import { test, expect } from '@playwright/test';

/**
 * 示例 E2E 测试
 * 
 * 这是一个示例测试文件，展示如何编写 E2E 测试
 * 可以根据实际需求修改或删除
 * 
 * 注意：这个文件主要用于演示，实际测试请参考其他测试文件
 */

test.describe('示例测试', () => {
  test('应该能够访问登录页面', async ({ page }) => {
    await page.goto('/login');
    
    // 验证登录表单元素存在
    await expect(page.locator('input[placeholder*="用户名"], input[placeholder*="Username"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toBeVisible();
  });

  test('未登录时访问首页应该重定向到登录页', async ({ page }) => {
    // 清除存储
    await page.goto('/');
    await page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
    });
    
    // 尝试访问首页
    await page.goto('/');
    
    // 应该重定向到登录页
    await expect(page).toHaveURL(/.*\/login/);
  });
});

