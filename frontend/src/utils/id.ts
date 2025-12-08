/**
 * ID 处理工具
 * 
 * 注意：所有ID现在都是字符串类型，不再需要类型转换。
 * 保留此文件用于ID比较和格式化等工具函数。
 */

/**
 * 安全地比较两个 ID
 * 
 * 统一转换为字符串进行比较，避免类型不一致的问题。
 * 
 * @param id1 - 第一个 ID
 * @param id2 - 第二个 ID
 * @returns 如果相等返回 true
 * 
 * @example
 * ```typescript
 * compareIds("123", "123") // true
 * compareIds("123", "456") // false
 * ```
 */
export function compareIds(
  id1: string | null | undefined,
  id2: string | null | undefined
): boolean {
  if (id1 === null || id1 === undefined || id2 === null || id2 === undefined) {
    return id1 === id2;
  }
  return String(id1) === String(id2);
}

/**
 * 格式化 ID 用于显示
 * 
 * @param id - ID 值（字符串）
 * @returns 格式化后的 ID 字符串
 * 
 * @example
 * ```typescript
 * formatId("123") // "123"
 * formatId(null) // ""
 * ```
 */
export function formatId(id: string | null | undefined): string {
  if (id === null || id === undefined) {
    return '';
  }
  return String(id);
}

/**
 * 从对象中提取 ID
 * 
 * 用于从实体对象中提取 ID。
 * 
 * @param entity - 实体对象
 * @param idField - ID 字段名，默认为 'id'
 * @returns ID 字符串
 * 
 * @example
 * ```typescript
 * extractId({ id: "123", name: 'test' }) // "123"
 * ```
 */
export function extractId(
  entity: { id?: string } | null | undefined,
  idField: string = 'id'
): string {
  if (!entity) {
    throw new Error('Entity cannot be null or undefined');
  }
  const id = (entity as any)[idField];
  if (id === null || id === undefined) {
    throw new Error(`ID field "${idField}" is missing`);
  }
  return String(id);
}
