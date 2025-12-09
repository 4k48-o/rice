/**
 * 路由配置
 */
import { createBrowserRouter, Navigate, Outlet } from 'react-router-dom';
import { useAuthStore } from '@/store/authStore';
import { useTranslation } from 'react-i18next';
import Login from '@/pages/Login/Login';
import MainLayout from '@/components/Layout/MainLayout';
import UserList from '@/pages/User/UserList';
import DepartmentList from '@/pages/Department/DepartmentList';
import { RoleList } from '@/pages/Role';
import { MenuList } from '@/pages/Menu';
import { DictList } from '@/pages/Dict';
import { OnlineUser, LoginLog } from '@/pages/Monitor';

// 路由守卫组件
function ProtectedRoute() {
  const { isAuthenticated, token } = useAuthStore();

  if (!isAuthenticated && !token) {
    return <Navigate to="/login" replace />;
  }

  return <Outlet />;
}

// 首页组件
function HomePage() {
  const { t } = useTranslation();
  return <div>{t('home.home')}</div>;
}

// 创建路由配置
export const router = createBrowserRouter([
  {
    path: '/login',
    element: <Login />,
  },
  {
    element: <ProtectedRoute />,
    children: [
      {
        path: '/',
        element: (
          <MainLayout>
            <HomePage />
          </MainLayout>
        ),
      },
      // 系统管理
      {
        path: '/system/user',
        element: (
          <MainLayout>
            <UserList />
          </MainLayout>
        ),
      },
      {
        path: '/system/role',
        element: (
          <MainLayout>
            <RoleList />
          </MainLayout>
        ),
      },
      {
        path: '/system/menu',
        element: (
          <MainLayout>
            <MenuList />
          </MainLayout>
        ),
      },
      {
        path: '/system/dept',
        element: (
          <MainLayout>
            <DepartmentList />
          </MainLayout>
        ),
      },
      {
        path: '/system/dict',
        element: (
          <MainLayout>
            <DictList />
          </MainLayout>
        ),
      },
      // 系统监控
      {
        path: '/monitor/online',
        element: (
          <MainLayout>
            <OnlineUser />
          </MainLayout>
        ),
      },
      {
        path: '/monitor/loginlog',
        element: (
          <MainLayout>
            <LoginLog />
          </MainLayout>
        ),
      },
      // 兼容旧路由
      {
        path: '/users',
        element: (
          <MainLayout>
            <UserList />
          </MainLayout>
        ),
      },
      {
        path: '/departments',
        element: (
          <MainLayout>
            <DepartmentList />
          </MainLayout>
        ),
      },
    ],
  },
  {
    path: '*',
    element: <Navigate to="/" replace />,
  },
]);

