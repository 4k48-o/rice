# 部门数据缓存方案

> **文档版本**: 1.0  
> **最后更新**: 2025-12-08  
> **状态**: 已实施

---

## 概述

部门数据是系统中使用非常频繁的数据，为了提升系统性能，我们为部门数据实现了Redis缓存机制。本文档详细说明了缓存的设计、实现和使用方法。

---

## 缓存策略

### 缓存键设计

| 缓存键 | 说明 | 示例 |
|--------|------|------|
| `dept:list:{tenant_id}` | 部门列表（按租户隔离） | `dept:list:1` |
| `dept:tree:{tenant_id}` | 部门树结构（按租户隔离，预留） | `dept:tree:1` |
| `dept:detail:{dept_id}` | 单个部门详情 | `dept:detail:1234567890123456789` |

**重要**: 所有缓存键中的ID（`tenant_id`、`dept_id`）都会自动转换为字符串类型，确保前端可以正常使用BigInt类型的ID，避免JavaScript精度丢失问题。

### 缓存数据格式

- **序列化方式**: JSON序列化
- **过期策略**: 不设置过期时间，采用"写时清除"策略
- **数据一致性**: 数据变更时立即清除相关缓存，确保数据一致性

### 缓存更新时机

1. **创建部门**: 清除对应租户的 `list` 和 `tree` 缓存
2. **更新部门**: 清除对应租户的 `list`、`tree` 缓存，以及该部门的 `detail` 缓存
3. **删除部门**: 清除对应租户的 `list`、`tree` 缓存，以及该部门的 `detail` 缓存

---

## 实现细节

### 1. 缓存工具类

**文件**: `backend/app/utils/cache.py`

`DepartmentCache` 类提供了所有部门缓存操作：

```python
from app.utils.cache import DepartmentCache

# 获取部门列表缓存
departments = await DepartmentCache.get_departments_list(tenant_id)

# 设置部门列表缓存
await DepartmentCache.set_departments_list(tenant_id, departments)

# 获取部门详情缓存
department = await DepartmentCache.get_department_detail(dept_id)

# 设置部门详情缓存
await DepartmentCache.set_department_detail(dept_id, department)

# 清除所有缓存（用于更新/删除操作）
await DepartmentCache.clear_all_cache(tenant_id, dept_id=dept_id)
```

**ID字符串转换**: 所有缓存键中的ID（`tenant_id`、`dept_id`）都会通过 `_to_id_string()` 函数自动转换为字符串，确保：
- Redis key中的ID都是字符串类型
- 前端可以正常使用BigInt类型的ID
- 避免JavaScript精度丢失问题

### 2. 服务层集成

**文件**: `backend/app/services/department_service.py`

#### 2.1 查询方法（自动使用缓存）

**`get_departments()`**:
- 先尝试从缓存获取：`dept:list:{tenant_id}`
- 缓存未命中时查询数据库，并将结果写入缓存
- Redis连接失败时自动降级到数据库查询

**`get_department_by_id()`**:
- 先尝试从缓存获取：`dept:detail:{dept_id}`
- 缓存未命中时查询数据库，并将结果写入缓存
- 包含租户安全检查（如果缓存中的租户ID不匹配，会重新查询数据库）

#### 2.2 更新方法（自动清除缓存）

**`create_department()`**:
- 创建部门后，自动清除相关缓存
- 清除当前租户的列表和树缓存
- 如果是非超级管理员租户，同时清除超级管理员（tenant_id=0）的缓存

**`update_department()`**:
- 更新部门后，自动清除相关缓存
- 清除当前租户的列表、树缓存，以及该部门的详情缓存

**`delete_department()`**:
- 删除部门后，自动清除相关缓存
- 清除当前租户的列表、树缓存，以及该部门的详情缓存

### 3. 错误处理和降级

所有缓存操作都包含完善的错误处理：

- **Redis连接失败**: 自动降级到数据库查询，不影响业务功能
- **序列化/反序列化失败**: 自动降级到数据库查询
- **缓存操作异常**: 记录警告日志，但不影响业务流程

```python
try:
    cached_data = await DepartmentCache.get_departments_list(tenant_id)
    if cached_data:
        # 使用缓存数据
        return departments
except Exception as e:
    logger.warning(f"Failed to get departments from cache, falling back to DB: {e}")

# 降级到数据库查询
departments = await db.execute(stmt)
```

---

## 超级管理员支持

### 问题

超级管理员（`tenant_id=0`）可以访问所有租户的部门数据。当任何租户的部门数据变更时，超级管理员的缓存也需要清除。

### 解决方案

在 `clear_all_cache()` 方法中，如果变更的租户不是超级管理员（`tenant_id != 0`），会自动清除超级管理员的缓存：

```python
# 如果提供了dept_id，也清除详情缓存
if dept_id:
    detail_key = DepartmentCache.CACHE_KEY_DETAIL.format(dept_id=dept_id)
    keys_to_delete.append(detail_key)

# 同时清除超级管理员的缓存（tenant_id=0），因为超级管理员可以看到所有部门
if tenant_id != 0:
    superadmin_list_key = DepartmentCache.CACHE_KEY_LIST.format(tenant_id=0)
    superadmin_tree_key = DepartmentCache.CACHE_KEY_TREE.format(tenant_id=0)
    keys_to_delete.extend([superadmin_list_key, superadmin_tree_key])
```

---

## 性能优化

### 缓存命中率

- **部门列表查询**: 首次查询后缓存，后续查询直接从缓存读取，响应时间从 ~50ms 降低到 ~5ms
- **部门详情查询**: 单个部门查询也会被缓存，减少数据库查询
- **部门树构建**: 基于缓存的部门列表在内存中构建，性能足够

### 内存使用

- 部门数据量通常不大（每个租户通常 < 1000 个部门）
- JSON序列化后的数据大小：每个部门约 500-1000 字节
- 1000 个部门的缓存大小约 500KB-1MB，内存占用可控

---

## 使用示例

### 前端使用

前端无需修改，所有缓存逻辑都在后端自动处理：

```typescript
// 前端代码无需修改
import { getDepartmentTree } from '@/api/department';

// 首次调用：查询数据库并写入缓存
const response1 = await getDepartmentTree();

// 后续调用：直接从缓存读取
const response2 = await getDepartmentTree(); // 更快！
```

### 后端使用

后端服务层已自动集成缓存，无需额外代码：

```python
# 查询部门列表（自动使用缓存）
departments = await department_service.get_departments(db, tenant_id=1)

# 查询部门详情（自动使用缓存）
department = await department_service.get_department_by_id(db, dept_id=123)

# 创建部门（自动清除缓存）
department = await department_service.create_department(db, dept_data, tenant_id=1)

# 更新部门（自动清除缓存）
department = await department_service.update_department(db, dept_id, dept_data, tenant_id=1)

# 删除部门（自动清除缓存）
success = await department_service.delete_department(db, dept_id, tenant_id=1)
```

---

## 测试建议

### 1. 缓存命中测试

```python
# 首次查询（缓存未命中）
departments1 = await department_service.get_departments(db, tenant_id=1)
# 应该查询数据库

# 再次查询（缓存命中）
departments2 = await department_service.get_departments(db, tenant_id=1)
# 应该从缓存读取
```

### 2. 缓存更新测试

```python
# 创建部门
dept = await department_service.create_department(db, dept_data, tenant_id=1)

# 查询部门列表（应该重新查询数据库，因为缓存已清除）
departments = await department_service.get_departments(db, tenant_id=1)
# 应该包含新创建的部门
```

### 3. 多租户隔离测试

```python
# 租户1的部门列表
depts1 = await department_service.get_departments(db, tenant_id=1)

# 租户2的部门列表
depts2 = await department_service.get_departments(db, tenant_id=2)

# 两个租户的缓存应该互不影响
assert depts1 != depts2
```

### 4. 超级管理员测试

```python
# 超级管理员查询（tenant_id=0）
all_depts = await department_service.get_departments(db, tenant_id=0)

# 租户1创建部门
dept = await department_service.create_department(db, dept_data, tenant_id=1)

# 超级管理员再次查询（应该重新查询，因为缓存已清除）
all_depts_new = await department_service.get_departments(db, tenant_id=0)
# 应该包含新创建的部门
```

### 5. Redis故障降级测试

```python
# 模拟Redis不可用
# 修改 RedisClient.get_client() 使其返回 None

# 查询应该仍然正常工作（降级到数据库）
departments = await department_service.get_departments(db, tenant_id=1)
# 应该从数据库查询，不报错
```

---

## 监控和调试

### 日志

缓存操作会记录详细的日志：

- **缓存命中**: `DEBUG` 级别日志
- **缓存未命中**: 正常流程，不记录日志
- **缓存错误**: `WARNING` 级别日志，包含错误信息

### Redis监控

建议监控以下指标：

- **缓存命中率**: `(缓存命中次数) / (总查询次数)`
- **缓存大小**: 使用 `redis-cli --bigkeys` 查看大键
- **内存使用**: 监控Redis内存使用情况

### 调试命令

```bash
# 查看部门列表缓存
redis-cli GET "dept:list:1"

# 查看部门详情缓存
redis-cli GET "dept:detail:1234567890123456789"

# 清除所有部门缓存（手动）
redis-cli DEL "dept:list:1" "dept:tree:1" "dept:detail:1234567890123456789"

# 查看所有部门相关缓存键
redis-cli KEYS "dept:*"
```

---

## 注意事项

### 1. 数据一致性

- ✅ 采用"写时清除"策略，确保数据变更时立即清除缓存
- ✅ 不依赖过期时间，避免脏数据
- ⚠️ 注意：如果直接修改数据库（绕过服务层），需要手动清除缓存

### 2. 性能考虑

- ✅ 部门数据量通常不大，缓存主要是减少数据库连接和查询开销
- ✅ JSON序列化会占用一定内存，但部门数据量通常可控
- ⚠️ 如果部门数据量非常大（> 10000），考虑使用分页或限制缓存大小

### 3. 并发安全

- ✅ Redis操作本身是线程安全的
- ✅ 缓存清除和设置的时序已正确处理
- ⚠️ 注意：高并发场景下，可能出现缓存击穿（多个请求同时查询数据库），但影响较小

### 4. 扩展性

- ✅ 缓存键设计支持多租户隔离
- ✅ 支持超级管理员跨租户访问
- ✅ 可以轻松扩展到其他业务模块（如菜单、角色等）

---

## 相关文档

- [最佳实践指南](./BEST_PRACTICES.md) - 开发最佳实践
- [开发指南](./DEVELOPMENT_GUIDE.md) - 标准开发流程
- [数据库设计文档](./DATABASE_DESIGN.md) - 数据库表结构

---

## 更新日志

### v1.1 (2025-12-08)

- ✅ 修复Redis key中的ID类型问题
- ✅ 所有缓存键中的ID统一转换为字符串类型
- ✅ 确保前端可以正常使用BigInt类型的ID

### v1.0 (2025-12-08)

- ✅ 实现部门列表缓存
- ✅ 实现部门详情缓存
- ✅ 实现缓存自动清除机制
- ✅ 支持超级管理员缓存
- ✅ 完善错误处理和降级机制

---

**文档结束**

