/**
 * 主布局组件
 */
import { useState, useEffect, useMemo } from 'react';
import { Layout, Menu, Avatar, Dropdown, Space, Button } from 'antd';
import {
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  UserOutlined,
  LogoutOutlined,
  GlobalOutlined,
  SettingOutlined,
  TeamOutlined,
  MenuOutlined,
  ApartmentOutlined,
  MonitorOutlined,
  SwapOutlined,
  FileTextOutlined,
} from '@ant-design/icons';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import { useAuthStore } from '@/store/authStore';
import { getUserMenuTree } from '@/api/auth';
import { useTranslation } from 'react-i18next';
import type { MenuProps } from 'antd';

const { Header, Sider, Content } = Layout;

interface MainLayoutProps {
  children: React.ReactNode;
}

export default function MainLayout({ children }: MainLayoutProps) {
  const [collapsed, setCollapsed] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const { logout, userInfo, token } = useAuth();
  const { menus, setMenus } = useAuthStore();
  const { t, i18n } = useTranslation();

  // 如果菜单为空且有token，尝试加载菜单（作为备用方案）
  useEffect(() => {
    const loadMenusIfNeeded = async () => {
      if (token && (!menus || menus.length === 0)) {
        try {
          const menuResponse = await getUserMenuTree();
          if (menuResponse && menuResponse.length > 0) {
            setMenus(menuResponse);
          }
        } catch (error) {
          console.error('Failed to load menus in MainLayout:', error);
        }
      }
    };

    loadMenusIfNeeded();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  // 图标映射
  const getIcon = (iconName?: string) => {
    if (!iconName) return null;
    
    // Ant Design Icons映射
    const iconMap: Record<string, React.ReactNode> = {
      setting: <SettingOutlined />,
      user: <UserOutlined />,
      team: <TeamOutlined />,
      menu: <MenuOutlined />,
      apartment: <ApartmentOutlined />,
      monitor: <MonitorOutlined />,
      'user-switch': <SwapOutlined />,
      'file-text': <FileTextOutlined />,
    };
    
    return iconMap[iconName] || null;
  };

  // 根据菜单路径或权限码获取国际化标题
  const getMenuTitle = (menu: any): string => {
    // 优先使用后端返回的 title，但尝试通过 path 或 permission_code 进行国际化
    const path = menu.path || '';
    const permissionCode = menu.permission_code || '';
    
    // 根据路径或权限码映射到国际化 key
    const menuKeyMap: Record<string, string> = {
      '/system': 'menu.systemManagement',
      '/system/user': 'user.userManagement',
      '/system/role': 'role.roleManagement',
      '/system/menu': 'menu.menuManagement',
      '/system/dept': 'department.departmentManagement',
      '/system/dict': 'dict.typeManagement',
      '/monitor': 'menu.monitor',
      '/monitor/online': 'monitor.onlineUsers',
      '/monitor/loginlog': 'monitor.loginLog',
      'user:list': 'user.userManagement',
      'role:list': 'role.roleManagement',
      'menu:list': 'menu.menuManagement',
      'dept:list': 'department.departmentManagement',
      'dict:list': 'dict.typeManagement',
      'monitor:online': 'monitor.onlineUsers',
      'monitor:loginlog': 'monitor.loginLog',
    };
    
    // 尝试通过路径或权限码获取翻译 key
    const translationKey = menuKeyMap[path] || menuKeyMap[permissionCode];
    if (translationKey) {
      const translated = t(translationKey);
      // 如果翻译成功（返回的不是 key 本身），使用翻译结果
      if (translated && translated !== translationKey) {
        return translated;
      }
    }
    
    // 如果没有找到翻译，使用后端返回的 title
    return menu.title || menu.name || `菜单${menu.id}`;
  };

  // 转换菜单数据为Ant Design Menu格式
  const convertMenusToItems = (menuList: any[]): MenuProps['items'] => {
    if (!menuList || menuList.length === 0) return [];
    
    return menuList
      .filter((menu) => {
        // 只显示目录和菜单类型，不显示按钮
        if (menu.type === 3) return false;
        // 只显示可见且启用的菜单
        return (menu.visible === undefined || menu.visible !== 0) && 
               (menu.status === undefined || menu.status === 1);
      })
      .map((menu) => {
        const item: any = {
          key: menu.path || menu.id.toString(),
          icon: getIcon(menu.icon),
          label: getMenuTitle(menu),
        };

        if (menu.children && menu.children.length > 0) {
          item.children = convertMenusToItems(menu.children);
        }

        return item;
      });
  };

  // 当语言切换时，menuItems 会重新计算（依赖 i18n.language）
  const menuItems: MenuProps['items'] = useMemo(() => {
    return convertMenusToItems(menus);
  }, [menus, i18n.language, t]);

  const handleMenuClick = ({ key }: { key: string }) => {
    if (key && key.startsWith('/')) {
      navigate(key);
    }
  };

  const handleLanguageChange = (lang: string) => {
    i18n.changeLanguage(lang);
    localStorage.setItem('language', lang);
  };

  const userMenuItems: MenuProps['items'] = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: t('common.profile'),
    },
    {
      type: 'divider',
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: t('auth.logout'),
      onClick: logout,
    },
  ];

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider trigger={null} collapsible collapsed={collapsed}>
        <div className="logo" style={{ height: 32, margin: 16, background: 'rgba(255, 255, 255, 0.3)' }} />
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={handleMenuClick}
        />
      </Sider>
      <Layout>
        <Header style={{ padding: 0, background: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Button
            type="text"
            icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
            onClick={() => setCollapsed(!collapsed)}
            style={{ fontSize: '16px', width: 64, height: 64 }}
          />
          <Space style={{ marginRight: 16 }}>
            <Dropdown
              menu={{
                items: [
                  { key: 'zh', label: t('common.chinese'), onClick: () => handleLanguageChange('zh') },
                  { key: 'en', label: t('common.english'), onClick: () => handleLanguageChange('en') },
                  { key: 'ja', label: t('common.japanese'), onClick: () => handleLanguageChange('ja') },
                ],
              }}
            >
              <Button type="text" icon={<GlobalOutlined />} />
            </Dropdown>
            <Dropdown menu={{ items: userMenuItems }}>
              <Space style={{ cursor: 'pointer' }}>
                <Avatar icon={<UserOutlined />} />
                <span>{userInfo?.real_name || userInfo?.username}</span>
              </Space>
            </Dropdown>
          </Space>
        </Header>
        <Content style={{ margin: '24px 16px', padding: 24, background: '#fff', minHeight: 280 }}>
          {children}
        </Content>
      </Layout>
    </Layout>
  );
}

