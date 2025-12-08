# ID 序列化处理指南

> **文档版本**: 1.0  
> **最后更新**: 2025-12-08  
> **问题**: JavaScript 无法安全处理超过 `Number.MAX_SAFE_INTEGER` (2^53 - 1) 的大整数

---

## 问题背景

### JavaScript 精度限制

JavaScript 的 `Number` 类型使用 IEEE 754 双精度浮点数，只能安全表示到 `2^53 - 1` (即 `9007199254740991`)。

**雪花算法生成的 ID** 是 64 位整数，可能超过这个范围，导致：
- ❌ 精度丢失
- ❌ ID 比较失败
- ❌ 数据查找错误

### 解决方案

**统一策略**：将超过安全范围的大整数 ID 转换为字符串传输。

---

## 后端处理

### 1. 统一工具函数

**文件**: `backend/app/utils/id_serializer.py`

```python
from app.utils.id_serializer import serialize_id, serialize_id_list

# 序列化单个 ID
id_str = serialize_id(9007199254740992)  # 返回 "9007199254740992"
id_int = serialize_id(123)  # 返回 123

# 序列化 ID 列表
ids = serialize_id_list([123, 9007199254740992])  # 返回 [123, "9007199254740992"]
```

### 2. Schema Mixin（推荐）

**文件**: `backend/app/schemas/mixins.py`

所有 Response Schema 继承 `IDSerializerMixin`，自动处理 ID 序列化：

```python
from app.schemas.mixins import IDSerializerMixin

class UserResponse(UserBase, IDSerializerMixin):
    """User response schema."""
    id: int
    # ID 序列化自动处理，无需手动编写
```

**自动处理的字段**:
- `id`, `tenant_id`, `user_id`, `dept_id`, `role_id`
- `permission_id`, `department_id`, `parent_id`, `leader_id`
- `created_by`, `updated_by`, `deleted_by`
- `role_ids`, `permission_ids`, `department_ids` (列表)

### 3. JSON 编码器

**文件**: `backend/app/main.py`

全局 JSON 编码器自动处理大整数：

```python
class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, int) and abs(obj) > 9007199254740991:
            return str(obj)
        return super().default(obj)
```

### 4. API 路由处理

API 路由接收字符串 ID，转换为 int：

```python
@router.get("/{user_id}")
async def get_user(
    user_id: str,  # 接收字符串
    ...
):
    # 转换为 int (BigInteger)
    user_id_int = int(user_id)
    user = await user_service.get_by_id(db, user_id_int)
    ...
```

---

## 前端处理

### 1. 统一工具函数

**文件**: `frontend/src/utils/id.ts`

```typescript
import { toIdString, extractId, compareIds } from '@/utils/id';

// 转换为字符串（用于 API 调用）
const userId = toIdString(123);  // "123"
const userId2 = toIdString(9007199254740992);  // "9007199254740992"

// 从对象提取 ID
const id = extractId(user);  // 自动转换为字符串

// 比较 ID
if (compareIds(id1, id2)) {
  // 相等
}
```

### 2. TypeScript 类型定义

所有 ID 字段使用 `number | string` 类型：

```typescript
export interface User {
  id: number | string;  // 支持字符串类型
  dept_id?: number | string;
  role_ids?: (number | string)[];
}
```

### 3. API 调用

API 函数统一使用 `toIdString()` 转换：

```typescript
// ❌ 错误做法
await getUserDetail(user.id);

// ✅ 正确做法
await getUserDetail(toIdString(user.id));
```

### 4. 组件中使用

```typescript
import { toIdString, extractId } from '@/utils/id';

// 删除操作
const handleDelete = async (record: User) => {
  await deleteUser(toIdString(record.id));
};

// 编辑操作
const handleEdit = (record: User) => {
  const userId = extractId(record);
  // ...
};
```

---

## 最佳实践

### ✅ 推荐做法

1. **后端 Schema**: 继承 `IDSerializerMixin`，自动处理
2. **前端 API**: 使用 `toIdString()` 统一转换
3. **类型定义**: 使用 `number | string` 类型
4. **比较操作**: 使用 `compareIds()` 函数

### ❌ 避免做法

1. ❌ 直接使用 `Number(id)` 转换大整数
2. ❌ 在组件中手动调用 `String(id)`（应使用工具函数）
3. ❌ 假设 ID 始终是 number 类型
4. ❌ 使用 `===` 直接比较可能为字符串的 ID

---

## 代码示例

### 后端示例

```python
# ✅ 使用 Mixin（推荐）
from app.schemas.mixins import IDSerializerMixin

class UserResponse(UserBase, IDSerializerMixin):
    id: int
    # 自动序列化，无需手动处理

# ✅ 手动序列化（特殊情况）
from app.utils.id_serializer import serialize_id

def custom_serialize(data):
    data['id'] = serialize_id(data['id'])
    return data
```

### 前端示例

```typescript
// ✅ 使用工具函数（推荐）
import { toIdString, extractId } from '@/utils/id';

// API 调用
const user = await getUserDetail(toIdString(record.id));

// 从对象提取
const id = extractId(record);

// ❌ 避免手动转换
const id = String(record.id);  // 不推荐
```

---

## 已更新的文件

### 后端
- ✅ `backend/app/utils/id_serializer.py` - 统一工具函数
- ✅ `backend/app/schemas/mixins.py` - Schema Mixin
- ✅ `backend/app/schemas/user.py` - 使用 Mixin
- ✅ `backend/app/schemas/department.py` - 使用 Mixin
- ✅ `backend/app/schemas/role.py` - 使用 Mixin
- ✅ `backend/app/schemas/menu.py` - 使用 Mixin
- ✅ `backend/app/schemas/permission.py` - 使用 Mixin
- ✅ `backend/app/main.py` - JSON 编码器

### 前端
- ✅ `frontend/src/utils/id.ts` - 统一工具函数
- ✅ `frontend/src/types/user.ts` - 类型定义（已支持）
- ✅ `frontend/src/types/department.ts` - 类型定义（已支持）

---

## 迁移指南

### 后端迁移

1. **更新 Schema**: 继承 `IDSerializerMixin`
2. **移除手动序列化**: 删除 `@field_serializer` 装饰器
3. **测试验证**: 确保大整数 ID 正确序列化为字符串

### 前端迁移

1. **导入工具函数**: `import { toIdString } from '@/utils/id'`
2. **更新 API 调用**: 使用 `toIdString(id)` 替代 `String(id)`
3. **更新比较操作**: 使用 `compareIds()` 替代 `===`

---

## 相关文档

- [ID 生成策略](./ID_GENERATION_STRATEGY.md)
- [数据库设计文档](./DATABASE_DESIGN.md)
- [最佳实践](./BEST_PRACTICES.md)

---

**文档结束**

