/**
 * 格式化工具函数
 */
import i18n from '@/i18n';

/**
 * 格式化日期时间
 */
export function formatDateTime(date: string | Date | null | undefined): string {
  if (!date) return '-';
  const d = typeof date === 'string' ? new Date(date) : date;
  return d.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });
}

/**
 * 格式化日期
 */
export function formatDate(date: string | Date | null | undefined): string {
  if (!date) return '-';
  const d = typeof date === 'string' ? new Date(date) : date;
  return d.toLocaleDateString('zh-CN');
}

/**
 * 格式化状态
 */
export function formatStatus(status: number): { text: string; color: string } {
  const statusMap: Record<number, { text: string; color: string }> = {
    0: { text: i18n.t('common.disabled'), color: 'error' },
    1: { text: i18n.t('common.normal'), color: 'success' },
    2: { text: i18n.t('common.locked'), color: 'warning' },
  };
  return statusMap[status] || { text: i18n.t('common.unknown'), color: 'default' };
}

/**
 * 格式化用户类型
 */
export function formatUserType(userType: number): string {
  const typeMap: Record<number, string> = {
    0: i18n.t('user.superAdmin'),
    1: i18n.t('user.tenantAdmin'),
    2: i18n.t('user.normalUser'),
  };
  return typeMap[userType] || i18n.t('common.unknown');
}

/**
 * 格式化性别
 */
export function formatGender(gender?: number): string {
  const genderMap: Record<number, string> = {
    0: i18n.t('user.genderUnknown'),
    1: i18n.t('user.male'),
    2: i18n.t('user.female'),
  };
  return gender !== undefined ? (genderMap[gender] || i18n.t('common.unknown')) : '-';
}

/**
 * 格式化数据权限
 */
export function formatDataScope(scope: number, t?: (key: string) => string): string {
  const translate = t || ((key: string) => i18n.t(key));
  const scopeMap: Record<number, string> = {
    1: translate('role.all'),
    2: translate('role.deptAndSub'),
    3: translate('role.deptOnly'),
    4: translate('role.selfOnly'),
    5: translate('role.custom'),
  };
  return scopeMap[scope] || translate('common.unknown');
}
