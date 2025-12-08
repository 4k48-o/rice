/**
 * 权限检查工具函数
 */

import { storage } from './storage';

/**
 * 检查用户是否拥有指定权限
 * @param permission 权限码
 * @returns 是否拥有权限
 */
export function hasPermission(permission: string): boolean {
  const userInfo = storage.getUserInfo();
  if (!userInfo) {
    return false;
  }

  // 超级管理员拥有所有权限
  if (userInfo.user_type === 0) {
    return true;
  }

  const permissions = userInfo.permissions || [];
  
  // 检查是否有通配符权限
  if (permissions.includes('*:*:*')) {
    return true;
  }

  // 精确匹配
  if (permissions.includes(permission)) {
    return true;
  }

  // 支持通配符匹配，如 user:* 匹配所有 user: 开头的权限
  const wildcardPermissions = permissions.filter((p: string) => p.endsWith(':*'));
  for (const wildcard of wildcardPermissions) {
    const prefix = wildcard.replace(':*', '');
    if (permission.startsWith(prefix + ':')) {
      return true;
    }
  }

  return false;
}

/**
 * 检查用户是否拥有任一权限
 * @param permissions 权限码数组
 * @returns 是否拥有任一权限
 */
export function hasAnyPermission(permissions: string[]): boolean {
  return permissions.some(permission => hasPermission(permission));
}

/**
 * 检查用户是否拥有所有权限
 * @param permissions 权限码数组
 * @returns 是否拥有所有权限
 */
export function hasAllPermissions(permissions: string[]): boolean {
  return permissions.every(permission => hasPermission(permission));
}

