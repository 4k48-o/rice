/**
 * 菜单相关类型定义
 */
import { PaginationParams } from './api';

export interface Menu {
  id: string; // ID 统一使用字符串类型
  name: string;
  title: string;
  parent_id?: string | null; // 父菜单ID，null表示顶级菜单
  path?: string;
  component?: string;
  redirect?: string;
  icon?: string;
  sort: number;
  type: number; // 类型:1目录,2菜单,3按钮
  permission_code?: string;
  status: number; // 状态:0禁用,1启用
  visible: number; // 是否可见:0隐藏,1显示
  is_cache: number; // 是否缓存:0否,1是
  is_external: number; // 是否外链:0否,1是
  tenant_id: string;
  children?: Menu[]; // 子菜单（树形结构）
}

export interface MenuCreate {
  name: string;
  title: string;
  parent_id?: string | null;
  path?: string;
  component?: string;
  redirect?: string;
  icon?: string;
  sort?: number;
  type: number;
  permission_code?: string;
  status?: number;
  visible?: number;
  is_cache?: number;
  is_external?: number;
}

export interface MenuUpdate {
  name?: string;
  title?: string;
  parent_id?: string | null;
  path?: string;
  component?: string;
  redirect?: string;
  icon?: string;
  sort?: number;
  type?: number;
  permission_code?: string;
  status?: number;
  visible?: number;
  is_cache?: number;
  is_external?: number;
}

export interface MenuListParams extends PaginationParams {
  keyword?: string;
  menu_type?: number;
  status?: number;
}

