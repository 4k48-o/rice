# DepartmentSelect 部门选择组件

可复用的部门选择下拉框组件，使用 TreeSelect 实现树形结构展示，支持树形结构的部门数据。

## 特性

- ✅ 使用 TreeSelect 实现树形结构展示
- ✅ 支持展开/折叠节点
- ✅ 层级关系清晰直观
- ✅ 自动加载部门数据
- ✅ 支持搜索过滤
- ✅ 支持只显示启用状态的部门
- ✅ 支持排除指定部门
- ✅ 完整的 TypeScript 类型支持
- ✅ 国际化支持（中文、英文、日文）

## 基本使用

```tsx
import { DepartmentSelect } from '@/components/DepartmentSelect';
import { Form } from 'antd';

<Form.Item name="dept_id" label="部门">
  <DepartmentSelect />
</Form.Item>
```

## 完整示例

```tsx
import { DepartmentSelect } from '@/components/DepartmentSelect';
import { Form } from 'antd';

function MyForm() {
  const [form] = Form.useForm();
  
  return (
    <Form form={form}>
      <Form.Item name="dept_id" label="所属部门">
        <DepartmentSelect
          placeholder="请选择部门"
          onlyEnabled={true}
          showSearch={true}
          allowClear={true}
        />
      </Form.Item>
    </Form>
  );
}
```

## API

### DepartmentSelectProps

| 属性 | 说明 | 类型 | 默认值 |
|------|------|------|--------|
| value | 选中的部门ID | `number \| string` | - |
| onChange | 值变化回调 | `(value: number \| string \| undefined) => void` | - |
| disabled | 是否禁用 | `boolean` | `false` |
| placeholder | 占位符 | `string` | - |
| showSearch | 是否显示搜索框 | `boolean` | `true` |
| allowClear | 是否允许清空 | `boolean` | `true` |
| style | 样式 | `React.CSSProperties` | - |
| className | 类名 | `string` | - |
| loading | 是否加载中（外部控制） | `boolean` | - |
| onlyEnabled | 是否只显示启用状态的部门 | `boolean` | `false` |
| excludeIds | 排除的部门ID列表（不显示这些部门及其子部门） | `(number \| string)[]` | - |
| treeDefaultExpandAll | 是否默认展开所有节点 | `boolean` | `false` |
| showSearch | 是否显示搜索框 | `boolean` | `true` |
| filterTreeNode | 树节点过滤函数 | `(inputValue: string, node: any) => boolean` | - |
| treeLine | 是否显示连接线 | `boolean` | `false` |
| maxTagCount | 最大标签数量 | `number` | - |
| dropdownStyle | 下拉框样式（已弃用，请使用 styles.popup.root） | `React.CSSProperties` | - |
| styles | 下拉框样式（新 API） | `{ popup?: { root?: React.CSSProperties } }` | - |

## 使用场景

### 1. 用户管理 - 选择用户所属部门

```tsx
<Form.Item name="dept_id" label="部门">
  <DepartmentSelect
    placeholder="请选择部门"
    onlyEnabled={true}
  />
</Form.Item>
```

### 2. 部门管理 - 选择上级部门（排除自身）

```tsx
<Form.Item name="parent_id" label="上级部门">
  <DepartmentSelect
    placeholder="请选择上级部门"
    excludeIds={[currentDeptId]} // 排除当前部门及其子部门
    onlyEnabled={true}
  />
</Form.Item>
```

### 3. 角色管理 - 选择数据权限范围部门

```tsx
<Form.Item name="department_ids" label="数据权限部门">
  <DepartmentSelect
    mode="multiple" // 注意：当前版本不支持 multiple，需要扩展
    placeholder="请选择部门"
    onlyEnabled={true}
  />
</Form.Item>
```

## 树形结构显示

组件以树形结构展示部门层级关系：

- **树形节点**: 每个部门作为一个树节点
- **展开/折叠**: 支持点击展开或折叠子部门
- **层级缩进**: 自动显示层级缩进，关系清晰
- **节点显示**: 部门名称 + 部门编码（如果有）
- **完整路径显示**: 选择子部门时，显示完整路径（包含主部门），更直观

示例结构：
```
├─ 技术部 (TECH)
│  ├─ 开发组 (DEV)
│  │  ├─ 前端组 (FE)
│  │  └─ 后端组 (BE)
│  └─ 测试组 (QA)
└─ 产品部 (PROD)
```

### 完整路径显示示例

当选择子部门时，输入框会显示完整路径：

- 选择"技术部" → 显示：`技术部`
- 选择"开发组" → 显示：`技术部 / 开发组`
- 选择"前端组" → 显示：`技术部 / 开发组 / 前端组`

这样用户可以清楚地看到所选部门的完整层级关系。

## 搜索功能

组件支持搜索过滤，可以：
- 按部门名称搜索
- 按部门编码搜索
- 自动过滤匹配的节点并高亮显示
- 搜索时自动展开包含匹配项的父节点

## 注意事项

1. **ID 类型**: 组件支持 `number | string` 类型，自动处理雪花 ID
2. **数据加载**: 组件会自动加载部门树数据，无需手动调用 API
3. **性能优化**: 使用 `useMemo` 优化数据处理，避免不必要的重渲染
4. **国际化**: 组件文本支持多语言，需要在 `locales` 文件中配置

## 高级用法

### 默认展开所有节点

```tsx
<DepartmentSelect
  treeDefaultExpandAll={true}
  onlyEnabled={true}
/>
```

### 显示连接线

```tsx
<DepartmentSelect
  treeLine={true}
  onlyEnabled={true}
/>
```

### 自定义过滤逻辑

```tsx
<DepartmentSelect
  filterTreeNode={(inputValue, node) => {
    // 自定义过滤逻辑
    return node.title.includes(inputValue);
  }}
/>
```

## 未来扩展

- [ ] 支持多选模式（`mode="multiple"`）
- [ ] 支持自定义分组逻辑
- [ ] 支持虚拟滚动（大数据量优化）
- [ ] 支持异步加载子部门

