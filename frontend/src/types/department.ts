/**
 * 部门相关类型定义
 */

export interface Department {
  id: number | string; // 支持字符串类型以避免 JavaScript 大整数精度丢失
  code: string; // 后端字段名是 code
  name: string; // 后端字段名是 name
  dept_code?: string; // 兼容旧字段名
  dept_name?: string; // 兼容旧字段名
  parent_id?: number | string;
  parent_name?: string;
  leader_id?: number | string;
  leader_name?: string;
  phone?: string;
  email?: string;
  status: number;
  sort?: number; // 后端字段名是 sort
  sort_order?: number; // 兼容旧字段名
  remark?: string;
  created_at: string;
  updated_at?: string;
  tenant_id?: number | string;
  children?: Department[];
}

export interface DepartmentCreate {
  dept_code: string;
  dept_name: string;
  parent_id?: number;
  leader_id?: number;
  phone?: string;
  email?: string;
  status?: number;
  sort_order?: number;
  remark?: string;
}

export interface DepartmentUpdate {
  dept_code?: string;
  dept_name?: string;
  parent_id?: number;
  leader_id?: number;
  phone?: string;
  email?: string;
  status?: number;
  sort_order?: number;
  remark?: string;
}

