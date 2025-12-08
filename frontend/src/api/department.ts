/**
 * 部门管理API
 */
import request from './request';
import { ApiResponse } from '@/types/api';
import { Department, DepartmentCreate, DepartmentUpdate } from '@/types/department';

/**
 * 获取部门树
 */
export function getDepartmentTree(): Promise<ApiResponse<Department[]>> {
  return request.get('/departments/tree');
}

/**
 * 获取部门列表
 */
export function getDepartmentList(params?: { keyword?: string; status?: number }): Promise<ApiResponse<Department[]>> {
  return request.get('/departments', { params });
}

/**
 * 获取部门详情
 */
export function getDepartmentDetail(id: number): Promise<ApiResponse<Department>> {
  return request.get(`/departments/${id}`);
}

/**
 * 创建部门
 */
export function createDepartment(data: DepartmentCreate): Promise<ApiResponse<{ id: number }>> {
  return request.post('/departments', data);
}

/**
 * 更新部门
 */
export function updateDepartment(id: number | string, data: DepartmentUpdate): Promise<ApiResponse<null>> {
  return request.put(`/departments/${id}`, data);
}

/**
 * 删除部门
 */
export function deleteDepartment(id: number | string): Promise<ApiResponse<null>> {
  return request.delete(`/departments/${id}`);
}

