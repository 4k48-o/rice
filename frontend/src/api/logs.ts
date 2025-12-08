/**
 * 日志查询API
 */
import request from './request';
import { ApiResponse, PageResponse } from '@/types/api';
import { LoginLogResponse, OperationLogResponse, OnlineUserResponse } from '@/types/logs';

/**
 * 获取登录日志
 */
export function getLoginLogs(params: any): Promise<ApiResponse<PageResponse<LoginLogResponse>>> {
  return request.get('/logs/login', { params });
}

/**
 * 获取操作日志
 */
export function getOperationLogs(params: any): Promise<ApiResponse<PageResponse<OperationLogResponse>>> {
  return request.get('/logs/operation', { params });
}

/**
 * 获取在线用户
 */
export function getOnlineUsers(): Promise<ApiResponse<OnlineUserResponse[]>> {
  return request.get('/logs/online');
}

/**
 * 强制下线用户
 */
export function forceLogoutUser(userId: number): Promise<ApiResponse<null>> {
  return request.post(`/logs/online/${userId}/force-logout`);
}

