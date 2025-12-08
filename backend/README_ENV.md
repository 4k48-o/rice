# 环境变量配置说明

## 快速开始

1. 复制示例配置文件：
```bash
cp .env.example .env
```

2. 编辑 `.env` 文件，填入你的实际配置值

3. 重要配置项说明：

### 必须配置的项

- `DATABASE_URL`: 数据库连接字符串
  - 格式: `postgresql+asyncpg://username:password@host:port/database`
  - 示例: `postgresql+asyncpg://postgres:your_password@localhost:5432/fast_andt_react_admin`

- `SECRET_KEY`: JWT 密钥（至少32个字符）
  - 生成方式: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
  - **生产环境必须修改！**

### 可选配置项

- `REDIS_PASSWORD`: Redis 密码（如果 Redis 设置了密码）
- `ADMIN_PASSWORD`: 初始化管理员密码（仅在首次初始化时使用）
- `APP_ENV`: 环境类型 (`development` | `production`)
- `DEBUG`: 调试模式 (`true` | `false`)

## 安全建议

1. **永远不要将 `.env` 文件提交到 Git**
2. **生产环境必须修改所有默认密码和密钥**
3. **使用强密码和随机生成的密钥**
4. **定期轮换密钥和密码**

## 生成安全密钥

```bash
# 生成 SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# 生成随机密码
python -c "import secrets; print(secrets.token_urlsafe(16))"
```

