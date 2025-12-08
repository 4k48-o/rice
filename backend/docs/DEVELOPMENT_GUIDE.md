# 开发指南

本文档提供添加新功能或修改现有功能时的标准开发流程。

## 添加新字段的标准流程

### 场景：给 Department 添加新字段 `description`

#### 步骤 1: 数据库迁移
```bash
# 创建迁移文件
cd backend
alembic revision --autogenerate -m "add_description_to_departments"

# 检查生成的迁移文件
# 确认添加了 description 字段

# 执行迁移
alembic upgrade head
```

#### 步骤 2: 更新数据库模型
```python
# backend/app/models/department.py
class Department(BaseModel, TenantMixin):
    # ... 现有字段 ...
    description: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="部门描述"
    )
```

#### 步骤 3: 更新后端 Schema
```python
# backend/app/schemas/department.py

class DepartmentBase(BaseModel):
    # ... 现有字段 ...
    description: Optional[str] = Field(None, max_length=500, description="部门描述")

class DepartmentUpdate(BaseModel):
    # ... 现有字段 ...
    description: Optional[str] = Field(None, max_length=500, description="部门描述")
```

**⚠️ 重要**：
- 如果字段继承自 `BaseModel`（如 `remark`），确保在 Base Schema 中明确定义
- Update Schema 必须包含所有可更新字段

#### 步骤 4: 更新前端类型定义
```typescript
// frontend/src/types/department.ts
export interface Department {
  // ... 现有字段 ...
  description?: string;
}

export interface DepartmentCreate {
  // ... 现有字段 ...
  description?: string;
}

export interface DepartmentUpdate {
  // ... 现有字段 ...
  description?: string;
}
```

#### 步骤 5: 更新前端表单
```typescript
// frontend/src/pages/Department/DepartmentForm.tsx

// 1. 在表单初始化中添加字段
const formValues = {
  // ... 现有字段 ...
  description: department.description || '',
};

// 2. 在表单中添加输入框
<Form.Item name="description" label="部门描述">
  <Input.TextArea rows={3} />
</Form.Item>

// 3. 在提交时确保字段包含在映射中
const mappedValues = {
  // ... 现有字段 ...
  description: values.description,
};
```

#### 步骤 6: 运行检查脚本
```bash
# 检查 Schema 完整性
python scripts/check_schema_completeness.py
```

#### 步骤 7: 测试验证
```bash
# 后端测试
cd backend
pytest tests/test_api/test_department.py -v

# 前端测试（如果有）
cd frontend
npm test
```

#### 步骤 8: 手动测试
1. 启动后端服务
2. 启动前端服务
3. 创建/编辑部门，测试新字段是否正常工作
4. 验证数据是否正确保存和显示

## Code Review 检查清单

### 后端代码 Review

- [ ] 数据库迁移文件是否正确？
- [ ] 数据库模型是否添加了字段？
- [ ] Base Schema 是否包含新字段？
- [ ] Create Schema 是否包含新字段？
- [ ] Update Schema 是否包含新字段（如可更新）？
- [ ] Response Schema 是否包含新字段？
- [ ] 字段验证规则是否合适（长度、类型等）？
- [ ] 是否添加了相应的测试？

### 前端代码 Review

- [ ] TypeScript 类型定义是否更新？
- [ ] 表单字段名是否与后端 Schema 一致？
- [ ] 表单初始化是否正确设置字段值？
- [ ] 提交时是否正确映射字段？
- [ ] 列表/详情页是否显示新字段？
- [ ] 是否有必要的字段验证？

## 常见错误和预防

### 错误 1: Schema 缺少字段
**症状**：前端发送的数据后端接收不到

**预防**：
- 使用检查脚本验证
- Code Review 时对照数据库模型检查

### 错误 2: 字段名不一致
**症状**：数据无法正确映射

**预防**：
- 使用后端 Schema 字段名作为标准
- 避免前端字段映射逻辑

### 错误 3: Update Schema 不完整
**症状**：某些字段无法更新

**预防**：
- Update Schema 应包含所有 Base Schema 字段（Optional）
- 使用类型检查工具

## 工具和脚本

### Schema 完整性检查
```bash
python scripts/check_schema_completeness.py
```

### 数据库迁移
```bash
# 创建迁移
alembic revision --autogenerate -m "description"

# 执行迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

### 代码格式化
```bash
# 后端
cd backend
black app/
ruff check app/

# 前端
cd frontend
npm run format
npm run lint
```

## 相关文档

- [最佳实践](./BEST_PRACTICES.md)
- [API 设计文档](./API_DOCUMENTATION.md)
- [快速参考](./QUICK_REFERENCE.md)
- [ID 生成策略](./ID_GENERATION_STRATEGY.md)

