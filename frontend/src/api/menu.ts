/**
 * 菜单管理API
 */
import request from './request';
import { ApiResponse, PageResponse } from '@/types/api';
import { Menu, MenuCreate, MenuUpdate, MenuListParams } from '@/types/menu';

/**
 * 获取菜单列表
 */
export function getMenuList(params: MenuListParams): Promise<ApiResponse<PageResponse<Menu>>> {
  return request.get('/menus', { params });
}

/**
 * 获取完整菜单树（管理员用）
 */
export function getMenuTree(): Promise<ApiResponse<Menu[]>> {
  return request.get('/menus/tree/all');
}

/**
 * 获取用户菜单树
 */
export function getUserMenuTree(): Promise<ApiResponse<Menu[]>> {
  return request.get('/menus/user');
}

/**
 * 获取菜单详情
 */
export function getMenuDetail(id: string): Promise<ApiResponse<Menu>> {
  return request.get(`/menus/${id}`);
}

/**
 * 创建菜单
 */
export function createMenu(data: MenuCreate): Promise<ApiResponse<Menu>> {
  return request.post('/menus', data);
}

/**
 * 更新菜单
 */
export function updateMenu(id: string, data: MenuUpdate): Promise<ApiResponse<Menu>> {
  return request.put(`/menus/${id}`, data);
}

/**
 * 删除菜单
 */
export function deleteMenu(id: string): Promise<ApiResponse<null>> {
  return request.delete(`/menus/${id}`);
}

