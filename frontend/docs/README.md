# 前端文档

## 📚 文档目录

### 开发规范
- **[FRONTEND_DEVELOPMENT_GUIDE.md](./FRONTEND_DEVELOPMENT_GUIDE.md)** - 完整的开发规范文档
- **[FRONTEND_QUICK_REFERENCE.md](./FRONTEND_QUICK_REFERENCE.md)** - 快速参考指南

### 代码审查
- **[PR_REVIEW_CHECKLIST.md](./PR_REVIEW_CHECKLIST.md)** - PR 审查检查清单
- **[CODE_REVIEW_GUIDE.md](./CODE_REVIEW_GUIDE.md)** - 代码审查指南

### 测试
- **[TESTING_GUIDE.md](./TESTING_GUIDE.md)** - 完整的测试指南
- **[TESTING_QUICK_START.md](./TESTING_QUICK_START.md)** - 测试快速开始

### 更新记录
- **[FRONTEND_UPDATE_SUMMARY.md](./FRONTEND_UPDATE_SUMMARY.md)** - 规范应用更新总结

## 🛠️ 工具和脚本

### 代码规范检查

使用自动化脚本检查代码是否符合规范：

```bash
# 检查单个文件
npm run check:standards src/pages/User/UserList.tsx

# 或直接使用 node
node scripts/check-code-standards.js src/pages/User/UserList.tsx
```

### PR 模板

提交 PR 时，请使用 [PR 模板](../.github/PULL_REQUEST_TEMPLATE.md)。

## 📋 快速检查清单

在提交 PR 前，请确保：

- [ ] 页面骨架（Skeleton）- 列表页面首次加载时显示 Skeleton
- [ ] 数据加载状态（Loading）- 所有异步操作都有 loading 状态
- [ ] 按钮防抖（Debounce）- 保存/查询/刷新按钮使用防抖
- [ ] 表单校验（Form Validation）- 使用 formRules 统一管理校验规则

## 🔗 相关资源

- [前端 README](../README.md)
- [项目根目录 README](../../README.md)

