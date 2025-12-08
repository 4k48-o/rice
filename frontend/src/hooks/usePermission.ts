/**
 * 权限相关Hooks
 */
import { useAuthStore } from '@/store/authStore';
import { hasPermission, hasAnyPermission, hasAllPermissions } from '@/utils/permission';

/**
 * 权限检查Hook
 */
export function usePermission() {
  const { userInfo, permissions } = useAuthStore();

  /**
   * 检查是否拥有指定权限
   */
  const checkPermission = (permission: string): boolean => {
    if (!userInfo) return false;
    
    // 超级管理员拥有所有权限
    if (userInfo.user_type === 0) {
      return true;
    }

    return hasPermission(permission);
  };

  /**
   * 检查是否拥有任一权限
   */
  const checkAnyPermission = (perms: string[]): boolean => {
    if (!userInfo) return false;
    if (userInfo.user_type === 0) return true;
    return hasAnyPermission(perms);
  };

  /**
   * 检查是否拥有所有权限
   */
  const checkAllPermissions = (perms: string[]): boolean => {
    if (!userInfo) return false;
    if (userInfo.user_type === 0) return true;
    return hasAllPermissions(perms);
  };

  return {
    checkPermission,
    checkAnyPermission,
    checkAllPermissions,
    permissions,
  };
}

