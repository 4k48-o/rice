/**
 * 认证相关Hooks
 */
import { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '@/store/authStore';
import { login, getUserInfo, getUserMenuTree } from '@/api/auth';
import { LoginRequest } from '@/types/auth';
import { message } from 'antd';
import i18n from '@/i18n';

export function useAuth() {
  const navigate = useNavigate();
  const location = useLocation();
  const { token, userInfo, menus, setToken, setRefreshToken, setUserInfo, setPermissions, setMenus, clearAuth, isAuthenticated } = useAuthStore();

  /**
   * 登录
   */
  const handleLogin = async (loginData: LoginRequest) => {
    try {
      const response = await login(loginData);
      const { access_token, refresh_token, user_info } = response.data;

      setToken(access_token);
      setRefreshToken(refresh_token);
      
      if (user_info) {
        // 后端返回的user_info可能不包含permissions，需要单独获取
        const userInfoData: any = {
          id: user_info.id,
          username: user_info.username,
          real_name: user_info.real_name,
          avatar: user_info.avatar,
          user_type: user_info.user_type || 0,
        };
        setUserInfo(userInfoData);
        // permissions需要从user_info中获取，如果没有则设为空数组
        setPermissions(user_info.permissions || []);
      }

      // 获取用户菜单
      try {
        const menuResponse = await getUserMenuTree();
        setMenus(menuResponse || []);
      } catch (error) {
        console.error('Failed to load menus:', error);
        // 菜单加载失败不影响登录
      }

      message.success(i18n.t('auth.loginSuccess'));
      navigate('/');
    } catch (error: any) {
      // 优先使用拦截器附加的错误消息，其次使用响应数据中的消息，最后使用默认消息
      const errorMessage = error.errorMessage || error.response?.data?.message || error.response?.data?.detail || error.message || i18n.t('auth.loginFailed');
      message.error(errorMessage);
      throw error;
    }
  };

  /**
   * 退出登录
   */
  const handleLogout = async () => {
    try {
      // 调用退出接口
      // await logout();
      clearAuth();
      message.success(i18n.t('auth.logoutSuccess'));
      navigate('/login');
    } catch (error) {
      // 即使接口失败也清除本地状态
      clearAuth();
      navigate('/login');
    }
  };

  /**
   * 检查登录状态并加载菜单
   */
  useEffect(() => {
    // 如果是登录页面，不执行初始化
    if (location.pathname === '/login') {
      return;
    }

    const initAuth = async () => {
      if (token) {
        // 如果有token但没有用户信息，尝试获取
        if (!userInfo) {
          try {
            const response = await getUserInfo();
            setUserInfo(response.data);
            setPermissions(response.data.permissions || []);
          } catch (error) {
            clearAuth();
            return;
          }
        }
        
        // 如果有token但没有菜单，尝试加载菜单
        // 直接从store获取当前菜单状态，避免闭包问题
        const currentMenus = useAuthStore.getState().menus;
        if (!currentMenus || currentMenus.length === 0) {
          try {
            const menuResponse = await getUserMenuTree();
            if (menuResponse && menuResponse.length > 0) {
              setMenus(menuResponse);
            }
          } catch (error) {
            console.error('Failed to load menus:', error);
            // 菜单加载失败不影响使用，只记录错误
          }
        }
      }
    };

    initAuth();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, location.pathname]);

  return {
    isAuthenticated,
    userInfo,
    token,
    login: handleLogin,
    logout: handleLogout,
  };
}

