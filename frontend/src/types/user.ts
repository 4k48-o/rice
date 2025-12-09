/**
 * 用户相关类型定义
 */
import { PaginationParams } from './api';

export interface User {
  id: string; // ID 统一使用字符串类型
  username: string;
  real_name?: string;
  nickname?: string;
  email?: string;
  phone?: string;
  user_type: number;
  dept_id?: string; // ID 统一使用字符串类型
  dept_name?: string;
  position?: string;
  status: number;
  avatar?: string;
  gender?: number;
  last_login_time?: string;
  last_login_ip?: string;
  login_count?: number;
  role_ids?: string[]; // ID 统一使用字符串类型
  roles?: RoleInfo[];
  created_at: string;
  updated_at?: string;
}

export interface RoleInfo {
  id: string; // ID 统一使用字符串类型
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
  dept_id?: string; // ID 统一使用字符串类型
  position?: string;
  gender?: number;
  role_ids?: string[]; // ID 统一使用字符串类型
  status?: number;
  remark?: string;
}

export interface UserUpdate {
  email?: string;
  phone?: string;
  real_name?: string;
  nickname?: string;
  dept_id?: string; // ID 统一使用字符串类型
  position?: string;
  gender?: number;
  status?: number;
  role_ids?: string[]; // ID 统一使用字符串类型
  remark?: string;
}

export interface UserListParams extends PaginationParams {
  username?: string;
  phone?: string;
  email?: string;
  status?: number;
  dept_id?: string; // ID 统一使用字符串类型
  user_type?: number;
  last_login_start?: string;
  last_login_end?: string;
}

