/**
 * 字典相关类型定义
 */
import { PaginationParams } from './api';

export interface DictType {
  id: string;
  name: string;
  code: string;
  sort: number;
  status: number; // 0禁用,1启用
  tenant_id: string;
  remark?: string;
  created_at?: string;
  updated_at?: string;
}

export interface DictTypeCreate {
  name: string;
  code: string;
  sort?: number;
  status?: number;
  remark?: string;
}

export interface DictTypeUpdate {
  name?: string;
  code?: string;
  sort?: number;
  status?: number;
  remark?: string;
}

export interface DictTypeListParams extends PaginationParams {
  keyword?: string;
  status?: number;
}

export interface DictData {
  id: string;
  dict_type_id: string;
  label: string;
  value: string;
  sort: number;
  status: number; // 0禁用,1启用
  css_class?: string;
  color?: string;
  icon?: string;
  tenant_id: string;
  remark?: string;
  created_at?: string;
  updated_at?: string;
  dict_type?: DictType; // 字典类型信息
}

export interface DictDataCreate {
  dict_type_id: string;
  label: string;
  value: string;
  sort?: number;
  status?: number;
  css_class?: string;
  color?: string;
  icon?: string;
  remark?: string;
}

export interface DictDataUpdate {
  dict_type_id?: string;
  label?: string;
  value?: string;
  sort?: number;
  status?: number;
  css_class?: string;
  color?: string;
  icon?: string;
  remark?: string;
}

export interface DictDataListParams extends PaginationParams {
  keyword?: string;
  dict_type_id?: string;
  status?: number;
}

