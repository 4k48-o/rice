/**
 * 角色相关类型定义
 */
import { PaginationParams } from './api';

/**
 * 角色基础类型
 */
export interface Role {
  id: string;
  name: string;
  code: string;
  sort: number;
  status: number;
  data_scope: number;
  tenant_id: string;
  created_at: string;
  updated_at?: string;
}

/**
 * 创建角色类型
 */
export interface RoleCreate {
  name: string;
  code: string;
  sort?: number;
  status?: number;
  data_scope?: number;
  permission_ids?: string[];
  department_ids?: string[]; // 当 data_scope=5 时使用
}

/**
 * 更新角色类型
 */
export interface RoleUpdate {
  name?: string;
  code?: string;
  sort?: number;
  status?: number;
  data_scope?: number;
  permission_ids?: string[];
  department_ids?: string[]; // 当 data_scope=5 时使用
}

/**
 * 角色列表查询参数
 */
export interface RoleListParams extends PaginationParams {
  name?: string;
  code?: string;
  status?: number;
}

/**
 * 权限树节点类型
 */
export interface PermissionTreeNode {
  id: string;
  name: string;
  code: string;
  type: number; // 1目录,2菜单,3按钮
  parent_id?: string;
  sort: number;
  status: number;
  tenant_id: string;
  children?: PermissionTreeNode[];
  checked?: boolean; // 前端使用，标记是否选中
}

