# 前端开发规范

本文档定义了前端开发的标准规范，确保代码质量和用户体验的一致性。

## 目录

1. [页面骨架（Skeleton）](#页面骨架)
2. [数据加载状态](#数据加载状态)
3. [按钮防抖](#按钮防抖)
4. [表单校验](#表单校验)

---

## 页面骨架（Skeleton）

### 规范要求

**所有列表页面必须使用 Skeleton 组件作为初始加载状态。**

### 使用场景

- 首次加载数据时（数据为空）
- 刷新数据时（如果当前数据为空）

### 实现方式

```tsx
import { Skeleton } from 'antd';

// 在列表区域使用
<Card>
  {loading && data.length === 0 ? (
    <Skeleton active paragraph={{ rows: 10 }} />
  ) : (
    <Table
      columns={columns}
      dataSource={data}
      loading={loading}
      // ... 其他配置
    />
  )}
</Card>
```

### 注意事项

- 只在数据为空时显示 Skeleton
- 数据加载中但已有数据时，使用 Table 的 `loading` 属性
- Skeleton 的行数应根据实际内容调整（通常 8-10 行）

---

## 数据加载状态

### 规范要求

**所有异步操作必须显示加载状态。**

### 使用场景

1. **列表数据加载**
   - 使用 `loading` state
   - Table 组件使用 `loading` 属性
   - 按钮使用 `loading` 属性

2. **表单提交**
   - 提交按钮显示 `loading` 状态
   - 提交过程中禁用表单

3. **单个操作**
   - 删除、编辑等操作按钮显示 `loading` 状态

### 实现方式

```tsx
// 列表加载
const [loading, setLoading] = useState(false);

const loadData = async () => {
  setLoading(true);
  try {
    // 加载数据
  } finally {
    setLoading(false);
  }
};

// 表单提交
const [submitting, setSubmitting] = useState(false);

const handleSubmit = async () => {
  setSubmitting(true);
  try {
    // 提交数据
  } finally {
    setSubmitting(false);
  }
};
```

### 注意事项

- 所有异步操作必须有 `try-finally` 确保 loading 状态正确重置
- 错误处理不应阻止 loading 状态重置

---

## 按钮防抖

### 规范要求

**所有保存、查询、提交按钮必须使用防抖处理。**

### 使用场景

- 保存按钮（Create/Update）
- 查询/搜索按钮
- 提交按钮
- 刷新按钮（可选，但推荐）

### 实现方式

#### 方式 1：使用 useDebounce Hook（推荐）

```tsx
import { useDebounce } from '@/hooks/useDebounce';

const handleSubmit = async () => {
  // 提交逻辑
};

const debouncedSubmit = useDebounce(handleSubmit, 300);
```

#### 方式 2：使用 debounce 工具函数

```tsx
import { debounce } from '@/utils/debounce';

const handleSubmitRef = useRef<() => Promise<void>>();

useEffect(() => {
  handleSubmitRef.current = async () => {
    // 提交逻辑
  };
}, [dependencies]);

const handleSubmitDebounced = useRef(
  debounce(() => {
    if (handleSubmitRef.current) {
      handleSubmitRef.current();
    }
  }, 300)
).current;
```

### 防抖时间

- **保存/提交按钮**：300ms
- **查询/搜索按钮**：500ms
- **刷新按钮**：300ms

### 注意事项

- 防抖期间按钮应显示 loading 状态
- 防抖期间应禁用按钮（通过 `disabled` 或 `loading` 属性）

---

## 表单校验

### 规范要求

**所有表单必须包含常规校验规则。**

### 必填字段校验

```tsx
<Form.Item
  name="username"
  label="用户名"
  rules={[
    { required: true, message: '请输入用户名' }
  ]}
>
  <Input />
</Form.Item>
```

### 常用校验规则

#### 1. 邮箱校验

```tsx
<Form.Item
  name="email"
  label="邮箱"
  rules={[
    { type: 'email', message: '请输入有效的邮箱地址' }
  ]}
>
  <Input />
</Form.Item>
```

#### 2. 密码校验

```tsx
<Form.Item
  name="password"
  label="密码"
  rules={[
    { required: true, message: '请输入密码' },
    { min: 8, message: '密码长度至少8位' },
    { max: 20, message: '密码长度不能超过20位' },
    { pattern: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/, message: '密码必须包含大小写字母和数字' }
  ]}
>
  <Input.Password />
</Form.Item>
```

#### 3. 手机号校验

```tsx
<Form.Item
  name="phone"
  label="手机号"
  rules={[
    { pattern: /^1[3-9]\d{9}$/, message: '请输入有效的手机号' }
  ]}
>
  <Input />
</Form.Item>
```

#### 4. 长度校验

```tsx
<Form.Item
  name="name"
  label="名称"
  rules={[
    { required: true, message: '请输入名称' },
    { min: 2, message: '名称长度至少2个字符' },
    { max: 50, message: '名称长度不能超过50个字符' }
  ]}
>
  <Input />
</Form.Item>
```

#### 5. 数字校验

```tsx
<Form.Item
  name="age"
  label="年龄"
  rules={[
    { type: 'number', min: 1, max: 150, message: '请输入有效的年龄（1-150）' }
  ]}
>
  <InputNumber />
</Form.Item>
```

#### 6. URL 校验

```tsx
<Form.Item
  name="url"
  label="网址"
  rules={[
    { type: 'url', message: '请输入有效的URL' }
  ]}
>
  <Input />
</Form.Item>
```

### 自定义校验

```tsx
<Form.Item
  name="confirmPassword"
  label="确认密码"
  dependencies={['password']}
  rules={[
    { required: true, message: '请确认密码' },
    ({ getFieldValue }) => ({
      validator(_, value) {
        if (!value || getFieldValue('password') === value) {
          return Promise.resolve();
        }
        return Promise.reject(new Error('两次输入的密码不一致'));
      },
    }),
  ]}
>
  <Input.Password />
</Form.Item>
```

### 使用校验工具函数（推荐）

```tsx
import { formRules } from '@/utils/formRules';

<Form.Item
  name="email"
  label="邮箱"
  rules={formRules.email}
>
  <Input />
</Form.Item>

<Form.Item
  name="phone"
  label="手机号"
  rules={formRules.phone}
>
  <Input />
</Form.Item>
```

### 注意事项

- 所有必填字段必须有 `required: true`
- 错误提示信息应清晰明确
- 使用国际化（i18n）处理错误信息
- 复杂校验使用自定义 validator

---

## 完整示例

### 列表页面示例

```tsx
import { useState, useEffect } from 'react';
import { Table, Card, Button, Skeleton, message } from 'antd';
import { useDebounce } from '@/hooks/useDebounce';

export default function ExampleList() {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState([]);
  const [page, setPage] = useState(1);

  const loadData = async () => {
    setLoading(true);
    try {
      // 加载数据
      const response = await fetchData({ page });
      setData(response.data);
    } catch (error) {
      message.error('加载失败');
    } finally {
      setLoading(false);
    }
  };

  // 防抖的刷新函数
  const debouncedRefresh = useDebounce(loadData, 300);

  useEffect(() => {
    loadData();
  }, [page]);

  return (
    <div>
      <Button onClick={debouncedRefresh} loading={loading}>
        刷新
      </Button>

      <Card>
        {loading && data.length === 0 ? (
          <Skeleton active paragraph={{ rows: 10 }} />
        ) : (
          <Table
            columns={columns}
            dataSource={data}
            loading={loading}
            rowKey="id"
          />
        )}
      </Card>
    </div>
  );
}
```

### 表单页面示例

```tsx
import { useState } from 'react';
import { Form, Input, Button, message } from 'antd';
import { useDebounce } from '@/hooks/useDebounce';
import { formRules } from '@/utils/formRules';

export default function ExampleForm({ visible, onCancel, onSuccess }) {
  const [form] = Form.useForm();
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async () => {
    if (submitting) return;

    try {
      const values = await form.validateFields();
      setSubmitting(true);
      
      // 提交数据
      await submitData(values);
      message.success('保存成功');
      onSuccess();
    } catch (error) {
      if (error.errorFields) {
        // 表单验证错误
        return;
      }
      message.error('保存失败');
    } finally {
      setSubmitting(false);
    }
  };

  // 防抖的提交函数
  const debouncedSubmit = useDebounce(handleSubmit, 300);

  return (
    <Form form={form} layout="vertical">
      <Form.Item
        name="name"
        label="名称"
        rules={formRules.required('名称')}
      >
        <Input />
      </Form.Item>

      <Form.Item
        name="email"
        label="邮箱"
        rules={formRules.email}
      >
        <Input />
      </Form.Item>

      <Form.Item>
        <Button
          type="primary"
          onClick={debouncedSubmit}
          loading={submitting}
        >
          保存
        </Button>
      </Form.Item>
    </Form>
  );
}
```

---

## 检查清单

在提交代码前，请确保：

- [ ] 列表页面有 Skeleton 骨架屏
- [ ] 所有异步操作有 loading 状态
- [ ] 保存/查询按钮有防抖处理
- [ ] 表单字段有适当的校验规则
- [ ] 错误提示信息清晰明确
- [ ] 使用国际化（i18n）处理文本

---

## 相关文件

- 防抖 Hook: `frontend/src/hooks/useDebounce.ts`
- 防抖工具: `frontend/src/utils/debounce.ts`
- 表单校验规则: `frontend/src/utils/formRules.ts`
- Skeleton 组件: 使用 Ant Design 的 `Skeleton` 组件

