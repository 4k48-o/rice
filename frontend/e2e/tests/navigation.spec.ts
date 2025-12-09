import { test, expect } from '@playwright/test';

/**
 * 导航功能 E2E 测试
 */

// 登录辅助函数
async function login(page: any, username: string = 'admin', password: string = 'admin123') {
  await page.goto('/login');
  await page.fill('input[placeholder*="用户名"], input[placeholder*="Username"]', username);
  await page.fill('input[type="password"]', password);
  await page.click('button[type="submit"]');
  await page.waitForURL(/^(?!.*\/login)/, { timeout: 10000 });
}

test.describe('导航功能', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
    });
    await login(page);
  });

  test('应该能够导航到用户管理页面', async ({ page }) => {
    await page.goto('/system/user');
    
    // 验证 URL
    await expect(page).toHaveURL(/.*\/system\/user/);
    
    // 验证页面内容加载
    await page.waitForSelector('body', { timeout: 5000 });
  });

  test('应该能够导航到部门管理页面', async ({ page }) => {
    await page.goto('/system/dept');
    
    // 验证 URL
    await expect(page).toHaveURL(/.*\/system\/dept/);
    
    // 验证页面内容加载
    await page.waitForSelector('body', { timeout: 5000 });
  });

  test('应该能够导航到角色管理页面', async ({ page }) => {
    await page.goto('/system/role');
    
    // 验证 URL
    await expect(page).toHaveURL(/.*\/system\/role/);
    
    // 验证页面内容加载
    await page.waitForSelector('body', { timeout: 5000 });
  });

  test('应该能够导航到菜单管理页面', async ({ page }) => {
    await page.goto('/system/menu');
    
    // 验证 URL
    await expect(page).toHaveURL(/.*\/system\/menu/);
    
    // 验证页面内容加载
    await page.waitForSelector('body', { timeout: 5000 });
  });

  test('应该能够通过侧边栏菜单导航', async ({ page }) => {
    await page.goto('/');
    
    // 等待侧边栏加载
    await page.waitForSelector('.ant-layout-sider, .ant-menu', { timeout: 10000 });

    // 查找菜单项（根据实际菜单结构调整选择器）
    const menuItems = page.locator('.ant-menu-item, .ant-menu-submenu-title');
    const menuCount = await menuItems.count();

    if (menuCount > 0) {
      // 点击第一个菜单项
      await menuItems.first().click();
      await page.waitForTimeout(1000);
    }
  });

  test('应该能够返回首页', async ({ page }) => {
    // 先导航到其他页面
    await page.goto('/system/user');
    await page.waitForTimeout(1000);

    // 导航到首页
    await page.goto('/');
    
    // 验证 URL
    await expect(page).toHaveURL(/\/$/);
  });

  test('访问不存在的路由应该重定向到首页', async ({ page }) => {
    await page.goto('/non-existent-page');
    
    // 应该重定向到首页
    await expect(page).toHaveURL(/\/$/);
  });
});

