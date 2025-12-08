/**
 * 用户管理API
 */
import request from './request';
import { ApiResponse, PageResponse } from '@/types/api';
import { User, UserCreate, UserUpdate, UserListParams } from '@/types/user';

/**
 * 获取用户列表
 */
export function getUserList(params: UserListParams): Promise<ApiResponse<PageResponse<User>>> {
  return request.get('/users', { params });
}

/**
 * 获取用户详情
 */
export function getUserDetail(id: number): Promise<ApiResponse<User>> {
  return request.get(`/users/${id}`);
}

/**
 * 获取用户角色
 */
export function getUserRoles(id: number): Promise<ApiResponse<Array<{ id: number; name: string; code: string }>>> {
  return request.get(`/users/${id}/roles`);
}

/**
 * 创建用户
 */
export function createUser(data: UserCreate): Promise<ApiResponse<{ id: number }>> {
  return request.post('/users', data);
}

/**
 * 更新用户
 */
export function updateUser(id: number, data: UserUpdate): Promise<ApiResponse<null>> {
  return request.put(`/users/${id}`, data);
}

/**
 * 删除用户
 */
export function deleteUser(id: number): Promise<ApiResponse<null>> {
  return request.delete(`/users/${id}`);
}

/**
 * 重置用户密码
 */
export function resetUserPassword(id: number, password: string): Promise<ApiResponse<null>> {
  return request.post(`/users/${id}/reset-password`, { password });
}

