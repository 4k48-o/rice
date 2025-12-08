/**
 * 权限控制组件
 */
import { ReactNode } from 'react';
import { usePermission } from '@/hooks/usePermission';

interface PermissionProps {
  permission?: string | string[];
  requireAll?: boolean;
  children: ReactNode;
  fallback?: ReactNode;
}

export function Permission({ permission, requireAll = false, children, fallback = null }: PermissionProps) {
  const { checkPermission, checkAnyPermission, checkAllPermissions } = usePermission();

  if (!permission) {
    return <>{children}</>;
  }

  let hasAccess = false;

  if (Array.isArray(permission)) {
    hasAccess = requireAll ? checkAllPermissions(permission) : checkAnyPermission(permission);
  } else {
    hasAccess = checkPermission(permission);
  }

  return hasAccess ? <>{children}</> : <>{fallback}</>;
}

