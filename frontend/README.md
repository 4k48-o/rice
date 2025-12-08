# FastAndt React Admin 前端

基于 React + TypeScript + Ant Design 构建的多租户企业管理系统前端应用。

## 技术栈

- **框架**: React 18+
- **构建工具**: Vite
- **语言**: TypeScript
- **UI组件库**: Ant Design 5.x
- **路由**: React Router v6
- **状态管理**: Zustand
- **HTTP客户端**: Axios
- **国际化**: react-i18next

## 快速开始

### 安装依赖

```bash
npm install
```

### 开发环境运行

```bash
npm run dev
```

应用将在 http://localhost:3000 启动。

### 构建生产版本

```bash
npm run build
```

### 预览生产构建

```bash
npm run preview
```

## 项目结构

```
frontend/
├── public/              # 静态资源
├── src/
│   ├── api/            # API接口封装
│   ├── components/     # 公共组件
│   │   ├── Layout/     # 布局组件
│   │   ├── Permission/ # 权限控制组件
│   │   └── ...
│   ├── hooks/          # 自定义Hooks
│   ├── locales/         # 国际化资源
│   ├── pages/          # 页面组件
│   │   ├── Login/      # 登录页
│   │   ├── User/       # 用户管理
│   │   └── Department/ # 部门管理
│   ├── routes/         # 路由配置
│   ├── store/          # 状态管理
│   ├── types/          # TypeScript类型定义
│   ├── utils/          # 工具函数
│   ├── App.tsx         # 主应用组件
│   └── index.tsx       # 应用入口
├── .eslintrc.json      # ESLint配置
├── .prettierrc         # Prettier配置
├── tsconfig.json        # TypeScript配置
├── vite.config.ts       # Vite配置
└── package.json         # 项目配置
```

## 功能特性

### 已实现功能

1. **认证授权模块**
   - 用户登录/退出
   - Token管理
   - 路由守卫
   - 权限检查

2. **用户管理模块**
   - 用户列表（分页、搜索、筛选）
   - 创建/编辑用户
   - 删除用户
   - 重置密码

3. **部门管理模块**
   - 部门树形展示
   - 创建/编辑部门
   - 删除部门

4. **国际化支持**
   - 中文、英文、日文
   - 语言切换

5. **权限控制**
   - 路由级权限
   - 按钮级权限
   - 权限组件封装

## 开发规范

### 代码规范

- 使用TypeScript严格模式
- 组件使用函数式组件 + Hooks
- 遵循React Hooks最佳实践
- 使用ESLint和Prettier统一代码风格

### 命名规范

- 组件文件：PascalCase（如`UserList.tsx`）
- 工具文件：camelCase（如`formatDate.ts`）
- 常量文件：UPPER_SNAKE_CASE

## API配置

前端默认通过Vite代理访问后端API：

- 开发环境：`http://localhost:8000`
- 生产环境：需要配置环境变量或修改`vite.config.ts`中的代理设置

## 环境变量

创建`.env`文件配置环境变量：

```env
VITE_API_BASE_URL=http://localhost:8000
```

## 参考文档

- [API接口设计文档](../backend/API_DESIGN.md)
- [数据库设计文档](../backend/DATABASE_DESIGN.md)
- [架构设计文档](../ARCHITECTURE_OPTIMIZED.md)

