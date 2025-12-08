/**
 * 表单数据处理工具
 * 
 * 注意：所有ID现在都是字符串类型，不再需要类型转换。
 * 保留此文件用于未来可能的表单数据处理需求。
 */

/**
 * 统一处理表单数据（占位函数，现在不需要转换）
 * 
 * @param data - 表单数据对象
 * @returns 处理后的数据对象（现在直接返回原数据）
 */
export function normalizeFormData<T extends Record<string, any>>(data: T): T {
  // 所有ID现在都是字符串，不需要转换
  return data;
}
