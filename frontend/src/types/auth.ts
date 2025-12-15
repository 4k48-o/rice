/**
 * 认证相关类型定义
 */
import { User } from './user';

export interface LoginRequest {
  username: string;
  password: string;
  tenant_code?: string;
  captcha_code?: string;
  captcha_key?: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  refresh_token: string;
  user_info?: UserInfo;
}

export interface RoleInfo {
  id: number;
  name: string;
  code: string;
  data_scope?: number;
}

export interface UserInfo {
  id: number | string;
  username: string;
  real_name?: string;
  avatar?: string;
  tenant_id?: number | string;
  user_type?: number;
  roles?: RoleInfo[];
  permissions?: string[];
  data_scope?: number;
}

export interface MenuNode {
  id: number;
  name?: string;
  title?: string;
  path?: string;
  component?: string;
  icon?: string;
  permission_code?: string;
  type?: number; // 1=目录,2=菜单,3=按钮
  sort?: number;
  status?: number;
  visible?: number;
  children?: MenuNode[];
}

