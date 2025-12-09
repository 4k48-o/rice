/**
 * 字典管理API
 */
import request from './request';
import { ApiResponse, PageResponse } from '@/types/api';
import { DictType, DictTypeCreate, DictTypeUpdate, DictTypeListParams, DictData, DictDataCreate, DictDataUpdate, DictDataListParams } from '@/types/dict';

/**
 * 获取字典类型列表
 */
export function getDictTypeList(params: DictTypeListParams): Promise<ApiResponse<PageResponse<DictType>>> {
  return request.get('/dict-types', { params });
}

/**
 * 获取字典类型详情
 */
export function getDictTypeDetail(id: string): Promise<ApiResponse<DictType>> {
  return request.get(`/dict-types/${id}`);
}

/**
 * 创建字典类型
 */
export function createDictType(data: DictTypeCreate): Promise<ApiResponse<DictType>> {
  return request.post('/dict-types', data);
}

/**
 * 更新字典类型
 */
export function updateDictType(id: string, data: DictTypeUpdate): Promise<ApiResponse<DictType>> {
  return request.put(`/dict-types/${id}`, data);
}

/**
 * 删除字典类型
 */
export function deleteDictType(id: string): Promise<ApiResponse<null>> {
  return request.delete(`/dict-types/${id}`);
}

/**
 * 获取字典数据列表
 */
export function getDictDataList(params: DictDataListParams): Promise<ApiResponse<PageResponse<DictData>>> {
  return request.get('/dict-data', { params });
}

/**
 * 根据类型获取字典数据（公开接口，支持缓存）
 */
export function getDictDataByType(typeCode: string): Promise<ApiResponse<DictData[]>> {
  return request.get(`/dict-data/type/${typeCode}`);
}

/**
 * 获取字典数据详情
 */
export function getDictDataDetail(id: string): Promise<ApiResponse<DictData>> {
  return request.get(`/dict-data/${id}`);
}

/**
 * 创建字典数据
 */
export function createDictData(data: DictDataCreate): Promise<ApiResponse<DictData>> {
  return request.post('/dict-data', data);
}

/**
 * 更新字典数据
 */
export function updateDictData(id: string, data: DictDataUpdate): Promise<ApiResponse<DictData>> {
  return request.put(`/dict-data/${id}`, data);
}

/**
 * 删除字典数据
 */
export function deleteDictData(id: string): Promise<ApiResponse<null>> {
  return request.delete(`/dict-data/${id}`);
}

