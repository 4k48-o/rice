# PR 代码审查检查清单

本文档用于在 Pull Request 中检查前端代码是否符合开发规范。

## 快速检查清单

在审查 PR 时，请确保以下所有项都符合规范：

### ✅ 1. 页面骨架（Skeleton）

- [ ] **列表页面**：首次加载时显示 Skeleton
- [ ] **条件判断**：只在 `loading && data.length === 0` 时显示 Skeleton
- [ ] **已有数据**：数据加载中但已有数据时，使用 Table/Tree 的 `loading` 属性

**检查代码模式**：
```tsx
// ✅ 正确
{loading && data.length === 0 ? (
  <Skeleton active paragraph={{ rows: 10 }} />
) : (
  <Table dataSource={data} loading={loading} />
)}

// ❌ 错误 - 缺少 Skeleton
<Table dataSource={data} loading={loading} />

// ❌ 错误 - 条件判断错误
{loading ? <Skeleton /> : <Table />}
```

---

### ✅ 2. 数据加载状态（Loading）

- [ ] **异步操作**：所有异步操作都有 `loading` 状态
- [ ] **状态管理**：使用 `useState` 管理 loading 状态
- [ ] **错误处理**：使用 `try-finally` 确保 loading 状态正确重置
- [ ] **按钮状态**：操作按钮显示 `loading` 属性

**检查代码模式**：
```tsx
// ✅ 正确
const [loading, setLoading] = useState(false);

const loadData = async () => {
  setLoading(true);
  try {
    // 加载数据
  } finally {
    setLoading(false);
  }
};

<Button onClick={loadData} loading={loading}>加载</Button>

// ❌ 错误 - 缺少 finally
const loadData = async () => {
  setLoading(true);
  try {
    // 加载数据
  } catch (error) {
    setLoading(false); // 错误时可能不会重置
  }
};
```

---

### ✅ 3. 按钮防抖（Debounce）

- [ ] **保存按钮**：使用防抖，延迟 300ms
- [ ] **查询按钮**：使用防抖，延迟 500ms
- [ ] **刷新按钮**：使用防抖，延迟 300ms
- [ ] **使用 Hook**：使用 `useDebounce` Hook（不是 `debounce` 工具函数）

**检查代码模式**：
```tsx
// ✅ 正确 - 使用 useDebounce Hook
import { useDebounce } from '@/hooks/useDebounce';

const handleSubmit = async () => { /* ... */ };
const debouncedSubmit = useDebounce(handleSubmit, 300);

<Button onClick={debouncedSubmit} loading={submitting}>保存</Button>

// ❌ 错误 - 没有防抖
<Button onClick={handleSubmit}>保存</Button>

// ❌ 错误 - 使用旧的 debounce 工具函数
import { debounce } from '@/utils/debounce';
const handleSubmitDebounced = useRef(debounce(() => {}, 300)).current;
```

**需要防抖的按钮**：
- ✅ 保存/提交按钮
- ✅ 查询/搜索按钮
- ✅ 刷新按钮
- ❌ 删除按钮（通常不需要防抖）
- ❌ 编辑按钮（通常不需要防抖）

---

### ✅ 4. 表单校验（Form Validation）

- [ ] **必填字段**：所有必填字段都有 `required: true` 校验
- [ ] **使用 formRules**：使用 `formRules` 工具统一管理校验规则
- [ ] **错误提示**：错误提示信息清晰明确
- [ ] **国际化**：使用 i18n 处理错误信息

**检查代码模式**：
```tsx
// ✅ 正确 - 使用 formRules
import { formRules } from '@/utils/formRules';

<Form.Item
  name="email"
  label="邮箱"
  rules={[formRules.required('邮箱'), formRules.email]}
>
  <Input />
</Form.Item>

<Form.Item
  name="phone"
  label="手机号"
  rules={[formRules.phone]}
>
  <Input />
</Form.Item>

// ❌ 错误 - 内联规则（应该使用 formRules）
<Form.Item
  name="email"
  rules={[{ type: 'email', message: '请输入有效的邮箱地址' }]}
>
  <Input />
</Form.Item>

// ❌ 错误 - 缺少必填校验
<Form.Item name="username" label="用户名">
  <Input />
</Form.Item>
```

**常用校验规则**：
- `formRules.required('字段名')` - 必填
- `formRules.email` - 邮箱
- `formRules.phone` - 手机号
- `formRules.password` - 密码（严格）
- `formRules.simplePassword` - 密码（简单）
- `formRules.username` - 用户名

---

## 文件结构检查

### 导入顺序

- [ ] **React 相关**：`react`, `react-dom` 等
- [ ] **第三方库**：`antd`, `dayjs` 等
- [ ] **项目工具**：`@/hooks`, `@/utils`, `@/components` 等
- [ ] **类型定义**：`@/types` 等
- [ ] **相对路径**：`./Component` 等

**示例**：
```tsx
// ✅ 正确
import { useState, useEffect } from 'react';
import { Table, Button } from 'antd';
import { useTranslation } from 'react-i18next';
import { useDebounce } from '@/hooks/useDebounce';
import { formRules } from '@/utils/formRules';
import { User } from '@/types/user';
import UserForm from './UserForm';
```

---

## 代码质量检查

### TypeScript

- [ ] **类型定义**：所有 props、state 都有类型定义
- [ ] **避免 any**：尽量不使用 `any` 类型
- [ ] **类型导入**：使用 `import type` 导入类型

### 错误处理

- [ ] **try-catch**：所有异步操作都有错误处理
- [ ] **用户提示**：错误时显示友好的提示信息
- [ ] **日志记录**：重要错误记录到控制台（开发环境）

### 性能优化

- [ ] **useMemo**：复杂计算使用 `useMemo`
- [ ] **useCallback**：传递给子组件的函数使用 `useCallback`
- [ ] **避免重复渲染**：检查依赖项是否正确

---

## 审查流程

### 1. 快速扫描

- [ ] 检查是否有新的列表页面（需要 Skeleton）
- [ ] 检查是否有新的表单页面（需要校验和防抖）
- [ ] 检查是否有新的按钮（需要防抖）

### 2. 详细检查

- [ ] 检查 Skeleton 的条件判断是否正确
- [ ] 检查 loading 状态是否正确管理
- [ ] 检查防抖是否正确实现
- [ ] 检查表单校验是否完整

### 3. 代码质量

- [ ] 检查 TypeScript 类型定义
- [ ] 检查错误处理
- [ ] 检查性能优化

---

## 常见问题

### Q1: 什么时候需要 Skeleton？

**A**: 所有列表页面（Table、Tree、List）在首次加载时都需要 Skeleton。

### Q2: 什么时候需要防抖？

**A**: 所有会触发网络请求的按钮都需要防抖：
- 保存/提交按钮
- 查询/搜索按钮
- 刷新按钮

不需要防抖的按钮：
- 删除按钮（通常有确认对话框）
- 编辑按钮（打开表单）
- 导航按钮（路由跳转）

### Q3: 表单校验规则应该放在哪里？

**A**: 统一使用 `formRules` 工具，不要内联定义校验规则。

### Q4: 防抖时间如何选择？

**A**: 
- 保存/提交：300ms
- 查询/搜索：500ms
- 刷新：300ms

---

## 审查模板

在 PR 评论中使用以下模板：

```markdown
## 代码审查

### ✅ 符合规范
- [x] 页面骨架（Skeleton）
- [x] 数据加载状态（Loading）
- [x] 按钮防抖（Debounce）
- [x] 表单校验（Form Validation）

### ⚠️ 需要改进
- [ ] 第 XX 行：缺少 Skeleton
- [ ] 第 XX 行：防抖时间应该使用 300ms
- [ ] 第 XX 行：应该使用 formRules.email

### 📝 建议
- 可以考虑使用 useMemo 优化性能
- 错误处理可以更详细
```

---

## 相关文档

- [前端开发规范](./FRONTEND_DEVELOPMENT_GUIDE.md)
- [快速参考指南](./FRONTEND_QUICK_REFERENCE.md)
- [更新总结](./FRONTEND_UPDATE_SUMMARY.md)

