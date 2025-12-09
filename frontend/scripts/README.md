# 前端脚本工具

## check-code-standards.js

前端代码规范检查脚本，用于检查代码是否符合开发规范。

### 功能

检查以下规范：
1. ✅ 页面骨架（Skeleton）
2. ✅ 数据加载状态（Loading）
3. ✅ 按钮防抖（Debounce）
4. ✅ 表单校验（Form Validation）

### 使用方法

```bash
# 检查单个文件
node scripts/check-code-standards.js src/pages/User/UserList.tsx

# 或在 package.json 中添加脚本
npm run check:standards src/pages/User/UserList.tsx
```

### 输出示例

```
📄 检查文件: UserList.tsx

❌ 发现 2 个问题：

1. [DEBOUNCE] UserList.tsx:315
   保存/查询/刷新按钮应该使用防抖处理

2. [VALIDATION] UserForm.tsx:106
   字段 username 应该有校验规则

📝 请参考文档修复这些问题：
   - frontend/docs/FRONTEND_DEVELOPMENT_GUIDE.md
   - frontend/docs/PR_REVIEW_CHECKLIST.md
```

### 集成到 CI/CD

可以在 CI/CD 流程中集成此脚本：

```yaml
# .github/workflows/check-standards.yml
name: Check Code Standards

on: [pull_request]

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Check code standards
        run: |
          node frontend/scripts/check-code-standards.js ${{ github.event.pull_request.head.ref }}
```

### 注意事项

- 脚本会检查常见的代码模式，但可能无法覆盖所有情况
- 建议结合人工审查使用
- 脚本主要用于快速检查，详细审查请参考 [PR_REVIEW_CHECKLIST.md](../docs/PR_REVIEW_CHECKLIST.md)

