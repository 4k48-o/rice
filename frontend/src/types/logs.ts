/**
 * 日志相关类型定义
 */

export interface LoginLogResponse {
  id: number;
  user_id?: number;
  username: string;
  status: number;
  ip?: string;
  location?: string;
  browser?: string;
  os?: string;
  msg?: string;
  login_time: string;
  created_at: string;
}

export interface OperationLogResponse {
  id: number;
  user_id?: number;
  username?: string;
  module?: string;
  summary?: string;
  method?: string;
  url?: string;
  ip?: string;
  location?: string;
  user_agent?: string;
  params?: Record<string, any>;
  result?: Record<string, any>;
  status: number;
  error_msg?: string;
  duration: number;
  created_at: string;
}

export interface OnlineUserResponse {
  user_id: number;
  username: string;
  real_name?: string;
  ip?: string;
  location?: string;
  login_time: string;
  last_active_time: string;
}

