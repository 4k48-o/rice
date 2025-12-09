#!/usr/bin/env node

/**
 * 前端代码规范检查脚本
 * 
 * 检查代码是否符合前端开发规范：
 * 1. 页面骨架（Skeleton）
 * 2. 数据加载状态（Loading）
 * 3. 按钮防抖（Debounce）
 * 4. 表单校验（Form Validation）
 * 
 * 使用方法：
 *   node scripts/check-code-standards.js [文件路径]
 * 
 * 示例：
 *   node scripts/check-code-standards.js src/pages/User/UserList.tsx
 */

const fs = require('fs');
const path = require('path');

// 颜色输出
const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

// 检查结果
const issues = [];

function addIssue(file, line, type, message) {
  issues.push({ file, line, type, message });
}

// 检查文件
function checkFile(filePath) {
  if (!fs.existsSync(filePath)) {
    log(`❌ 文件不存在: ${filePath}`, 'red');
    return;
  }

  const content = fs.readFileSync(filePath, 'utf-8');
  const lines = content.split('\n');
  const fileName = path.basename(filePath);

  log(`\n📄 检查文件: ${fileName}`, 'blue');

  // 1. 检查 Skeleton
  checkSkeleton(filePath, content, lines);

  // 2. 检查 Loading 状态
  checkLoading(filePath, content, lines);

  // 3. 检查防抖
  checkDebounce(filePath, content, lines);

  // 4. 检查表单校验
  checkFormValidation(filePath, content, lines);
}

// 检查 Skeleton
function checkSkeleton(filePath, content, lines) {
  // 检查是否是列表页面
  const isListPage = path.basename(filePath).includes('List') || 
                     content.includes('<Table') || 
                     content.includes('<Tree') ||
                     content.includes('dataSource');

  if (!isListPage) {
    return; // 不是列表页面，跳过
  }

  // 检查是否有 Skeleton
  const hasSkeleton = content.includes('Skeleton') || content.includes('skeleton');
  
  if (!hasSkeleton) {
    // 查找 Table 或 Tree 组件
    const tableLine = lines.findIndex(line => line.includes('<Table') || line.includes('<Tree'));
    if (tableLine !== -1) {
      addIssue(filePath, tableLine + 1, 'skeleton', '列表页面应该使用 Skeleton 骨架屏');
    }
  } else {
    // 检查 Skeleton 的条件判断
    const skeletonPattern = /loading.*data.*length.*===.*0|loading.*\&\&.*length.*===.*0/;
    if (!skeletonPattern.test(content)) {
      const skeletonLine = lines.findIndex(line => line.includes('Skeleton'));
      if (skeletonLine !== -1) {
        addIssue(filePath, skeletonLine + 1, 'skeleton', 'Skeleton 应该只在 loading && data.length === 0 时显示');
      }
    }
  }
}

// 检查 Loading 状态
function checkLoading(filePath, content, lines) {
  // 检查异步函数
  const asyncFunctions = content.match(/const\s+\w+\s*=\s*async\s*\([^)]*\)\s*=>/g) || [];
  const asyncFunctionNames = content.match(/async\s+function\s+(\w+)/g) || [];

  asyncFunctions.forEach((func, index) => {
    const funcName = func.match(/const\s+(\w+)/)?.[1];
    if (funcName) {
      // 检查是否有 loading 状态管理
      const hasLoadingState = content.includes(`setLoading(true)`) || 
                             content.includes(`loading`) ||
                             content.includes(`set${funcName.charAt(0).toUpperCase() + funcName.slice(1)}Loading`);
      
      if (!hasLoadingState) {
        const funcLine = lines.findIndex(line => line.includes(func));
        if (funcLine !== -1) {
          addIssue(filePath, funcLine + 1, 'loading', `异步函数 ${funcName} 应该有 loading 状态管理`);
        }
      }

      // 检查是否有 try-finally
      const funcContent = extractFunctionContent(content, funcName);
      if (funcContent && !funcContent.includes('finally')) {
        const funcLine = lines.findIndex(line => line.includes(func));
        if (funcLine !== -1) {
          addIssue(filePath, funcLine + 1, 'loading', `异步函数 ${funcName} 应该使用 try-finally 确保 loading 状态正确重置`);
        }
      }
    }
  });
}

// 检查防抖
function checkDebounce(filePath, content, lines) {
  // 检查按钮点击事件
  const buttonPattern = /onClick\s*=\s*\{([^}]+)\}/g;
  let match;

  while ((match = buttonPattern.exec(content)) !== null) {
    const onClickValue = match[1].trim();
    const buttonLine = content.substring(0, match.index).split('\n').length;

    // 检查是否是保存、查询、刷新按钮
    const isActionButton = /保存|提交|查询|搜索|刷新|submit|save|search|refresh|load/i.test(
      lines[buttonLine - 1] || ''
    );

    if (isActionButton) {
      // 检查是否使用防抖
      const hasDebounce = onClickValue.includes('debounce') || 
                         onClickValue.includes('useDebounce') ||
                         onClickValue.includes('Debounced');

      if (!hasDebounce) {
        addIssue(filePath, buttonLine, 'debounce', '保存/查询/刷新按钮应该使用防抖处理');
      } else {
        // 检查是否使用 useDebounce Hook
        if (onClickValue.includes('debounce') && !onClickValue.includes('useDebounce')) {
          addIssue(filePath, buttonLine, 'debounce', '应该使用 useDebounce Hook 而不是 debounce 工具函数');
        }
      }
    }
  }
}

// 检查表单校验
function checkFormValidation(filePath, content, lines) {
  // 检查是否是表单页面
  const isFormPage = path.basename(filePath).includes('Form') || content.includes('<Form') || content.includes('Form.Item');

  if (!isFormPage) {
    return; // 不是表单页面，跳过
  }

  // 检查是否导入 formRules
  const hasFormRulesImport = content.includes('formRules') || content.includes('@/utils/formRules');

  if (!hasFormRulesImport) {
    const formLine = lines.findIndex(line => line.includes('<Form'));
    if (formLine !== -1) {
      addIssue(filePath, formLine + 1, 'validation', '表单页面应该使用 formRules 统一管理校验规则');
    }
  }

  // 检查 Form.Item 是否有 rules
  const formItemPattern = /<Form\.Item[^>]*name\s*=\s*["'](\w+)["'][^>]*>/g;
  while ((match = formItemPattern.exec(content)) !== null) {
    const fieldName = match[1];
    const formItemContent = match[0];
    
    // 检查是否是必填字段（根据字段名判断）
    const requiredFields = ['username', 'password', 'email', 'phone', 'name', 'code'];
    if (requiredFields.includes(fieldName)) {
      if (!formItemContent.includes('rules') && !formItemContent.includes('required')) {
        const itemLine = content.substring(0, match.index).split('\n').length;
        addIssue(filePath, itemLine, 'validation', `字段 ${fieldName} 应该有校验规则`);
      }
    }
  }
}

// 提取函数内容（简化版）
function extractFunctionContent(content, funcName) {
  const funcPattern = new RegExp(`(const\\s+${funcName}\\s*=\\s*async[\\s\\S]*?\\})`, 'g');
  const match = funcPattern.exec(content);
  return match ? match[1] : null;
}

// 主函数
function main() {
  const args = process.argv.slice(2);
  
  if (args.length === 0) {
    log('使用方法: node scripts/check-code-standards.js [文件路径]', 'yellow');
    log('示例: node scripts/check-code-standards.js src/pages/User/UserList.tsx', 'yellow');
    process.exit(1);
  }

  const filePath = args[0];
  const fullPath = path.resolve(process.cwd(), filePath);

  checkFile(fullPath);

  // 输出结果
  if (issues.length === 0) {
    log('\n✅ 代码检查通过，符合规范！', 'green');
    process.exit(0);
  } else {
    log(`\n❌ 发现 ${issues.length} 个问题：`, 'red');
    
    issues.forEach((issue, index) => {
      log(`\n${index + 1}. [${issue.type.toUpperCase()}] ${path.basename(issue.file)}:${issue.line}`, 'yellow');
      log(`   ${issue.message}`, 'red');
    });

    log('\n📝 请参考文档修复这些问题：', 'blue');
    log('   - frontend/docs/FRONTEND_DEVELOPMENT_GUIDE.md', 'blue');
    log('   - frontend/docs/PR_REVIEW_CHECKLIST.md', 'blue');
    
    process.exit(1);
  }
}

// 运行
if (require.main === module) {
  main();
}

module.exports = { checkFile };

