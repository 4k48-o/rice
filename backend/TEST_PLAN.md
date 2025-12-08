# 系统全面测试方案

## 测试状态概览

### ✅ 已完成的测试
- **Snowflake ID 生成器** - 11个测试用例（100%覆盖）
- **密码策略** - 基础测试
- **异常处理** - 基础测试
- **I18n国际化** - 基础测试
- **单点登录** - 基础测试

### ❌ 待完成的测试
- 认证授权完整测试套件
- 用户管理完整测试
- 角色管理测试
- 部门管理测试
- 菜单管理测试
- 权限控制测试
- 性能测试
- 安全测试
- 端到端测试

---

## 一、单元测试 (Unit Tests)

### 1.1 Snowflake ID 生成器 ✅ **已完成**
**文件**: `tests/test_utils/test_snowflake.py`

**已实现的测试用例** (11个):
- ✅ `test_snowflake_initialization` - 初始化测试
- ✅ `test_invalid_datacenter_id` - 无效数据中心ID
- ✅ `test_invalid_worker_id` - 无效工作节点ID
- ✅ `test_generate_id` - 基础ID生成
- ✅ `test_id_uniqueness` - 唯一性验证（10,000个ID）
- ✅ `test_concurrent_id_generation` - 并发测试（10线程，10,000个ID）
- ✅ `test_parse_id` - ID解析功能
- ✅ `test_global_functions` - 全局函数测试
- ✅ `test_sequence_overflow` - 序列号溢出处理
- ✅ `test_id_format` - ID格式验证
- ✅ `test_performance` - 性能基准测试（1.2M+ IDs/秒）

**建议补充**:
- [ ] 时钟回拨极端场景测试
- [ ] 跨时区ID生成测试

---

### 1.2 密码安全工具 ⚠️ **部分完成**
**文件**: `tests/test_password_policy.py`

**已实现的测试用例**:
- ✅ 密码强度校验基础测试

**待补充的测试用例**:
```python
# 密码加密和验证
def test_password_hashing():
    """测试密码加密"""
    from app.core.security import get_password_hash, verify_password
    
    password = "Test@123456"
    hashed = get_password_hash(password)
    
    # 验证哈希值不等于原密码
    assert hashed != password
    # 验证密码验证成功
    assert verify_password(password, hashed)
    # 验证错误密码失败
    assert not verify_password("wrong", hashed)

# 密码强度校验
def test_password_strength_weak():
    """测试弱密码"""
    weak_passwords = [
        "123456",           # 纯数字
        "password",         # 纯字母
        "Pass123",          # 缺少特殊字符
        "P@ss",             # 长度不足
        "PASS@123",         # 缺少小写
        "pass@123",         # 缺少大写
    ]
    for pwd in weak_passwords:
        # 应抛出验证错误
        with pytest.raises(ValueError):
            validate_password_strength(pwd)

def test_password_strength_strong():
    """测试强密码"""
    strong_passwords = [
        "Test@123456",
        "MyP@ssw0rd",
        "Secure#2024",
    ]
    for pwd in strong_passwords:
        # 应通过验证
        validate_password_strength(pwd)  # 不抛出异常

# 密码过期检查
def test_password_expiry():
    """测试密码过期检查"""
    from datetime import datetime, timedelta
    
    # 未过期密码
    recent_date = datetime.utcnow() - timedelta(days=10)
    assert not is_password_expired(recent_date, days=30)
    
    # 已过期密码
    old_date = datetime.utcnow() - timedelta(days=40)
    assert is_password_expired(old_date, days=30)

# 密码历史检查
def test_password_history():
    """测试密码历史（防止重复使用）"""
    # 新密码不在历史中 -> 允许
    # 新密码在历史中 -> 拒绝
```

---

### 1.3 权限工具 ❌ **未完成**
**文件**: `tests/test_core/test_permissions.py` (待创建)

**待实现的测试用例**:
```python
async def test_get_user_permissions():
    """测试获取用户权限"""
    # 创建用户、角色、权限
    # 分配角色给用户
    # 验证返回正确的权限列表
    
async def test_get_user_roles():
    """测试获取用户角色"""
    # 创建用户和多个角色
    # 分配角色
    # 验证返回所有角色

async def test_get_user_data_scope():
    """测试获取用户数据权限范围"""
    # 用户有多个角色时，返回最宽松的权限
    # 角色1: data_scope=4 (仅本人)
    # 角色2: data_scope=2 (本部门及下级)
    # 应返回: 2

async def test_apply_data_scope_filter():
    """测试应用数据权限过滤"""
    # data_scope=1: 查询所有数据
    # data_scope=2: 查询本部门及下级
    # data_scope=3: 查询本部门
    # data_scope=4: 查询本人数据
```

---

## 二、集成测试 (Integration Tests)

### 2.1 认证授权模块 ⚠️ **部分完成**
**文件**: `tests/test_api/test_auth_manual.py`, `tests/test_single_session.py`

**已实现的测试**:
- ✅ 单点登录基础测试

**待补充的测试用例**:

#### 2.1.1 用户登录 ❌
```python
async def test_login_success():
    """测试成功登录"""
    response = await client.post("/api/v1/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data["data"]
    assert "refresh_token" in data["data"]
    
    # 验证Redis中存储了token
    redis_key = f"user_token:{user_id}"
    cached_token = await redis.get(redis_key)
    assert cached_token == data["data"]["access_token"]

async def test_login_wrong_password():
    """测试错误密码"""
    response = await client.post("/api/v1/auth/login", json={
        "username": "admin",
        "password": "wrongpassword"
    })
    assert response.status_code == 401
    assert "密码错误" in response.json()["message"]

async def test_login_nonexistent_user():
    """测试不存在的用户"""
    response = await client.post("/api/v1/auth/login", json={
        "username": "nonexistent",
        "password": "password"
    })
    assert response.status_code == 401

async def test_login_disabled_user():
    """测试禁用用户登录"""
    # 创建禁用用户 (status=0)
    # 尝试登录
    # 应返回403
    
async def test_login_password_expired():
    """测试密码过期"""
    # 创建密码已过期的用户
    # 登录应成功但提示修改密码
    
async def test_login_rate_limiting():
    """测试登录频率限制"""
    # 短时间内多次登录失败
    # 应触发频率限制

async def test_login_with_different_languages():
    """测试不同语言的登录响应"""
    # Accept-Language: zh -> 中文响应
    # Accept-Language: en -> 英文响应
    # Accept-Language: ja -> 日文响应
```

#### 2.1.2 单点登录 ✅ **已完成**
```python
async def test_single_session_enforcement():
    """测试单点登录强制"""
    # 已在 test_single_session.py 中实现
```

#### 2.1.3 Token刷新 ❌
```python
async def test_token_refresh_success():
    """测试Token刷新成功"""
    # 登录获取refresh_token
    # 使用refresh_token刷新
    # 验证返回新的access_token
    
async def test_token_refresh_invalid():
    """测试无效refresh_token"""
    response = await client.post("/api/v1/auth/refresh", json={
        "refresh_token": "invalid_token"
    })
    assert response.status_code == 401

async def test_token_refresh_expired():
    """测试过期的refresh_token"""
    # 使用已过期的refresh_token
    # 应返回401
```

#### 2.1.4 用户登出 ❌
```python
async def test_logout_success():
    """测试成功登出"""
    # 登录获取token
    # 登出
    # 验证Redis中token被删除
    # 使用旧token访问 -> 401

async def test_logout_without_token():
    """测试未登录状态登出"""
    # 应返回401
```

---

### 2.2 用户管理模块 ⚠️ **部分完成**
**文件**: `tests/test_api/test_user_manual.py`

**已实现的测试**:
- ✅ 用户创建基础测试

**待补充的测试用例**:

#### 2.2.1 用户CRUD ❌
```python
async def test_create_user_success():
    """测试创建用户成功"""
    response = await client.post("/api/v1/users", 
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "username": "testuser",
            "password": "Test@123456",
            "email": "test@example.com",
            "user_type": 2,
            "status": 1
        }
    )
    assert response.status_code == 200
    user = response.json()["data"]
    
    # 验证Snowflake ID生成
    assert len(str(user["id"])) >= 18
    # 验证密码已加密（不返回密码）
    assert "password" not in user

async def test_create_user_duplicate_username():
    """测试重复用户名"""
    # 创建用户A
    # 再次创建用户名相同的用户B
    # 应返回400

async def test_create_user_duplicate_email():
    """测试重复邮箱"""
    # 应返回400

async def test_create_user_weak_password():
    """测试弱密码"""
    response = await client.post("/api/v1/users",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "username": "testuser",
            "password": "123456",  # 弱密码
            "email": "test@example.com"
        }
    )
    assert response.status_code == 422  # 验证错误

async def test_list_users_pagination():
    """测试用户列表分页"""
    # 创建20个用户
    # 请求第1页，每页10条
    # 验证返回10条
    # 请求第2页
    # 验证返回10条

async def test_list_users_filter_by_status():
    """测试按状态过滤"""
    # 创建启用和禁用用户
    # 过滤status=1
    # 验证只返回启用用户

async def test_list_users_search_by_keyword():
    """测试关键字搜索"""
    # 创建用户: alice, bob, charlie
    # 搜索"ali"
    # 应只返回alice

async def test_update_user_success():
    """测试更新用户"""
    # 更新用户名、邮箱
    # 验证更新成功

async def test_update_user_not_found():
    """测试更新不存在的用户"""
    # 应返回404

async def test_delete_user_soft_delete():
    """测试软删除用户"""
    # 删除用户
    # 验证is_deleted=True
    # 用户列表中不再显示

async def test_delete_user_not_found():
    """测试删除不存在的用户"""
    # 应返回404
```

#### 2.2.2 密码管理 ❌
```python
async def test_reset_password_by_admin():
    """测试管理员重置密码"""
    # 管理员重置用户密码
    # 验证密码已更改
    # 用户使用新密码登录成功

async def test_reset_password_without_permission():
    """测试无权限重置密码"""
    # 普通用户尝试重置他人密码
    # 应返回403

async def test_change_own_password():
    """测试修改个人密码"""
    # 提供旧密码和新密码
    # 验证旧密码正确
    # 验证新密码强度
    # 更新成功

async def test_change_password_wrong_old_password():
    """测试旧密码错误"""
    # 应返回400

async def test_change_password_weak_new_password():
    """测试新密码强度不足"""
    # 应返回422
```

---

### 2.3 角色管理模块 ❌ **未完成**
**文件**: `tests/test_api/test_roles.py` (待创建)

**待实现的测试用例**:
```python
async def test_create_role_with_permissions():
    """测试创建角色并分配权限"""
    response = await client.post("/api/v1/roles",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "项目经理",
            "code": "PM",
            "data_scope": 2,
            "permission_ids": [1, 2, 6, 11]
        }
    )
    assert response.status_code == 200
    role = response.json()["data"]
    
    # 验证角色创建成功
    assert role["name"] == "项目经理"
    
    # 验证权限关联
    role_perms = await db.execute(
        select(RolePermission).where(RolePermission.role_id == role["id"])
    )
    assert len(list(role_perms.scalars().all())) == 4

async def test_create_role_invalid_permissions():
    """测试分配无效权限"""
    # permission_ids包含不存在的ID
    # 应返回400

async def test_update_role_permissions():
    """测试更新角色权限"""
    # 创建角色，权限[1,2,3]
    # 更新权限为[4,5,6]
    # 验证旧权限被删除
    # 验证新权限被添加

async def test_delete_role_with_users():
    """测试删除有用户的角色"""
    # 创建角色
    # 分配给用户
    # 尝试删除
    # 应返回400

async def test_delete_role_success():
    """测试删除角色成功"""
    # 创建未分配的角色
    # 删除成功
    # 验证is_deleted=True

async def test_get_permission_tree():
    """测试获取权限树"""
    response = await client.get("/api/v1/roles/permissions/tree",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    tree = response.json()["data"]
    
    # 验证树形结构
    assert isinstance(tree, list)
    # 验证有子节点
    if len(tree) > 0:
        assert "children" in tree[0]

async def test_list_roles():
    """测试角色列表"""
    # 验证返回所有角色
    # 验证排序正确

async def test_get_role_with_permissions():
    """测试获取角色详情（含权限）"""
    # 应返回角色信息和权限列表
```

---

### 2.4 部门管理模块 ❌ **未完成**
**文件**: `tests/test_api/test_departments.py` (待创建)

**待实现的测试用例**:
```python
async def test_create_department():
    """测试创建部门"""
    response = await client.post("/api/v1/departments",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "产品部",
            "code": "PRODUCT",
            "sort": 10
        }
    )
    assert response.status_code == 200

async def test_create_child_department():
    """测试创建子部门"""
    # 创建父部门
    # 创建子部门，指定parent_id
    # 验证parent_id正确

async def test_create_department_invalid_parent():
    """测试无效的父部门ID"""
    # parent_id不存在
    # 应返回400

async def test_get_department_tree():
    """测试获取部门树"""
    response = await client.get("/api/v1/departments/tree",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    tree = response.json()["data"]
    
    # 验证树形结构
    # 验证排序（按sort字段）

async def test_update_department():
    """测试更新部门"""
    # 更新部门名称
    # 验证更新成功

async def test_update_department_circular_reference():
    """测试防止循环引用"""
    # 部门A的parent_id设为自己
    # 应返回400

async def test_delete_department_with_children():
    """测试删除有子部门的部门"""
    # 创建父部门和子部门
    # 尝试删除父部门
    # 应返回400

async def test_delete_department_success():
    """测试删除部门成功"""
    # 删除无子部门的部门
    # 验证is_deleted=True

async def test_list_departments_flat():
    """测试平铺部门列表"""
    # 验证返回所有部门（非树形）
```

---

### 2.5 菜单管理模块 ❌ **未完成**
**文件**: `tests/test_api/test_menus.py` (待创建)

**待实现的测试用例**:
```python
async def test_get_user_menu_tree_superadmin():
    """测试超级管理员获取菜单树"""
    # 超级管理员应看到所有菜单
    
async def test_get_user_menu_tree_normal_user():
    """测试普通用户获取菜单树"""
    # 创建用户，分配部分权限
    # 只应看到有权限的菜单

async def test_menu_cache_hit():
    """测试菜单缓存命中"""
    # 第一次请求（缓存未命中）
    start1 = time.time()
    response1 = await client.get("/api/v1/menus/user")
    time1 = time.time() - start1
    
    # 第二次请求（缓存命中）
    start2 = time.time()
    response2 = await client.get("/api/v1/menus/user")
    time2 = time.time() - start2
    
    # 第二次应明显更快
    assert time2 < time1 * 0.5

async def test_menu_cache_ttl():
    """测试菜单缓存TTL"""
    # 请求菜单
    # 等待6分钟（超过5分钟TTL）
    # 再次请求
    # 验证缓存已过期，重新查询数据库

async def test_menu_permission_filter():
    """测试菜单权限过滤"""
    # 用户有user:list权限
    # 应看到"用户管理"菜单
    # 用户无role:list权限
    # 不应看到"角色管理"菜单

async def test_create_menu():
    """测试创建菜单"""
    
async def test_update_menu():
    """测试更新菜单"""
    
async def test_delete_menu():
    """测试删除菜单"""
```

---

### 2.6 权限控制测试 ❌ **未完成**
**文件**: `tests/test_api/test_permission_control.py` (待创建)

**待实现的测试用例**:
```python
async def test_require_permissions_with_permission():
    """测试有权限的用户访问"""
    # 用户有user:list权限
    # 访问需要user:list的端点
    # 应成功

async def test_require_permissions_without_permission():
    """测试无权限的用户访问"""
    # 用户无user:delete权限
    # 访问需要user:delete的端点
    # 应返回403

async def test_require_multiple_permissions():
    """测试需要多个权限（AND逻辑）"""
    # 端点需要user:list AND user:create
    # 用户只有user:list
    # 应返回403

async def test_require_any_permission():
    """测试需要任一权限（OR逻辑）"""
    # 端点需要user:list OR user:query
    # 用户有user:query
    # 应成功

async def test_require_roles():
    """测试角色装饰器"""
    # 用户有admin角色
    # 访问需要admin角色的端点
    # 应成功

async def test_superadmin_bypass_all_permissions():
    """测试超级管理员绕过所有权限检查"""
    # user_type=0的用户
    # 访问任何需要权限的端点
    # 都应成功

async def test_access_without_token():
    """测试无Token访问受保护端点"""
    # 不提供Authorization header
    # 应返回401

async def test_access_with_invalid_token():
    """测试无效Token"""
    # 提供错误的token
    # 应返回401

async def test_access_with_expired_token():
    """测试过期Token"""
    # 提供已过期的token
    # 应返回401
```

---

## 三、性能测试 (Performance Tests)

### 3.1 Snowflake ID 性能 ✅ **已完成**
**测试结果**: 1.2M+ IDs/秒

### 3.2 菜单缓存性能 ❌ **未完成**
**文件**: `tests/test_performance/test_menu_cache.py` (待创建)

```python
async def test_menu_query_performance_without_cache():
    """测试无缓存的菜单查询性能"""
    # 清空Redis缓存
    # 执行100次菜单查询
    # 记录平均响应时间

async def test_menu_query_performance_with_cache():
    """测试有缓存的菜单查询性能"""
    # 预热缓存
    # 执行100次菜单查询
    # 记录平均响应时间
    # 对比无缓存场景，应有显著提升

async def test_cache_memory_usage():
    """测试缓存内存占用"""
    # 缓存1000个用户的菜单
    # 检查Redis内存使用
```

### 3.3 并发登录测试 ❌ **未完成**
**文件**: `tests/test_performance/test_concurrent_operations.py` (待创建)

```python
async def test_concurrent_logins():
    """测试并发登录"""
    import asyncio
    
    async def login():
        response = await client.post("/api/v1/auth/login", json={
            "username": "testuser",
            "password": "Test@123456"
        })
        return response.status_code
    
    # 100个并发登录
    tasks = [login() for _ in range(100)]
    results = await asyncio.gather(*tasks)
    
    # 验证所有请求成功
    assert all(status == 200 for status in results)

async def test_concurrent_user_creation():
    """测试并发创建用户"""
    # 10个并发创建用户请求
    # 验证所有用户创建成功
    # 验证用户名唯一性约束生效

async def test_database_connection_pool():
    """测试数据库连接池"""
    # 发起超过连接池大小的并发请求
    # 验证请求排队等待
    # 验证所有请求最终成功
```

---

## 四、安全测试 (Security Tests)

### 4.1 SQL注入防护 ❌ **未完成**
**文件**: `tests/test_security/test_sql_injection.py` (待创建)

```python
async def test_sql_injection_in_username():
    """测试用户名SQL注入"""
    malicious_usernames = [
        "admin' OR '1'='1",
        "admin'; DROP TABLE users;--",
        "admin' UNION SELECT * FROM users--",
    ]
    
    for username in malicious_usernames:
        response = await client.post("/api/v1/auth/login", json={
            "username": username,
            "password": "password"
        })
        # 应安全处理，不应导致SQL注入
        assert response.status_code in [401, 422]

async def test_sql_injection_in_search():
    """测试搜索SQL注入"""
    # 在用户搜索中尝试注入
    # 应被参数化查询防护

async def test_sql_injection_in_filter():
    """测试过滤条件SQL注入"""
    # 在过滤参数中尝试注入
```

### 4.2 XSS防护 ❌ **未完成**
```python
async def test_xss_in_username():
    """测试用户名XSS"""
    response = await client.post("/api/v1/users", json={
        "username": "<script>alert('XSS')</script>",
        "password": "Test@123456",
        "email": "test@example.com"
    })
    # 应转义或拒绝
```

### 4.3 权限绕过测试 ❌ **未完成**
**文件**: `tests/test_security/test_permission_bypass.py` (待创建)

```python
async def test_access_other_tenant_data():
    """测试跨租户数据访问"""
    # 租户A的用户登录
    # 尝试访问租户B的数据
    # 应返回404或403

async def test_horizontal_privilege_escalation():
    """测试水平权限提升"""
    # 用户A尝试修改用户B的数据
    # 应返回403

async def test_vertical_privilege_escalation():
    """测试垂直权限提升"""
    # 普通用户尝试执行管理员操作
    # 应返回403

async def test_jwt_token_tampering():
    """测试JWT Token篡改"""
    # 修改token中的user_id
    # 应验证失败，返回401
```

---

## 五、端到端测试 (E2E Tests)

### 5.1 完整用户流程 ❌ **未完成**
**文件**: `tests/test_e2e/test_user_workflow.py` (待创建)

```python
async def test_complete_rbac_workflow():
    """测试完整RBAC工作流"""
    # 1. 管理员登录
    admin_response = await client.post("/api/v1/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    admin_token = admin_response.json()["data"]["access_token"]
    
    # 2. 创建部门
    dept_response = await client.post("/api/v1/departments",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"name": "测试部", "code": "TEST"}
    )
    dept_id = dept_response.json()["data"]["id"]
    
    # 3. 创建角色并分配权限
    role_response = await client.post("/api/v1/roles",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "测试角色",
            "code": "TESTER",
            "permission_ids": [1, 2]  # user:list, user:query
        }
    )
    role_id = role_response.json()["data"]["id"]
    
    # 4. 创建用户并分配角色
    user_response = await client.post("/api/v1/users",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "username": "testuser",
            "password": "Test@123456",
            "email": "test@example.com",
            "dept_id": dept_id,
            "role_ids": [role_id]
        }
    )
    
    # 5. 用户登录
    user_login = await client.post("/api/v1/auth/login", json={
        "username": "testuser",
        "password": "Test@123456"
    })
    user_token = user_login.json()["data"]["access_token"]
    
    # 6. 用户访问有权限的资源（user:list）
    list_response = await client.get("/api/v1/users",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert list_response.status_code == 200
    
    # 7. 用户访问无权限的资源（user:delete）
    delete_response = await client.delete("/api/v1/users/999",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert delete_response.status_code == 403
    
    # 8. 用户登出
    logout_response = await client.post("/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert logout_response.status_code == 200
    
    # 9. 使用旧token访问，应失败
    retry_response = await client.get("/api/v1/users",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert retry_response.status_code == 401

async def test_menu_permission_workflow():
    """测试菜单权限工作流"""
    # 创建用户，分配特定权限
    # 获取用户菜单树
    # 验证只显示有权限的菜单
```

---

## 六、测试覆盖率统计

### 当前覆盖率
- **Snowflake ID**: 100% ✅
- **密码策略**: ~30% ⚠️
- **认证授权**: ~20% ⚠️
- **用户管理**: ~10% ⚠️
- **角色管理**: 0% ❌
- **部门管理**: 0% ❌
- **菜单管理**: 0% ❌
- **权限控制**: 0% ❌

### 目标覆盖率
- **核心模块**: 80%+
- **业务逻辑**: 70%+
- **整体覆盖率**: 60%+

---

## 七、测试执行计划

### 优先级分配

**P0 (高优先级)** - 必须完成
- ✅ Snowflake ID测试
- ❌ 认证授权完整测试
- ❌ 权限控制测试
- ❌ 用户CRUD测试

**P1 (中优先级)** - 重要功能
- ❌ 角色管理测试
- ❌ 部门管理测试
- ❌ 菜单管理测试
- ❌ 密码管理测试

**P2 (低优先级)** - 辅助功能
- ❌ 性能测试
- ❌ 安全测试
- ❌ E2E测试

### 实施时间表

**第一阶段**（2天）
- Day 1: 认证授权测试 + 用户管理测试
- Day 2: 权限控制测试 + 密码管理测试

**第二阶段**（2天）
- Day 3: 角色管理测试 + 部门管理测试
- Day 4: 菜单管理测试

**第三阶段**（1天）
- Day 5: 性能测试 + 安全测试 + E2E测试

**第四阶段**（半天）
- 生成覆盖率报告
- 分析测试结果
- 优化测试用例

---

## 八、测试工具配置

### 8.1 pytest配置
**文件**: `pytest.ini`
```ini
[pytest]
asyncio_mode = auto
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --cov=app
    --cov-report=html
    --cov-report=term-missing
```

### 8.2 运行测试
```bash
# 运行所有测试
pytest

# 运行特定模块
pytest tests/test_api/test_auth.py

# 运行特定测试
pytest tests/test_api/test_auth.py::test_login_success

# 生成覆盖率报告
pytest --cov=app --cov-report=html

# 并行运行测试（需要pytest-xdist）
pytest -n auto

# 只运行失败的测试
pytest --lf

# 详细输出
pytest -vv
```

---

## 九、测试数据管理

### 9.1 测试数据库
- 使用独立的测试数据库
- 每次测试前清空数据
- 使用事务回滚保证测试隔离

### 9.2 Fixtures
**文件**: `tests/conftest.py`
```python
@pytest.fixture
async def test_db():
    """测试数据库会话"""
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()

@pytest.fixture
async def test_client():
    """测试HTTP客户端"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
async def admin_user(test_db):
    """测试管理员用户"""
    user = User(
        username="admin",
        password=get_password_hash("admin123"),
        user_type=0,
        tenant_id=0
    )
    test_db.add(user)
    await test_db.commit()
    return user

@pytest.fixture
async def admin_token(test_client, admin_user):
    """管理员Token"""
    response = await test_client.post("/api/v1/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    return response.json()["data"]["access_token"]
```

---

## 十、持续集成

### GitHub Actions配置
**文件**: `.github/workflows/test.yml`
```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      
      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-cov httpx
      
      - name: Run tests
        run: |
          pytest --cov=app --cov-report=xml
        env:
          DATABASE_URL: postgresql+asyncpg://postgres:postgres@localhost/test
          REDIS_URL: redis://localhost:6379/0
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

---

## 总结

### 测试完成度
- ✅ **已完成**: 1个模块（Snowflake ID）
- ⚠️ **部分完成**: 4个模块（密码策略、认证、用户、异常处理）
- ❌ **未完成**: 10+个测试套件

### 预计工作量
- **总测试用例数**: ~150个
- **已完成**: ~15个（10%）
- **待完成**: ~135个（90%）
- **预计时间**: 4-5天

### 下一步行动
1. 创建测试基础设施（conftest.py）
2. 实施P0优先级测试（认证、权限、用户）
3. 逐步完成P1、P2测试
4. 持续监控覆盖率，目标60%+
