/**
 * 认证相关API
 */
import request from './request';
import { ApiResponse, PageResponse } from '@/types/api';
import { LoginRequest, TokenResponse, UserInfo, MenuNode } from '@/types/auth';

/**
 * 用户登录
 */
export function login(data: LoginRequest): Promise<ApiResponse<TokenResponse>> {
  return request.post('/auth/login', data);
}

/**
 * 刷新Token
 */
export function refreshToken(refreshToken: string): Promise<ApiResponse<TokenResponse>> {
  return request.post('/auth/refresh', { refresh_token: refreshToken });
}

/**
 * 退出登录
 */
export function logout(): Promise<ApiResponse<null>> {
  return request.post('/auth/logout');
}

/**
 * 获取当前用户信息
 */
export function getUserInfo(): Promise<ApiResponse<UserInfo>> {
  return request.get('/auth/user-info');
}

/**
 * 获取用户菜单树（从菜单API）
 * 注意：此接口直接返回数组，不是包装在Response中
 */
export async function getUserMenuTree(): Promise<MenuNode[]> {
  // 后端直接返回数组，需要特殊处理
  const response = await request.get('/menus/user');
  // 如果返回的是数组，直接返回；如果是包装在data中，返回data
  return Array.isArray(response) ? response : (response.data || []);
}

/**
 * 获取验证码
 */
export function getCaptcha(): Promise<ApiResponse<{ captcha_key: string; captcha_image: string; expires_in: number }>> {
  return request.get('/auth/captcha');
}

