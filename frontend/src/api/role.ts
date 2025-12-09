/**
 * 角色管理API
 */
import request from './request';
import { ApiResponse } from '@/types/api';
import { Role, RoleCreate, RoleUpdate, RoleListParams, PermissionTreeNode } from '@/types/role';

/**
 * 获取角色列表
 */
export function getRoleList(params?: RoleListParams): Promise<ApiResponse<Role[]>> {
  return request.get('/roles', { params });
}

/**
 * 获取角色详情（包含权限）
 */
export function getRoleDetail(id: string): Promise<ApiResponse<Role & { permissions: PermissionTreeNode[] }>> {
  return request.get(`/roles/${id}`);
}

/**
 * 获取权限树
 */
export function getPermissionTree(): Promise<ApiResponse<PermissionTreeNode[]>> {
  return request.get('/roles/permissions/tree');
}

/**
 * 创建角色
 */
export function createRole(data: RoleCreate): Promise<ApiResponse<Role>> {
  return request.post('/roles', data);
}

/**
 * 更新角色
 */
export function updateRole(id: string, data: RoleUpdate): Promise<ApiResponse<Role>> {
  return request.put(`/roles/${id}`, data);
}

/**
 * 删除角色
 */
export function deleteRole(id: string): Promise<ApiResponse<null>> {
  return request.delete(`/roles/${id}`);
}

