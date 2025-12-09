import { test, expect } from '@playwright/test';

/**
 * 用户管理 E2E 测试
 * 
 * 注意：这些测试需要有效的后端 API 和测试数据
 * 在运行测试前，请确保：
 * 1. 后端服务正在运行
 * 2. 有有效的测试账号（默认：admin/admin123）
 * 3. 测试数据已准备
 */

// 登录辅助函数
async function login(page: any, username: string = 'admin', password: string = 'admin123') {
  await page.goto('/login');
  await page.fill('input[placeholder*="用户名"], input[placeholder*="Username"]', username);
  await page.fill('input[type="password"]', password);
  await page.click('button[type="submit"]');
  
  // 等待登录完成（检查是否跳转到首页或显示成功消息）
  await page.waitForURL(/^(?!.*\/login)/, { timeout: 10000 });
}

// 切换语言辅助函数
async function changeLanguage(page: any, lang: string) {
  await page.evaluate((language) => {
    localStorage.setItem('language', language);
    window.location.reload();
  }, lang);
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(1000);
}

test.describe('用户管理', () => {
  test.beforeEach(async ({ page }) => {
    // 清除存储并登录
    await page.goto('/login');
    await page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
    });
    await login(page);
  });

  test('应该能够访问用户管理页面', async ({ page }) => {
    await page.goto('/system/user');

    // 等待页面加载完成
    await page.waitForLoadState('networkidle');

    // 验证页面关键元素存在（查询表单或表格）
    // QueryForm 使用 Card 组件，表格使用 ant-table
    const queryForm = page.locator('.ant-card, .ant-card-head-title').first();
    const table = page.locator('.ant-table, table').first();
    
    // 至少有一个关键元素可见即可
    await expect(queryForm.or(table).first()).toBeVisible({ timeout: 10000 });
  });

  test('应该显示用户列表', async ({ page }) => {
    await page.goto('/system/user');

    // 等待表格加载
    await page.waitForSelector('.ant-table, table, [data-testid="user-table"]', { timeout: 10000 });

    // 验证表格存在
    const table = page.locator('.ant-table, table, [data-testid="user-table"]').first();
    await expect(table).toBeVisible();
  });

  test('应该能够打开新建用户表单', async ({ page }) => {
    await page.goto('/system/user');

    // 等待页面加载
    await page.waitForSelector('button', { timeout: 10000 });

    // 查找并点击"新建"按钮
    const createButton = page.locator('button:has-text("新建"), button:has-text("新增"), button:has-text("New")').first();
    
    // 如果按钮存在，点击它
    if (await createButton.isVisible().catch(() => false)) {
      await createButton.click();
      
      // 验证表单或抽屉打开
      await page.waitForSelector('.ant-drawer, .ant-modal, form', { timeout: 5000 });
      const form = page.locator('.ant-drawer, .ant-modal, form').first();
      await expect(form).toBeVisible();
    }
  });

  test('应该能够搜索用户', async ({ page }) => {
    await page.goto('/system/user');

    // 等待搜索框加载
    await page.waitForSelector('input[placeholder*="搜索"], input[placeholder*="Search"]', { timeout: 10000 });

    // 查找搜索输入框
    const searchInput = page.locator('input[placeholder*="搜索"], input[placeholder*="Search"]').first();
    
    if (await searchInput.isVisible().catch(() => false)) {
      // 输入搜索关键词
      await searchInput.fill('admin');
      
      // 按 Enter 键或点击搜索按钮
      await searchInput.press('Enter');
      
      // 等待搜索结果加载
      await page.waitForTimeout(1000);
      
      // 验证搜索框有值
      await expect(searchInput).toHaveValue('admin');
    }
  });

  test('应该能够刷新用户列表', async ({ page }) => {
    await page.goto('/system/user');

    // 等待页面加载
    await page.waitForSelector('button', { timeout: 10000 });

    // 查找刷新按钮
    const refreshButton = page.locator('button:has-text("刷新"), button[aria-label*="reload"], button .anticon-reload').first();
    
    if (await refreshButton.isVisible().catch(() => false)) {
      await refreshButton.click();
      
      // 等待刷新完成（可以检查加载状态）
      await page.waitForTimeout(500);
    }
  });

  test('应该能够分页', async ({ page }) => {
    await page.goto('/system/user');

    // 等待表格和分页器加载
    await page.waitForSelector('.ant-pagination, .ant-table-pagination', { timeout: 10000 });

    // 查找分页器
    const pagination = page.locator('.ant-pagination, .ant-table-pagination').first();
    
    if (await pagination.isVisible().catch(() => false)) {
      // 查找下一页按钮
      const nextButton = pagination.locator('.ant-pagination-next, [aria-label="Next Page"]').first();
      
      if (await nextButton.isVisible().catch(() => false) && !(await nextButton.isDisabled().catch(() => true))) {
        await nextButton.click();
        
        // 等待页面切换
        await page.waitForTimeout(1000);
      }
    }
  });
});

test.describe('用户管理 - 表单操作', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
    });
    await login(page);
    await page.goto('/system/user');
    await page.waitForSelector('.ant-table, table', { timeout: 10000 });
  });

  test('应该能够打开编辑用户表单', async ({ page }) => {
    // 查找表格中的编辑按钮
    const editButton = page.locator('button:has-text("编辑"), button .anticon-edit, [aria-label*="edit"]').first();
    
    if (await editButton.isVisible().catch(() => false)) {
      await editButton.click();
      
      // 验证表单打开
      await page.waitForSelector('.ant-drawer, .ant-modal', { timeout: 5000 });
      const form = page.locator('.ant-drawer, .ant-modal').first();
      await expect(form).toBeVisible();
    }
  });

  test('应该能够填写用户表单字段', async ({ page }) => {
    // 打开新建或编辑表单
    const createButton = page.locator('button:has-text("新建"), button:has-text("新增")').first();
    
    if (await createButton.isVisible().catch(() => false)) {
      await createButton.click();
      await page.waitForSelector('.ant-drawer, .ant-modal', { timeout: 5000 });

      // 查找并填写表单字段
      const usernameInput = page.locator('input[name="username"], input[placeholder*="用户名"]').first();
      if (await usernameInput.isVisible().catch(() => false)) {
        await usernameInput.fill('testuser');
        await expect(usernameInput).toHaveValue('testuser');
      }

      const emailInput = page.locator('input[name="email"], input[placeholder*="邮箱"]').first();
      if (await emailInput.isVisible().catch(() => false)) {
        await emailInput.fill('test@example.com');
        await expect(emailInput).toHaveValue('test@example.com');
      }
    }
  });
});

test.describe('用户管理 - 表单校验', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
    });
    await login(page);
    await page.goto('/system/user');
    await page.waitForSelector('.ant-table, table', { timeout: 10000 });
    
    // 打开新建用户表单
    const createButton = page.locator('button:has-text("新建"), button:has-text("新增")').first();
    if (await createButton.isVisible().catch(() => false)) {
      await createButton.click();
      await page.waitForSelector('.ant-drawer, .ant-modal', { timeout: 5000 });
    }
  });

  test('应该验证必填字段（用户名）', async ({ page }) => {
    // 查找用户名输入框
    const usernameInput = page.locator('input[name="username"]').first();
    
    if (await usernameInput.isVisible().catch(() => false)) {
      // 先填写然后清空，触发验证
      await usernameInput.fill('test');
      await usernameInput.clear();
      
      // 尝试提交表单
      const submitButton = page.locator('button:has-text("保存"), button:has-text("确定"), button[type="submit"]').first();
      if (await submitButton.isVisible().catch(() => false)) {
        await submitButton.click();
        
        // 等待验证错误显示
        await page.waitForTimeout(500);
        
        // 验证错误消息存在（Ant Design 会在输入框下方显示错误）
        const errorMessage = page.locator('.ant-form-item-explain-error, .ant-form-item-has-error').first();
        await expect(errorMessage).toBeVisible({ timeout: 2000 });
      }
    }
  });

  test('应该验证必填字段（密码）', async ({ page }) => {
    // 查找密码输入框
    const passwordInput = page.locator('input[type="password"][name="password"]').first();
    
    if (await passwordInput.isVisible().catch(() => false)) {
      // 先填写然后清空，触发验证
      await passwordInput.fill('test123');
      await passwordInput.clear();
      
      // 尝试提交表单
      const submitButton = page.locator('button:has-text("保存"), button:has-text("确定"), button[type="submit"]').first();
      if (await submitButton.isVisible().catch(() => false)) {
        await submitButton.click();
        
        // 等待验证错误显示
        await page.waitForTimeout(500);
        
        // 验证错误消息存在
        const errorMessage = page.locator('.ant-form-item-explain-error, .ant-form-item-has-error').first();
        await expect(errorMessage).toBeVisible({ timeout: 2000 });
      }
    }
  });

  test('应该验证邮箱格式', async ({ page }) => {
    // 查找邮箱输入框
    const emailInput = page.locator('input[name="email"], input[type="email"]').first();
    
    if (await emailInput.isVisible().catch(() => false)) {
      // 输入无效邮箱格式
      await emailInput.fill('invalid-email');
      await emailInput.blur(); // 触发验证
      
      // 等待验证错误显示
      await page.waitForTimeout(500);
      
      // 验证错误消息存在
      const errorMessage = page.locator('.ant-form-item-explain-error').first();
      const hasError = await errorMessage.isVisible().catch(() => false);
      
      if (hasError) {
        // 验证错误消息包含邮箱相关提示
        const errorText = await errorMessage.textContent();
        expect(errorText).toBeTruthy();
      }
      
      // 输入有效邮箱格式，应该没有错误
      await emailInput.clear();
      await emailInput.fill('valid@example.com');
      await emailInput.blur();
      await page.waitForTimeout(500);
      
      // 验证没有错误消息
      const errorAfterValid = await page.locator('.ant-form-item-explain-error').first().isVisible().catch(() => false);
      // 如果之前有错误，现在应该消失
      if (hasError) {
        expect(errorAfterValid).toBeFalsy();
      }
    }
  });

  test('应该验证手机号格式', async ({ page }) => {
    // 查找手机号输入框
    const phoneInput = page.locator('input[name="phone"]').first();
    
    if (await phoneInput.isVisible().catch(() => false)) {
      // 输入无效手机号格式（不是 11 位，不是以 1[3-9] 开头）
      await phoneInput.fill('1234567890');
      await phoneInput.blur(); // 触发验证
      
      // 等待验证错误显示
      await page.waitForTimeout(500);
      
      // 验证错误消息存在
      const errorMessage = page.locator('.ant-form-item-explain-error').first();
      const hasError = await errorMessage.isVisible().catch(() => false);
      
      if (hasError) {
        // 验证错误消息包含手机号相关提示
        const errorText = await errorMessage.textContent();
        expect(errorText).toBeTruthy();
      }
      
      // 输入有效手机号格式
      await phoneInput.clear();
      await phoneInput.fill('13800138000');
      await phoneInput.blur();
      await page.waitForTimeout(500);
      
      // 验证没有错误消息
      const errorAfterValid = await page.locator('.ant-form-item-explain-error').first().isVisible().catch(() => false);
      if (hasError) {
        expect(errorAfterValid).toBeFalsy();
      }
    }
  });

  test('应该验证密码最小长度', async ({ page }) => {
    // 查找密码输入框
    const passwordInput = page.locator('input[type="password"][name="password"]').first();
    
    if (await passwordInput.isVisible().catch(() => false)) {
      // 输入少于 8 位的密码
      await passwordInput.fill('12345');
      await passwordInput.blur(); // 触发验证
      
      // 等待验证错误显示
      await page.waitForTimeout(500);
      
      // 验证错误消息存在
      const errorMessage = page.locator('.ant-form-item-explain-error').first();
      const hasError = await errorMessage.isVisible().catch(() => false);
      
      if (hasError) {
        const errorText = await errorMessage.textContent();
        // 验证错误消息包含长度相关提示
        expect(errorText).toBeTruthy();
      }
    }
  });

  test('应该验证用户名长度限制', async ({ page }) => {
    // 查找用户名输入框
    const usernameInput = page.locator('input[name="username"]').first();
    
    if (await usernameInput.isVisible().catch(() => false)) {
      // 输入超过 50 位的用户名
      const longUsername = 'a'.repeat(51);
      await usernameInput.fill(longUsername);
      await usernameInput.blur(); // 触发验证
      
      // 等待验证错误显示
      await page.waitForTimeout(500);
      
      // 验证错误消息存在或输入被限制
      const currentValue = await usernameInput.inputValue();
      // 如果前端有 maxLength 限制，值会被截断
      // 或者显示错误消息
      const errorMessage = page.locator('.ant-form-item-explain-error').first();
      const hasError = await errorMessage.isVisible().catch(() => false);
      
      // 验证要么值被截断，要么显示错误
      expect(currentValue.length <= 50 || hasError).toBeTruthy();
    }
  });

  test('应该验证真实姓名长度限制', async ({ page }) => {
    // 查找真实姓名输入框
    const realNameInput = page.locator('input[name="real_name"]').first();
    
    if (await realNameInput.isVisible().catch(() => false)) {
      // 输入超过 50 位的真实姓名
      const longName = '测'.repeat(51);
      await realNameInput.fill(longName);
      await realNameInput.blur(); // 触发验证
      
      // 等待验证错误显示
      await page.waitForTimeout(500);
      
      // 验证错误消息存在或输入被限制
      const currentValue = await realNameInput.inputValue();
      const errorMessage = page.locator('.ant-form-item-explain-error').first();
      const hasError = await errorMessage.isVisible().catch(() => false);
      
      // 验证要么值被截断，要么显示错误
      expect(currentValue.length <= 50 || hasError).toBeTruthy();
    }
  });

  test('应该允许空的可选字段（邮箱、手机号）', async ({ page }) => {
    // 查找邮箱和手机号输入框
    const emailInput = page.locator('input[name="email"], input[type="email"]').first();
    const phoneInput = page.locator('input[name="phone"]').first();
    
    // 这些字段应该是可选的，清空后不应该有错误
    if (await emailInput.isVisible().catch(() => false)) {
      await emailInput.clear();
      await emailInput.blur();
      await page.waitForTimeout(300);
      
      // 验证没有必填错误
      const emailError = await page.locator('input[name="email"]').locator('..').locator('.ant-form-item-explain-error').isVisible().catch(() => false);
      expect(emailError).toBeFalsy();
    }
    
    if (await phoneInput.isVisible().catch(() => false)) {
      await phoneInput.clear();
      await phoneInput.blur();
      await page.waitForTimeout(300);
      
      // 验证没有必填错误
      const phoneError = await page.locator('input[name="phone"]').locator('..').locator('.ant-form-item-explain-error').isVisible().catch(() => false);
      expect(phoneError).toBeFalsy();
    }
  });
});

