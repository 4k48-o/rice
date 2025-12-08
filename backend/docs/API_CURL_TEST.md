# API 测试文档 (Curl 命令指南)

本文档提供了测试后端 API 的 `curl` 命令示例。
**前提条件**: 确保后端服务正在运行 (默认 `http://localhost:8000`)。

## 1. 认证模块 (Authentication)

### 1.1 登录 (Login)
获取 Access Token 和 Refresh Token。

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/json" \
     -d '{
           "username": "admin",
           "password": "admin123"
         }'

### 1.1.1 国际化测试 (I18n)
支持 `zh`, `en`, `ja`。

**英文 (English)**:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login?lang=en" \
     -H "Content-Type: application/json" \
     -d '{"username": "wrong", "password": "wrong"}'
```

**日文 (Japanese)**:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Accept-Language: ja" \
     -H "Content-Type: application/json" \
     -d '{"username": "wrong", "password": "wrong"}'
```
```

**响应示例**:
```json
{
  "code": 200,
  "message": "Login success",
  "data": {
    "access_token": "eyJhbG...",
    "refresh_token": "eyJhbG...",
    "token_type": "Bearer",
    ...
  }
}
```

> **注意**: 请复制响应中的 `access_token`，在后续请求中替换 `<YOUR_ACCESS_TOKEN>`。

### 1.2 获取当前用户信息 (Get User Info)
需要 `Authorization` 头。

```bash
curl -X GET "http://localhost:8000/api/v1/auth/user-info" \
     -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>"
```

### 1.3 刷新 Token (Refresh Token)
使用 `refresh_token` 获取新的 `access_token`。请替换 `<YOUR_REFRESH_TOKEN>`。

```bash
# 注意: refresh_token 可以放在 query 参数中
curl -X POST "http://localhost:8000/api/v1/auth/refresh?refresh_token=<YOUR_REFRESH_TOKEN>" \
     -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>"
```

---

## 2. 用户管理模块 (User Management)

**注意**: 以下所有接口都需要 `Authorization: Bearer <YOUR_ACCESS_TOKEN>`。

### 2.1 创建用户 (Create User)

```bash
curl -X POST "http://localhost:8000/api/v1/users" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>" \
     -d '{
           "username": "test_user_01",
           "password": "password123",
           "real_name": "测试用户01",
           "role_ids": []
         }'
```

### 2.2 获取用户列表 (List Users)
支持分页和筛选。

```bash
curl -X GET "http://localhost:8000/api/v1/users?page=1&page_size=10&username=test" \
     -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>"
```

### 2.3 更新用户 (Update User)
替换 `<USER_ID>` (例如 `2`)。

```bash
curl -X PUT "http://localhost:8000/api/v1/users/<USER_ID>" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>" \
     -d '{
           "nickname": "Updated Nickname",
           "status": 1
         }'
```

### 2.4 重置用户密码 (Reset Password)
管理员强制重置用户密码。替换 `<USER_ID>`。

```bash
curl -X POST "http://localhost:8000/api/v1/users/<USER_ID>/reset-password" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>" \
     -d '{
           "password": "NewStrongPassword123!"
         }'
```

### 2.5 删除用户 (Delete User)
软删除用户。替换 `<USER_ID>`。

```bash
curl -X DELETE "http://localhost:8000/api/v1/users/<USER_ID>" \
     -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>"
```
