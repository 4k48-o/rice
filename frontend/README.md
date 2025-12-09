# 前端项目

## 开发规范

前端开发规范文档位于 `docs/` 目录：

- **[FRONTEND_DEVELOPMENT_GUIDE.md](./docs/FRONTEND_DEVELOPMENT_GUIDE.md)** - 完整的开发规范文档
- **[FRONTEND_QUICK_REFERENCE.md](./docs/FRONTEND_QUICK_REFERENCE.md)** - 快速参考指南

## 核心规范

### 1. 页面骨架（Skeleton）
所有列表页面必须使用 Skeleton 组件作为初始加载状态。

### 2. 数据加载状态
所有异步操作必须显示加载状态。

### 3. 按钮防抖
所有保存、查询、提交按钮必须使用防抖处理。

### 4. 表单校验
所有表单必须包含常规校验规则。

## 工具和组件

### Hooks

- `useDebounce` - 防抖 Hook
- `useAuth` - 认证 Hook
- `usePermission` - 权限 Hook

### 工具函数

- `formRules` - 表单校验规则工具
- `debounce` - 防抖工具函数

## 使用示例

### 防抖按钮

```tsx
import { useDebounce } from '@/hooks/useDebounce';

const handleSubmit = async () => {
  // 提交逻辑
};

const debouncedSubmit = useDebounce(handleSubmit, 300);

<Button onClick={debouncedSubmit} loading={submitting}>
  保存
</Button>
```

### 表单校验

```tsx
import { formRules } from '@/utils/formRules';

<Form.Item
  name="email"
  label="邮箱"
  rules={[formRules.required('邮箱'), formRules.email]}
>
  <Input />
</Form.Item>
```

### 页面骨架

```tsx
import { Skeleton } from 'antd';

{loading && data.length === 0 ? (
  <Skeleton active paragraph={{ rows: 10 }} />
) : (
  <Table dataSource={data} loading={loading} />
)}
```

## 目录结构

```
frontend/
├── docs/                    # 文档目录
│   ├── FRONTEND_DEVELOPMENT_GUIDE.md
│   └── FRONTEND_QUICK_REFERENCE.md
├── src/
│   ├── hooks/              # React Hooks
│   │   ├── useDebounce.ts
│   │   ├── useAuth.ts
│   │   └── index.ts
│   ├── utils/              # 工具函数
│   │   ├── formRules.ts
│   │   └── debounce.ts
│   └── ...
```

## 更多信息

详细的使用说明和示例请查看 [开发规范文档](./docs/FRONTEND_DEVELOPMENT_GUIDE.md)。
