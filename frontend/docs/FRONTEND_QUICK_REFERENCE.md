# 前端开发快速参考

本文档提供前端开发规范的快速参考，详细说明请查看 [FRONTEND_DEVELOPMENT_GUIDE.md](./FRONTEND_DEVELOPMENT_GUIDE.md)。

## 快速检查清单

### ✅ 页面骨架（Skeleton）

```tsx
import { Skeleton } from 'antd';

{loading && data.length === 0 ? (
  <Skeleton active paragraph={{ rows: 10 }} />
) : (
  <Table dataSource={data} loading={loading} />
)}
```

### ✅ 数据加载状态

```tsx
const [loading, setLoading] = useState(false);

const loadData = async () => {
  setLoading(true);
  try {
    // 加载数据
  } finally {
    setLoading(false);
  }
};
```

### ✅ 按钮防抖

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

### ✅ 表单校验

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

## 常用校验规则

| 规则 | 用法 |
|------|------|
| 必填 | `formRules.required('字段名')` |
| 邮箱 | `formRules.email` |
| 手机号 | `formRules.phone` |
| 密码 | `formRules.password` |
| 简单密码 | `formRules.simplePassword` |
| URL | `formRules.url` |
| 用户名 | `formRules.username` |
| 确认密码 | `formRules.confirmPassword()` |
| 中文姓名 | `formRules.chineseName` |
| 身份证 | `formRules.idCard` |

## 防抖时间建议

- **保存/提交按钮**：300ms
- **查询/搜索按钮**：500ms
- **刷新按钮**：300ms

## 文件位置

- 开发规范：`frontend/docs/FRONTEND_DEVELOPMENT_GUIDE.md`
- 防抖 Hook：`frontend/src/hooks/useDebounce.ts`
- 表单校验规则：`frontend/src/utils/formRules.ts`
- 防抖工具函数：`frontend/src/utils/debounce.ts`

