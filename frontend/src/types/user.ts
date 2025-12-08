/**
 * 用户相关类型定义
 */
import { PaginationParams } from './api';

export interface User {
  id: number | string; // 支持字符串类型以避免 JavaScript 大整数精度丢失
  username: string;
  real_name?: string;
  nickname?: string;
  email?: string;
  phone?: string;
  user_type: number;
  dept_id?: number | string; // 支持字符串类型以避免精度丢失
  dept_name?: string;
  position?: string;
  status: number;
  avatar?: string;
  gender?: number;
  last_login_time?: string;
  last_login_ip?: string;
  login_count?: number;
  role_ids?: (number | string)[]; // 支持字符串类型以避免精度丢失
  roles?: RoleInfo[];
  created_at: string;
  updated_at?: string;
}

export interface RoleInfo {
  id: number | string; // 支持字符串类型以避免精度丢失
  role_code: string;
  role_name: string;
}

export interface UserCreate {
  username: string;
  password: string;
  real_name?: string;
  nickname?: string;
  email?: string;
  phone?: string;
  dept_id?: number | string;
  position?: string;
  gender?: number;
  role_ids?: (number | string)[];
  status?: number;
  remark?: string;
}

export interface UserUpdate {
  email?: string;
  phone?: string;
  real_name?: string;
  nickname?: string;
  dept_id?: number | string;
  position?: string;
  gender?: number;
  status?: number;
  role_ids?: (number | string)[];
  remark?: string;
}

export interface UserListParams extends PaginationParams {
  username?: string;
  phone?: string;
  email?: string;
  status?: number;
  dept_id?: number | string;
  user_type?: number;
  last_login_start?: string;
  last_login_end?: string;
}

