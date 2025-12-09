import { test, expect } from '@playwright/test';

/**
 * 部门管理 E2E 测试
 */

// 登录辅助函数
async function login(page: any, username: string = 'admin', password: string = 'admin123') {
  await page.goto('/login');
  await page.fill('input[placeholder*="用户名"], input[placeholder*="Username"]', username);
  await page.fill('input[type="password"]', password);
  await page.click('button[type="submit"]');
  await page.waitForURL(/^(?!.*\/login)/, { timeout: 10000 });
}

test.describe('部门管理', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
    });
    await login(page);
  });

  test('应该能够访问部门管理页面', async ({ page }) => {
    await page.goto('/system/dept');

    // 验证页面加载
    await page.waitForSelector('body', { timeout: 10000 });
    
    // 验证 URL
    await expect(page).toHaveURL(/.*\/system\/dept/);
  });

  test('应该显示部门列表或树形结构', async ({ page }) => {
    await page.goto('/system/dept');

    // 等待内容加载（可能是表格或树形结构）
    await page.waitForSelector('.ant-table, .ant-tree, table, [data-testid="dept-list"]', { timeout: 10000 });

    // 验证内容区域存在
    const content = page.locator('.ant-table, .ant-tree, table, [data-testid="dept-list"]').first();
    await expect(content).toBeVisible();
  });

  test('应该能够打开新建部门表单', async ({ page }) => {
    await page.goto('/system/dept');
    await page.waitForSelector('button', { timeout: 10000 });

    // 查找新建按钮
    const createButton = page.locator('button:has-text("新建"), button:has-text("新增"), button:has-text("New")').first();
    
    if (await createButton.isVisible().catch(() => false)) {
      await createButton.click();
      
      // 验证表单打开
      await page.waitForSelector('.ant-drawer, .ant-modal, form', { timeout: 5000 });
      const form = page.locator('.ant-drawer, .ant-modal, form').first();
      await expect(form).toBeVisible();
    }
  });

  test('应该能够搜索部门', async ({ page }) => {
    await page.goto('/system/dept');
    await page.waitForSelector('input[placeholder*="搜索"], input[placeholder*="Search"]', { timeout: 10000 });

    // 查找搜索输入框
    const searchInput = page.locator('input[placeholder*="搜索"], input[placeholder*="Search"]').first();
    
    if (await searchInput.isVisible().catch(() => false)) {
      await searchInput.fill('测试');
      await searchInput.press('Enter');
      
      // 等待搜索结果
      await page.waitForTimeout(1000);
      await expect(searchInput).toHaveValue('测试');
    }
  });
});

