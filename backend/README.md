# FastAndtAdmin Backend

多租户企业管理系统后端 API 服务

## 技术栈

- **框架**: FastAPI 0.109+
- **Python**: 3.10+
- **数据库**: PostgreSQL 15+ (异步)
- **ORM**: SQLAlchemy 2.0 (Async)
- **认证**: JWT (python-jose)
- **密码**: bcrypt (passlib)
- **缓存**: Redis 7
- **数据验证**: Pydantic v2
- **国际化**: Support zh, en, ja

## 主要特性

### 1. 安全增强
- **密码策略**: 强制复杂度(大小写/数字/特殊字符)、8位最小长度、定期过期(默认30天)
- **单点登录**: Redis强制单会户在线,新登录踢出旧登录
- **JWT认证**: 标准Bear Token流程,支持Refresh Token

### 2. 用户管理
- 完整的CRUD操作
- 基于角色的权限控制基础
- 多语言支持 (I18n)


## 快速开始

### 1. 环境要求

- Python 3.10 或更高版本
- PostgreSQL 15+
- Redis 7+

### 2. 安装依赖

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件,配置数据库连接等信息
# 必须修改的配置:
# - DATABASE_URL: PostgreSQL连接字符串
# - SECRET_KEY: JWT密钥(生成随机字符串)
# - SECRET_KEY: JWT密钥(生成随机字符串)
# - REDIS_URL: Redis连接字符串
# - REDIS_PASSWORD: Redis密码(如需要)
# - SINGLE_SESSION_MODE: 是否开启单点登录(True/False)

```

### 4. 初始化数据库

```bash
# 使用Alembic创建数据库表
alembic upgrade head

# 或者运行初始化脚本
python scripts/init_db.py
```

### 5. 启动服务

```bash
# 开发模式(自动重载)
uvicorn app.main:app --reload --port 8000

# 或者直接运行
python app/main.py
```

### 6. 访问API文档

启动后访问:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

## 项目结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI应用入口
│   ├── core/                      # 核心配置
│   │   ├── config.py              # 配置管理
│   │   ├── security.py            # JWT、密码加密
│   │   └── database.py            # 数据库连接
│   ├── models/                    # SQLAlchemy模型
│   │   ├── base.py                # 基础模型
│   │   └── user.py                # 用户模型
│   ├── schemas/                   # Pydantic schemas
│   │   ├── common.py              # 通用响应
│   │   └── auth.py                # 认证schemas
│   ├── api/                       # API路由
│   │   ├── deps.py                # 依赖注入
│   │   └── v1/
│   │       └── auth.py            # 认证接口
│   ├── services/                  # 业务逻辑层
│   ├── middleware/                # 中间件
│   └── utils/                     # 工具函数
├── tests/                         # 测试
├── alembic/                       # 数据库迁移
├── scripts/                       # 脚本
├── .env.example                   # 环境变量模板
├── requirements.txt               # 依赖
└── README.md                      # 本文件
```

## 开发指南

### 代码规范

```bash
# 代码格式化
black app/

# 代码检查
ruff check app/

# 类型检查
mypy app/
```

### 数据库迁移

```bash
# 创建迁移
alembic revision --autogenerate -m "description"

# 执行迁移
alembic upgrade head

# 回滚
alembic downgrade -1
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_api/test_auth.py

# 生成覆盖率报告
pytest --cov=app tests/
```

## API设计

### 响应格式

成功响应:
```json
{
  "code": 200,
  "message": "success",
  "data": {...},
  "timestamp": 1701936000
}
```

分页响应:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [...],
    "total": 100,
    "page": 1,
    "page_size": 20,
    "total_pages": 5
  },
  "timestamp": 1701936000
}
```

错误响应:
```json
{
  "code": 400,
  "message": "参数错误",
  "data": null,
  "errors": [
    {"field": "username", "message": "用户名不能为空"}
  ],
  "timestamp": 1701936000
}
```

### 认证

所有需要认证的接口都需要在请求头中携带JWT token:

```
Authorization: Bearer <access_token>
```

### 多租户

多租户请求需要在请求头中携带租户ID:

```
X-Tenant-ID: 1001
```

## 部署

### Docker部署

```bash
# 构建镜像
docker build -t fast-andt-admin-backend .

# 运行容器
docker run -d \
  -p 8000:8000 \
  --env-file .env \
  --name backend \
  fast-andt-admin-backend
```

### 生产环境

```bash
# 使用gunicorn + uvicorn workers
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

## 相关文档

- [API接口文档](../API_DESIGN.md)
- [数据库设计文档](../DATABASE_DESIGN.md)
- [架构设计文档](../DETAILED_ARCHITECTURE_DESIGN.md)
- [开发计划](./DEVELOPMENT_PLAN.md)

## 许可证

MIT License
