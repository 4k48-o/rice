/**
 * 表单校验规则工具
 * 
 * 提供常用的表单校验规则，统一管理校验逻辑
 * 支持国际化，使用 i18n 实例自动响应语言切换
 * 
 * 注意：由于 i18n 可能在模块加载时尚未初始化，所有规则都使用 validator 函数
 * 在运行时动态获取翻译，确保国际化正确工作
 */
import { Rule } from 'antd/es/form';
import i18n from '@/i18n';

/**
 * 获取翻译函数（在运行时动态获取，确保 i18n 已初始化）
 */
const getT = () => {
  return (key: string, options?: any): string => {
    const result = i18n.t(key, options);
    return typeof result === 'string' ? result : String(result);
  };
};

/**
 * 必填字段校验
 */
export const required = (fieldName: string = '此字段'): Rule => ({
  required: true,
  validator: (_, value) => {
    const t = getT();
    if (!value || (typeof value === 'string' && value.trim() === '')) {
      return Promise.reject(new Error(t('common.validation.required', { field: fieldName })));
    }
    return Promise.resolve();
  },
});

/**
 * 邮箱校验（格式 + 长度）
 * 只在有值时才校验，允许为空
 */
export const email: Rule[] = [
  {
    validator: (_, value) => {
      const t = getT();
      if (!value || value.trim() === '') {
        return Promise.resolve();
      }
      // 邮箱格式校验
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(value)) {
        return Promise.reject(new Error(t('common.validation.invalidEmail')));
      }
      // 长度校验
      if (value.length > 100) {
        return Promise.reject(new Error(t('common.validation.emailMaxLength', { max: 100 })));
      }
      return Promise.resolve();
    },
  },
];

/**
 * 手机号校验（格式 + 长度）
 * 只在有值时才校验，允许为空
 */
export const phone: Rule[] = [
  {
    validator: (_, value) => {
      const t = getT();
      if (!value || value.trim() === '') {
        return Promise.resolve();
      }
      // 手机号格式校验
      const phoneRegex = /^1[3-9]\d{9}$/;
      if (!phoneRegex.test(value)) {
        return Promise.reject(new Error(t('common.validation.invalidPhone')));
      }
      // 长度校验（手机号固定11位，但为了兼容性保留）
      if (value.length > 20) {
        return Promise.reject(new Error(t('common.validation.phoneMaxLength', { max: 20 })));
      }
      return Promise.resolve();
    },
  },
];

/**
 * 密码校验（至少8位，包含大小写字母和数字）
 */
export const password: Rule[] = [
  { required: true, message: i18n.t('common.validation.passwordRequired') },
  { min: 8, message: i18n.t('common.validation.passwordMinLength', { min: 8 }) },
  { max: 20, message: i18n.t('common.validation.passwordMaxLength', { max: 20 }) },
  {
    pattern: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/,
    message: i18n.t('common.validation.passwordComplexity'),
  },
];

/**
 * 简单密码校验（至少6位）
 */
export const simplePassword: Rule[] = [
  { required: true, message: i18n.t('common.validation.passwordRequired') },
  { min: 6, message: i18n.t('common.validation.passwordMinLength', { min: 6 }) },
  { max: 20, message: i18n.t('common.validation.passwordMaxLength', { max: 20 }) },
];

/**
 * URL 校验
 */
export const url: Rule = {
  type: 'url',
  message: i18n.t('common.validation.invalidUrl'),
};

/**
 * 数字范围校验
 */
export const numberRange = (min: number, max: number): Rule => ({
  type: 'number',
  min,
  max,
  message: i18n.t('common.validation.numberRange', { min, max }),
});

/**
 * 字符串长度校验
 */
export const stringLength = (min: number, max: number, fieldName: string = '此字段'): Rule[] => [
  { min, message: i18n.t('common.validation.stringMinLength', { field: fieldName, min }) },
  { max, message: i18n.t('common.validation.stringMaxLength', { field: fieldName, max }) },
];

/**
 * 用户名校验（字母、数字、下划线，3-50位）
 */
export const username: Rule[] = [
  { required: true, message: i18n.t('common.validation.usernameRequired') },
  { min: 3, message: i18n.t('common.validation.usernameMinLength', { min: 3 }) },
  { max: 50, message: i18n.t('common.validation.usernameMaxLength', { max: 50 }) },
  {
    pattern: /^[a-zA-Z0-9_]+$/,
    message: i18n.t('common.validation.usernamePattern'),
  },
];

/**
 * 真实姓名校验（最多50字符）
 */
export const realName: Rule[] = [
  {
    validator: (_, value) => {
      const t = getT();
      if (!value || value.trim() === '') {
        return Promise.resolve();
      }
      if (value.length > 50) {
        return Promise.reject(new Error(t('common.validation.realNameMaxLength', { max: 50 })));
      }
      return Promise.resolve();
    },
  },
];

/**
 * 昵称校验（最多50字符）
 */
export const nickname: Rule[] = [
  {
    validator: (_, value) => {
      const t = getT();
      if (!value || value.trim() === '') {
        return Promise.resolve();
      }
      if (value.length > 50) {
        return Promise.reject(new Error(t('common.validation.nicknameMaxLength', { max: 50 })));
      }
      return Promise.resolve();
    },
  },
];

/**
 * 职位校验（最多50字符）
 */
export const position: Rule[] = [
  {
    validator: (_, value) => {
      const t = getT();
      if (!value || value.trim() === '') {
        return Promise.resolve();
      }
      if (value.length > 50) {
        return Promise.reject(new Error(t('common.validation.positionMaxLength', { max: 50 })));
      }
      return Promise.resolve();
    },
  },
];

/**
 * 备注校验（最多500字符）
 */
export const remark: Rule[] = [
  {
    validator: (_, value) => {
      const t = getT();
      if (!value || value.trim() === '') {
        return Promise.resolve();
      }
      if (value.length > 500) {
        return Promise.reject(new Error(t('common.validation.remarkMaxLength', { max: 500 })));
      }
      return Promise.resolve();
    },
  },
];

/**
 * 确认密码校验
 */
export const confirmPassword = (passwordField: string = 'password'): Rule[] => [
  { required: true, message: i18n.t('common.validation.confirmPasswordRequired') },
  ({ getFieldValue }) => ({
    validator(_, value) {
      if (!value || getFieldValue(passwordField) === value) {
        return Promise.resolve();
      }
      return Promise.reject(new Error(i18n.t('common.validation.passwordMismatch')));
    },
  }),
];

/**
 * 正整数校验
 */
export const positiveInteger: Rule = {
  pattern: /^[1-9]\d*$/,
  message: i18n.t('common.validation.positiveInteger'),
};

/**
 * 非负整数校验（包括0）
 */
export const nonNegativeInteger: Rule = {
  pattern: /^\d+$/,
  message: i18n.t('common.validation.nonNegativeInteger'),
};

/**
 * 中文姓名校验（2-10个汉字）
 */
export const chineseName: Rule[] = [
  { required: true, message: i18n.t('common.validation.chineseNameRequired') },
  {
    pattern: /^[\u4e00-\u9fa5]{2,10}$/,
    message: i18n.t('common.validation.chineseNamePattern'),
  },
];

/**
 * 身份证号校验（18位）
 */
export const idCard: Rule = {
  pattern: /^[1-9]\d{5}(18|19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dXx]$/,
  message: i18n.t('common.validation.invalidIdCard'),
};

/**
 * 导出所有规则对象（方便使用）
 */
export const formRules = {
  required,
  email,
  phone,
  password,
  simplePassword,
  url,
  numberRange,
  stringLength,
  username,
  confirmPassword,
  positiveInteger,
  nonNegativeInteger,
  chineseName,
  idCard,
  realName,
  nickname,
  position,
  remark,
};

