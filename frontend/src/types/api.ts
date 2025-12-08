/**
 * API响应类型定义
 */

export interface ApiResponse<T = any> {
  code: number;
  message: string;
  data: T;
  timestamp: number;
  errors?: Array<{
    field: string;
    message: string;
  }>;
}

export interface PageResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages?: number;
}

export interface PaginationParams {
  page?: number;
  page_size?: number;
}

