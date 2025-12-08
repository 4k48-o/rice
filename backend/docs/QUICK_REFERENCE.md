# 快速参考指南

## 🚨 避免字段不一致问题的快速检查

### 添加新字段时的 5 步检查

```
1. ✅ 数据库模型中有字段
2. ✅ Base Schema 中有字段  
3. ✅ Update Schema 中有字段（如果是可更新的）
4. ✅ 前端类型定义中有字段
5. ✅ 前端表单字段名与后端一致
```

### 运行自动检查

```bash
# 检查 Schema 完整性
python scripts/check_schema_completeness.py
# 或使用简化版（不需要数据库连接）
python scripts/check_schema_simple.py
```

### 字段命名规则

| ❌ 错误示例 | ✅ 正确做法 |
|------------|-----------|
| 前端: `dept_code` <br> 后端: `code` | 统一使用: `code` |
| 前端: `dept_name` <br> 后端: `name` | 统一使用: `name` |
| 前端: `sort_order` <br> 后端: `sort` | 统一使用: `sort` |

**原则**：以**后端 Schema**字段名为准！

### 常见问题快速修复

#### 问题：字段保存不了
```bash
# 1. 检查 Schema 是否有字段
grep "remark" backend/app/schemas/department.py

# 2. 检查前端是否正确映射
grep "remark" frontend/src/pages/Department/DepartmentForm.tsx

# 3. 运行检查脚本
python scripts/check_schema_completeness.py
# 或使用简化版
python scripts/check_schema_simple.py
```

#### 问题：字段名不一致
- 方案1：修改前端使用后端字段名（推荐）
- 方案2：后端使用 Field alias 支持两种名称

## 📚 相关文档

- [最佳实践指南](./BEST_PRACTICES.md) - 详细的最佳实践
- [开发指南](./DEVELOPMENT_GUIDE.md) - 标准开发流程

