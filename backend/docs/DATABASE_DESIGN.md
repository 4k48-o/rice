# 数据库设计文档

> **文档版本**: 1.0  
> **最后更新**: 2025-12-08  
> **数据库**: PostgreSQL 15+  
> **ORM**: SQLAlchemy 2.0 (Async)

---

## 目录

1. [数据库概述](#1-数据库概述)
2. [设计原则](#2-设计原则)
3. [核心概念](#3-核心概念)
4. [表结构设计](#4-表结构设计)
5. [表关系图](#5-表关系图)
6. [索引设计](#6-索引设计)
7. [数据隔离策略](#7-数据隔离策略)
8. [ID 生成策略](#8-id-生成策略)

---

## 1. 数据库概述

### 1.1 数据库类型
- **数据库**: PostgreSQL 15+
- **字符集**: UTF-8
- **时区**: UTC
- **连接方式**: 异步连接 (asyncpg)

### 1.2 表分类

| 分类 | 表数量 | 说明 |
|------|--------|------|
| 核心业务表 | 8 | 租户、用户、部门、角色、菜单、权限、日志 |
| 关联表 | 3 | 用户角色、角色权限、角色部门关联 |
| **总计** | **11** | |

### 1.3 核心特性
- ✅ 多租户数据隔离
- ✅ 软删除支持
- ✅ 审计字段（创建人、更新人、时间戳）
- ✅ 雪花算法 ID 生成
- ✅ 树形结构支持（部门、菜单）

---

## 2. 设计原则

### 2.1 命名规范
- **表名**: 小写，下划线分隔，复数形式（如 `users`, `user_roles`）
- **字段名**: 小写，下划线分隔（如 `user_id`, `created_at`）
- **索引名**: `ix_表名_字段名` 或 `uk_表名_字段名`（唯一索引）

### 2.2 字段类型规范
- **ID 字段**: `BigInteger`（支持雪花算法生成的 64 位整数）
- **时间字段**: `DateTime`（UTC 时间）
- **状态字段**: `SmallInteger`（0/1 枚举值）
- **文本字段**: `String`（根据实际需要指定长度）
- **大文本字段**: `Text`（不限长度）

### 2.3 数据完整性
- ✅ 主键约束（所有表）
- ✅ 外键约束（通过应用层保证，数据库层可选）
- ✅ 唯一约束（用户名、租户编码等）
- ✅ 非空约束（必填字段）
- ✅ 默认值（状态、时间等字段）

---

## 3. 核心概念

### 3.1 BaseModel 基类

所有业务表继承 `BaseModel`，自动包含以下字段：

```python
class BaseModel:
    id: BigInteger              # 主键，雪花算法生成
    remark: String(500)         # 备注（可选）
    created_at: DateTime        # 创建时间（自动）
    updated_at: DateTime        # 更新时间（自动）
    created_by: BigInteger      # 创建人ID（可选）
    updated_by: BigInteger      # 更新人ID（可选）
    is_deleted: Boolean         # 是否删除（默认false）
    deleted_at: DateTime        # 删除时间（可选）
    deleted_by: BigInteger      # 删除人ID（可选）
```

### 3.2 TenantMixin 多租户支持

除 `tenants` 表外，所有业务表继承 `TenantMixin`：

```python
class TenantMixin:
    tenant_id: BigInteger       # 租户ID，0表示平台级
```

**说明**：
- `tenant_id = 0`: 平台级数据，所有租户可见
- `tenant_id > 0`: 租户级数据，仅该租户可见
- `Tenant` 表本身不包含 `tenant_id`（它是租户实体本身）

### 3.3 软删除机制

所有业务表支持软删除：
- `is_deleted = false`: 正常数据
- `is_deleted = true`: 已删除数据（逻辑删除，不物理删除）

**查询时自动过滤**: `WHERE is_deleted = false`

---

## 4. 表结构设计

### 4.1 租户表 (tenants)

**表名**: `tenants`  
**说明**: 多租户系统的租户信息

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| `id` | `BigInteger` | PK | 主键，雪花算法生成 |
| `name` | `String(50)` | NOT NULL | 租户名称 |
| `code` | `String(50)` | UNIQUE, INDEX | 租户编码（唯一） |
| `contact_name` | `String(50)` | NULL | 联系人 |
| `contact_phone` | `String(20)` | NULL | 联系电话 |
| `status` | `SmallInteger` | NOT NULL, DEFAULT 1 | 状态：0禁用，1正常 |
| `domain` | `String(100)` | NULL | 绑定域名 |
| `expire_time` | `DateTime` | NULL | 过期时间 |
| `package_id` | `BigInteger` | NULL | 套餐ID |
| `account_count` | `Integer` | NOT NULL, DEFAULT 0 | 账号数量 |
| `remark` | `String(500)` | NULL | 备注 |
| `created_at` | `DateTime` | NOT NULL | 创建时间 |
| `updated_at` | `DateTime` | NOT NULL | 更新时间 |
| `created_by` | `BigInteger` | NULL | 创建人ID |
| `updated_by` | `BigInteger` | NULL | 更新人ID |
| `is_deleted` | `Boolean` | NOT NULL, DEFAULT false | 是否删除 |
| `deleted_at` | `DateTime` | NULL | 删除时间 |
| `deleted_by` | `BigInteger` | NULL | 删除人ID |

**特殊说明**:
- `Tenant` 表不包含 `tenant_id`（它是租户实体本身）
- `code` 字段全局唯一，用于租户识别

---

### 4.2 用户表 (users)

**表名**: `users`  
**说明**: 系统用户信息

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| `id` | `BigInteger` | PK | 主键，雪花算法生成 |
| `tenant_id` | `BigInteger` | NOT NULL, INDEX, DEFAULT 0 | 租户ID |
| `username` | `String(50)` | NOT NULL | 用户名 |
| `password` | `String(255)` | NOT NULL | 密码（bcrypt哈希） |
| `real_name` | `String(50)` | NULL | 真实姓名 |
| `nickname` | `String(50)` | NULL | 昵称 |
| `email` | `String(100)` | INDEX | 邮箱 |
| `phone` | `String(20)` | INDEX | 手机号 |
| `user_type` | `SmallInteger` | NOT NULL, DEFAULT 1 | 用户类型：0超级管理员，1租户管理员，2普通用户 |
| `dept_id` | `BigInteger` | INDEX | 部门ID |
| `position` | `String(50)` | NULL | 职位 |
| `status` | `SmallInteger` | NOT NULL, INDEX, DEFAULT 1 | 状态：0禁用，1正常，2锁定 |
| `avatar` | `String(255)` | NULL | 头像URL |
| `gender` | `SmallInteger` | NULL | 性别：0未知，1男，2女 |
| `last_login_time` | `DateTime` | NULL | 最后登录时间 |
| `last_login_ip` | `String(50)` | NULL | 最后登录IP |
| `login_count` | `Integer` | NOT NULL, DEFAULT 0 | 登录次数 |
| `password_updated_at` | `DateTime` | NULL | 密码更新时间 |
| `must_change_password` | `Boolean` | NOT NULL, DEFAULT false | 是否必须修改密码 |
| `remark` | `String(500)` | NULL | 备注 |
| `created_at` | `DateTime` | NOT NULL | 创建时间 |
| `updated_at` | `DateTime` | NOT NULL | 更新时间 |
| `created_by` | `BigInteger` | NULL | 创建人ID |
| `updated_by` | `BigInteger` | NULL | 更新人ID |
| `is_deleted` | `Boolean` | NOT NULL, DEFAULT false | 是否删除 |
| `deleted_at` | `DateTime` | NULL | 删除时间 |
| `deleted_by` | `BigInteger` | NULL | 删除人ID |

**关系**:
- 多对多: `users` ↔ `roles` (通过 `user_roles` 表)
- 多对一: `users` → `departments` (通过 `dept_id`)

**索引**:
- `ix_users_tenant_id`: 租户查询
- `ix_users_email`: 邮箱登录
- `ix_users_phone`: 手机号登录
- `ix_users_dept_id`: 部门查询
- `ix_users_status`: 状态筛选

---

### 4.3 部门表 (departments)

**表名**: `departments`  
**说明**: 组织架构部门信息（树形结构）

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| `id` | `BigInteger` | PK | 主键，雪花算法生成 |
| `tenant_id` | `BigInteger` | NOT NULL, INDEX, DEFAULT 0 | 租户ID |
| `parent_id` | `BigInteger` | INDEX | 父部门ID，NULL表示顶级部门 |
| `name` | `String(50)` | NOT NULL | 部门名称 |
| `code` | `String(50)` | NOT NULL, INDEX | 部门编码 |
| `leader_id` | `BigInteger` | NULL | 部门负责人ID（关联users.id） |
| `phone` | `String(20)` | NULL | 联系电话 |
| `email` | `String(100)` | NULL | 邮箱 |
| `sort` | `Integer` | NOT NULL, DEFAULT 0 | 排序（升序） |
| `status` | `Integer` | NOT NULL, DEFAULT 1 | 状态：0禁用，1启用 |
| `remark` | `String(500)` | NULL | 备注 |
| `created_at` | `DateTime` | NOT NULL | 创建时间 |
| `updated_at` | `DateTime` | NOT NULL | 更新时间 |
| `created_by` | `BigInteger` | NULL | 创建人ID |
| `updated_by` | `BigInteger` | NULL | 更新人ID |
| `is_deleted` | `Boolean` | NOT NULL, DEFAULT false | 是否删除 |
| `deleted_at` | `DateTime` | NULL | 删除时间 |
| `deleted_by` | `BigInteger` | NULL | 删除人ID |

**关系**:
- 自关联: `departments.parent_id` → `departments.id` (树形结构)
- 多对一: `departments.leader_id` → `users.id` (负责人)

**索引**:
- `ix_departments_tenant_id`: 租户查询
- `ix_departments_parent_id`: 父部门查询
- `ix_departments_code`: 部门编码查询

---

### 4.4 角色表 (roles)

**表名**: `roles`  
**说明**: 系统角色信息

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| `id` | `BigInteger` | PK | 主键，雪花算法生成 |
| `tenant_id` | `BigInteger` | NOT NULL, INDEX, DEFAULT 0 | 租户ID |
| `name` | `String(50)` | NOT NULL | 角色名称 |
| `code` | `String(50)` | NOT NULL, INDEX | 角色编码 |
| `sort` | `SmallInteger` | NOT NULL, DEFAULT 0 | 显示顺序 |
| `status` | `SmallInteger` | NOT NULL, DEFAULT 1 | 状态：0禁用，1正常 |
| `data_scope` | `SmallInteger` | NOT NULL, DEFAULT 1 | 数据权限：1全部，2本部门及以下，3本部门，4仅本人，5自定义 |
| `remark` | `String(500)` | NULL | 备注 |
| `created_at` | `DateTime` | NOT NULL | 创建时间 |
| `updated_at` | `DateTime` | NOT NULL | 更新时间 |
| `created_by` | `BigInteger` | NULL | 创建人ID |
| `updated_by` | `BigInteger` | NULL | 更新人ID |
| `is_deleted` | `Boolean` | NOT NULL, DEFAULT false | 是否删除 |
| `deleted_at` | `DateTime` | NULL | 删除时间 |
| `deleted_by` | `BigInteger` | NULL | 删除人ID |

**关系**:
- 多对多: `roles` ↔ `users` (通过 `user_roles` 表)
- 多对多: `roles` ↔ `permissions` (通过 `role_permissions` 表)
- 多对多: `roles` ↔ `departments` (通过 `role_departments` 表，用于自定义数据权限)

**索引**:
- `ix_roles_tenant_id`: 租户查询
- `ix_roles_code`: 角色编码查询

**数据权限说明**:
- `data_scope = 1`: 全部数据权限
- `data_scope = 2`: 本部门及子部门数据
- `data_scope = 3`: 本部门数据
- `data_scope = 4`: 仅本人数据
- `data_scope = 5`: 自定义数据权限（通过 `role_departments` 表配置）

---

### 4.5 菜单表 (menus)

**表名**: `menus`  
**说明**: 系统菜单导航（树形结构）

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| `id` | `BigInteger` | PK | 主键，雪花算法生成 |
| `tenant_id` | `BigInteger` | NOT NULL, INDEX, DEFAULT 0 | 租户ID |
| `parent_id` | `BigInteger` | INDEX | 父菜单ID，NULL表示顶级菜单 |
| `name` | `String(50)` | NOT NULL | 菜单名称 |
| `title` | `String(50)` | NOT NULL | 菜单标题（用于显示） |
| `path` | `String(200)` | NULL | 路由路径 |
| `component` | `String(200)` | NULL | 组件路径 |
| `redirect` | `String(200)` | NULL | 重定向路径 |
| `icon` | `String(100)` | NULL | 图标 |
| `sort` | `Integer` | NOT NULL, DEFAULT 0 | 排序（升序） |
| `type` | `SmallInteger` | NOT NULL, DEFAULT 1 | 类型：1目录，2菜单，3按钮 |
| `permission_code` | `String(100)` | INDEX | 权限标识，如 `user:list` |
| `status` | `SmallInteger` | NOT NULL, DEFAULT 1 | 状态：0禁用，1启用 |
| `visible` | `SmallInteger` | NOT NULL, DEFAULT 1 | 是否可见：0隐藏，1显示 |
| `is_cache` | `SmallInteger` | NOT NULL, DEFAULT 0 | 是否缓存：0否，1是 |
| `is_external` | `SmallInteger` | NOT NULL, DEFAULT 0 | 是否外链：0否，1是 |
| `remark` | `String(500)` | NULL | 备注 |
| `created_at` | `DateTime` | NOT NULL | 创建时间 |
| `updated_at` | `DateTime` | NOT NULL | 更新时间 |
| `created_by` | `BigInteger` | NULL | 创建人ID |
| `updated_by` | `BigInteger` | NULL | 更新人ID |
| `is_deleted` | `Boolean` | NOT NULL, DEFAULT false | 是否删除 |
| `deleted_at` | `DateTime` | NULL | 删除时间 |
| `deleted_by` | `BigInteger` | NULL | 删除人ID |

**关系**:
- 自关联: `menus.parent_id` → `menus.id` (树形结构)

**索引**:
- `ix_menus_tenant_id`: 租户查询
- `ix_menus_parent_id`: 父菜单查询
- `ix_menus_permission_code`: 权限标识查询

---

### 4.6 权限表 (permissions)

**表名**: `permissions`  
**说明**: 系统权限资源（树形结构）

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| `id` | `BigInteger` | PK | 主键，雪花算法生成 |
| `tenant_id` | `BigInteger` | NOT NULL, INDEX, DEFAULT 0 | 租户ID |
| `parent_id` | `BigInteger` | NOT NULL, INDEX, DEFAULT 0 | 父级ID，0表示顶级 |
| `name` | `String(50)` | NOT NULL | 菜单名称 |
| `code` | `String(100)` | INDEX | 权限标识（唯一标识权限） |
| `type` | `SmallInteger` | NOT NULL, DEFAULT 1 | 类型：1目录，2菜单，3按钮 |
| `path` | `String(255)` | NULL | 路由路径 |
| `component` | `String(255)` | NULL | 前端组件 |
| `icon` | `String(50)` | NULL | 图标 |
| `sort` | `Integer` | NOT NULL, DEFAULT 0 | 排序 |
| `status` | `SmallInteger` | NOT NULL, DEFAULT 1 | 状态：0禁用，1正常 |
| `visible` | `SmallInteger` | NOT NULL, DEFAULT 1 | 是否可见：0隐藏，1显示 |
| `remark` | `String(500)` | NULL | 备注 |
| `created_at` | `DateTime` | NOT NULL | 创建时间 |
| `updated_at` | `DateTime` | NOT NULL | 更新时间 |
| `created_by` | `BigInteger` | NULL | 创建人ID |
| `updated_by` | `BigInteger` | NULL | 更新人ID |
| `is_deleted` | `Boolean` | NOT NULL, DEFAULT false | 是否删除 |
| `deleted_at` | `DateTime` | NULL | 删除时间 |
| `deleted_by` | `BigInteger` | NULL | 删除人ID |

**关系**:
- 自关联: `permissions.parent_id` → `permissions.id` (树形结构)
- 多对多: `permissions` ↔ `roles` (通过 `role_permissions` 表)

**索引**:
- `ix_permissions_tenant_id`: 租户查询
- `ix_permissions_parent_id`: 父权限查询
- `ix_permissions_code`: 权限标识查询

---

### 4.7 登录日志表 (sys_login_log)

**表名**: `sys_login_log`  
**说明**: 用户登录日志

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| `id` | `BigInteger` | PK | 主键，雪花算法生成 |
| `tenant_id` | `BigInteger` | NOT NULL, INDEX, DEFAULT 0 | 租户ID |
| `user_id` | `BigInteger` | NULL | 用户ID |
| `username` | `String(50)` | NOT NULL | 用户名 |
| `status` | `SmallInteger` | NOT NULL, DEFAULT 1 | 状态：1成功，0失败 |
| `ip` | `String(50)` | NULL | 登录IP |
| `location` | `String(100)` | NULL | IP归属地 |
| `browser` | `String(100)` | NULL | 浏览器 |
| `os` | `String(100)` | NULL | 操作系统 |
| `msg` | `String(255)` | NULL | 提示消息 |
| `login_time` | `DateTime` | NOT NULL | 登录时间 |
| `remark` | `String(500)` | NULL | 备注 |
| `created_at` | `DateTime` | NOT NULL | 创建时间 |
| `updated_at` | `DateTime` | NOT NULL | 更新时间 |
| `created_by` | `BigInteger` | NULL | 创建人ID |
| `updated_by` | `BigInteger` | NULL | 更新人ID |
| `is_deleted` | `Boolean` | NOT NULL, DEFAULT false | 是否删除 |
| `deleted_at` | `DateTime` | NULL | 删除时间 |
| `deleted_by` | `BigInteger` | NULL | 删除人ID |

**索引**:
- `ix_sys_login_log_tenant_id`: 租户查询
- 建议: 在 `(tenant_id, login_time)` 上创建复合索引用于时间范围查询

---

### 4.8 操作日志表 (sys_opt_log)

**表名**: `sys_opt_log`  
**说明**: 系统操作日志

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| `id` | `BigInteger` | PK | 主键，雪花算法生成 |
| `tenant_id` | `BigInteger` | NOT NULL, INDEX, DEFAULT 0 | 租户ID |
| `user_id` | `BigInteger` | NULL | 用户ID |
| `username` | `String(50)` | NULL | 用户名 |
| `module` | `String(50)` | NULL | 功能模块 |
| `summary` | `String(255)` | NULL | 操作摘要 |
| `method` | `String(20)` | NULL | 请求方法 |
| `url` | `String(255)` | NULL | 请求路径 |
| `ip` | `String(50)` | NULL | 请求IP |
| `location` | `String(100)` | NULL | IP归属地 |
| `user_agent` | `String(500)` | NULL | UA系统 |
| `params` | `JSON` | NULL | 请求参数 |
| `result` | `JSON` | NULL | 响应结果 |
| `status` | `SmallInteger` | NOT NULL, DEFAULT 1 | 状态：1成功，0失败 |
| `error_msg` | `Text` | NULL | 错误消息 |
| `duration` | `Integer` | NULL | 耗时（毫秒） |
| `remark` | `String(500)` | NULL | 备注 |
| `created_at` | `DateTime` | NOT NULL | 创建时间 |
| `updated_at` | `DateTime` | NOT NULL | 更新时间 |
| `created_by` | `BigInteger` | NULL | 创建人ID |
| `updated_by` | `BigInteger` | NULL | 更新人ID |
| `is_deleted` | `Boolean` | NOT NULL, DEFAULT false | 是否删除 |
| `deleted_at` | `DateTime` | NULL | 删除时间 |
| `deleted_by` | `BigInteger` | NULL | 删除人ID |

**索引**:
- `ix_sys_opt_log_tenant_id`: 租户查询
- 建议: 在 `(tenant_id, created_at)` 上创建复合索引用于时间范围查询
- 建议: 在 `(tenant_id, user_id)` 上创建复合索引用于用户操作查询

---

### 4.9 关联表

#### 4.9.1 用户角色关联表 (user_roles)

**表名**: `user_roles`  
**说明**: 用户与角色的多对多关联

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| `id` | `BigInteger` | PK | 主键，数据库自增 |
| `tenant_id` | `BigInteger` | NOT NULL, INDEX, DEFAULT 0 | 租户ID |
| `user_id` | `BigInteger` | NOT NULL, INDEX | 用户ID |
| `role_id` | `BigInteger` | NOT NULL, INDEX | 角色ID |
| `created_at` | `DateTime` | NOT NULL | 创建时间 |
| `created_by` | `BigInteger` | NULL | 创建人ID |

**约束**:
- 唯一约束: `uk_user_role` (`user_id`, `role_id`) - 同一用户不能重复分配同一角色

**索引**:
- `ix_user_roles_tenant_id`: 租户查询
- `ix_user_roles_user_id`: 用户查询
- `ix_user_roles_role_id`: 角色查询

---

#### 4.9.2 角色权限关联表 (role_permissions)

**表名**: `role_permissions`  
**说明**: 角色与权限的多对多关联

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| `id` | `BigInteger` | PK | 主键，数据库自增 |
| `tenant_id` | `BigInteger` | NOT NULL, INDEX, DEFAULT 0 | 租户ID |
| `role_id` | `BigInteger` | NOT NULL, INDEX | 角色ID |
| `permission_id` | `BigInteger` | NOT NULL, INDEX | 权限ID |
| `created_at` | `DateTime` | NOT NULL | 创建时间 |
| `created_by` | `BigInteger` | NULL | 创建人ID |

**约束**:
- 唯一约束: `uk_role_permission` (`role_id`, `permission_id`) - 同一角色不能重复分配同一权限

**索引**:
- `ix_role_permissions_tenant_id`: 租户查询
- `ix_role_permissions_role_id`: 角色查询
- `ix_role_permissions_permission_id`: 权限查询

---

#### 4.9.3 角色部门关联表 (role_departments)

**表名**: `role_departments`  
**说明**: 角色与部门的关联（用于自定义数据权限，`data_scope = 5` 时使用）

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| `id` | `BigInteger` | PK | 主键，数据库自增 |
| `role_id` | `BigInteger` | NOT NULL, INDEX | 角色ID |
| `department_id` | `BigInteger` | NOT NULL, INDEX | 部门ID |

**约束**:
- 唯一约束: `uk_role_department` (`role_id`, `department_id`) - 同一角色不能重复分配同一部门

**索引**:
- `ix_role_departments_role_id`: 角色查询
- `ix_role_departments_department_id`: 部门查询

**说明**:
- 此表不包含 `tenant_id`（通过 `role_id` 和 `department_id` 关联到租户）
- 仅在角色的 `data_scope = 5`（自定义数据权限）时使用

---

## 5. 表关系图

```
┌─────────────┐
│   tenants   │ (租户表)
└─────────────┘
      │
      │ 1:N
      ▼
┌─────────────┐         ┌─────────────┐
│    users    │────────▶│ departments │
└─────────────┘  N:1    └─────────────┘
      │                         │
      │ M:N                     │ 1:N (树形)
      │                         ▼
      │                  ┌─────────────┐
      │                  │ departments │ (自关联)
      │                  └─────────────┘
      │
      │ M:N
      ▼
┌─────────────┐         ┌─────────────┐
│ user_roles  │────────▶│    roles    │
└─────────────┘         └─────────────┘
                              │
                              │ M:N
                              ▼
                     ┌──────────────────┐
                     │ role_permissions │────────▶┌─────────────┐
                     └──────────────────┘         │ permissions │
                              │                   └─────────────┘
                              │                           │
                              │ 1:N (树形)                │ 1:N (树形)
                              ▼                           ▼
                     ┌──────────────────┐         ┌─────────────┐
                     │ role_departments │────────▶│ permissions │ (自关联)
                     └──────────────────┘         └─────────────┘

┌─────────────┐         ┌─────────────┐
│sys_login_log│         │ sys_opt_log │
└─────────────┘         └─────────────┘
      │                         │
      │ N:1                     │ N:1
      ▼                         ▼
┌─────────────┐         ┌─────────────┐
│    users    │         │    users    │
└─────────────┘         └─────────────┘
```

### 5.1 主要关系说明

1. **租户 → 用户**: 一对多（一个租户有多个用户）
2. **用户 → 部门**: 多对一（一个用户属于一个部门）
3. **用户 ↔ 角色**: 多对多（通过 `user_roles` 表）
4. **角色 ↔ 权限**: 多对多（通过 `role_permissions` 表）
5. **角色 ↔ 部门**: 多对多（通过 `role_departments` 表，自定义数据权限）
6. **部门**: 自关联（树形结构，通过 `parent_id`）
7. **菜单**: 自关联（树形结构，通过 `parent_id`）
8. **权限**: 自关联（树形结构，通过 `parent_id`）

---

## 6. 索引设计

### 6.1 单列索引

所有表都包含以下基础索引：

| 表名 | 索引字段 | 索引名 | 用途 |
|------|---------|--------|------|
| 所有业务表 | `tenant_id` | `ix_{table}_tenant_id` | 租户数据隔离查询 |
| `users` | `email` | `ix_users_email` | 邮箱登录 |
| `users` | `phone` | `ix_users_phone` | 手机号登录 |
| `users` | `dept_id` | `ix_users_dept_id` | 部门查询 |
| `users` | `status` | `ix_users_status` | 状态筛选 |
| `departments` | `parent_id` | `ix_departments_parent_id` | 父部门查询 |
| `departments` | `code` | `ix_departments_code` | 部门编码查询 |
| `roles` | `code` | `ix_roles_code` | 角色编码查询 |
| `menus` | `parent_id` | `ix_menus_parent_id` | 父菜单查询 |
| `menus` | `permission_code` | `ix_menus_permission_code` | 权限标识查询 |
| `permissions` | `parent_id` | `ix_permissions_parent_id` | 父权限查询 |
| `permissions` | `code` | `ix_permissions_code` | 权限标识查询 |

### 6.2 复合索引（建议）

| 表名 | 索引字段 | 索引名 | 用途 |
|------|---------|--------|------|
| `users` | `(tenant_id, status)` | `ix_users_tenant_status` | 租户内状态筛选 |
| `users` | `(tenant_id, dept_id)` | `ix_users_tenant_dept` | 租户内部门查询 |
| `departments` | `(tenant_id, parent_id)` | `ix_dept_tenant_parent` | 租户内部门树查询 |
| `sys_login_log` | `(tenant_id, login_time)` | `ix_login_tenant_time` | 租户登录日志时间查询 |
| `sys_opt_log` | `(tenant_id, created_at)` | `ix_opt_tenant_time` | 租户操作日志时间查询 |
| `sys_opt_log` | `(tenant_id, user_id)` | `ix_opt_tenant_user` | 租户用户操作查询 |

### 6.3 唯一索引

| 表名 | 索引字段 | 索引名 | 说明 |
|------|---------|--------|------|
| `tenants` | `code` | `uk_tenants_code` | 租户编码全局唯一 |
| `user_roles` | `(user_id, role_id)` | `uk_user_role` | 用户角色关联唯一 |
| `role_permissions` | `(role_id, permission_id)` | `uk_role_permission` | 角色权限关联唯一 |
| `role_departments` | `(role_id, department_id)` | `uk_role_department` | 角色部门关联唯一 |

---

## 7. 数据隔离策略

### 7.1 多租户隔离

**策略**: 共享数据库，共享 Schema，逻辑隔离（Discriminator Column）

**实现**:
- 所有业务表（除 `tenants` 外）包含 `tenant_id` 字段
- 应用层查询时自动添加 `tenant_id` 过滤条件
- 超级管理员（`user_type = 0`）可以跨租户访问

**查询示例**:
```python
# 自动过滤租户数据
stmt = select(User).where(
    User.tenant_id == current_user.tenant_id,
    User.is_deleted == False
)
```

### 7.2 数据权限隔离

**策略**: 基于角色的数据范围（Data Scope）

**数据范围类型**:
1. **全部数据** (`data_scope = 1`): 可访问所有租户内数据
2. **本部门及以下** (`data_scope = 2`): 可访问本部门及子部门数据
3. **本部门** (`data_scope = 3`): 仅可访问本部门数据
4. **仅本人** (`data_scope = 4`): 仅可访问本人数据
5. **自定义** (`data_scope = 5`): 通过 `role_departments` 表配置可访问的部门

**实现位置**: `app/core/permissions.py` 和 `app/services/*_service.py`

---

## 8. ID 生成策略

### 8.1 雪花算法（Snowflake）

**使用范围**: 所有业务主表（8 张表）

| 表名 | ID 生成方式 |
|------|-----------|
| `tenants` | 雪花算法 ✅ |
| `users` | 雪花算法 ✅ |
| `departments` | 雪花算法 ✅ |
| `roles` | 雪花算法 ✅ |
| `menus` | 雪花算法 ✅ |
| `permissions` | 雪花算法 ✅ |
| `sys_login_log` | 雪花算法 ✅ |
| `sys_opt_log` | 雪花算法 ✅ |

**实现机制**:
- 在 `before_insert` 事件中自动生成
- 如果 `id` 为 `None`，自动调用 `generate_id()` 生成
- ID 类型: `BigInteger`（64 位整数）

**配置参数**:
```python
SNOWFLAKE_DATACENTER_ID: int = 0  # 0-31
SNOWFLAKE_WORKER_ID: int = 0      # 0-31
SNOWFLAKE_EPOCH: int = 1609459200000  # 2021-01-01 00:00:00 UTC
```

### 8.2 数据库自增

**使用范围**: 关联表（3 张表）

| 表名 | ID 生成方式 |
|------|-----------|
| `user_roles` | 数据库自增 ✅ |
| `role_permissions` | 数据库自增 ✅ |
| `role_departments` | 数据库自增 ✅ |

**原因**:
- 关联表不需要分布式唯一性
- 自增 ID 性能更好，占用空间更小

---

## 9. 数据库迁移

### 9.1 迁移工具

- **工具**: Alembic
- **配置文件**: `alembic.ini`
- **迁移目录**: `backend/alembic/versions/`

### 9.2 常用命令

```bash
# 创建迁移
alembic revision --autogenerate -m "description"

# 执行迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1

# 查看迁移历史
alembic history
```

### 9.3 迁移文件列表

1. `51079b45a694_add_auth_models.py` - 创建认证相关表（users, roles, permissions, tenants）
2. `800c7f8c34e6_add_menus_table.py` - 创建菜单表
3. `25753b260180_add_departments_table.py` - 创建部门表
4. `ca21df2d286f_add_log_models.py` - 创建日志表
5. `d675cfa187b4_add_tenant_id_and_audit_fields_to_.py` - 添加租户ID和审计字段
6. `4ca356db0472_add_role_custom_dept_ids_and_.py` - 添加角色自定义部门权限
7. `597f7ddd950d_change_user_id_to_bigint_in_log_tables.py` - 修改日志表用户ID为BigInteger

---

## 10. 数据字典

### 10.1 枚举值定义

#### 用户类型 (user_type)
- `0`: 超级管理员（平台级）
- `1`: 租户管理员
- `2`: 普通用户

#### 用户状态 (status - users)
- `0`: 禁用
- `1`: 正常
- `2`: 锁定

#### 部门/菜单/权限状态 (status)
- `0`: 禁用
- `1`: 启用

#### 角色状态 (status - roles)
- `0`: 禁用
- `1`: 正常

#### 数据权限范围 (data_scope)
- `1`: 全部数据
- `2`: 本部门及以下
- `3`: 本部门
- `4`: 仅本人
- `5`: 自定义

#### 菜单/权限类型 (type)
- `1`: 目录
- `2`: 菜单
- `3`: 按钮

#### 性别 (gender)
- `0`: 未知
- `1`: 男
- `2`: 女

#### 日志状态 (status - logs)
- `0`: 失败
- `1`: 成功

---

## 11. 性能优化建议

### 11.1 索引优化

- ✅ 所有 `tenant_id` 字段已建立索引
- ✅ 所有外键字段已建立索引
- ⚠️ 建议添加复合索引用于常用查询组合

### 11.2 查询优化

1. **软删除过滤**: 所有查询自动添加 `is_deleted = false` 条件
2. **租户过滤**: 所有业务查询自动添加 `tenant_id` 条件
3. **分页查询**: 使用 LIMIT/OFFSET 或游标分页
4. **关联查询**: 使用 `selectin` 加载策略，避免 N+1 问题

### 11.3 数据归档

- 日志表建议定期归档旧数据（如 1 年以前）
- 考虑使用分区表（PostgreSQL Partitioning）按时间分区日志表

---

## 12. 安全性考虑

### 12.1 数据访问控制

- ✅ 租户数据隔离（应用层保证）
- ✅ 软删除机制（防止数据误删）
- ✅ 审计字段（记录操作人）

### 12.2 敏感数据

- 密码字段: 使用 bcrypt 哈希，不存储明文
- 日志参数: 建议过滤敏感字段（如密码）后再记录

---

## 13. 相关文档

- [ID 生成策略](./ID_GENERATION_STRATEGY.md)
- [API 接口文档](./API_DOCUMENTATION.md)
- [开发指南](./DEVELOPMENT_GUIDE.md)
- [最佳实践](./BEST_PRACTICES.md)

---

## 14. 更新历史

| 版本 | 日期 | 更新内容 | 作者 |
|------|------|---------|------|
| 1.0 | 2025-12-08 | 初始版本，完整数据库设计文档 | System |

---

## 附录

### A. 数据库初始化脚本

```bash
# 创建数据库
createdb fast_andt_admin

# 执行迁移
cd backend
alembic upgrade head

# 初始化数据
python scripts/init_data.py
python scripts/seed_roles_permissions.py
```

### B. 表统计信息

```sql
-- 查看所有表
SELECT tablename FROM pg_tables WHERE schemaname = 'public';

-- 查看表大小
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

---

**文档结束**

