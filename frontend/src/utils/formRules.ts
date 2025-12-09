/**
 * 表单校验规则工具
 * 
 * 提供常用的表单校验规则，统一管理校验逻辑
 */
import { Rule } from 'antd/es/form';

/**
 * 必填字段校验
 */
export const required = (fieldName: string = '此字段'): Rule => ({
  required: true,
  message: `请输入${fieldName}`,
});

/**
 * 邮箱校验
 */
export const email: Rule = {
  type: 'email',
  message: '请输入有效的邮箱地址',
};

/**
 * 手机号校验
 */
export const phone: Rule = {
  pattern: /^1[3-9]\d{9}$/,
  message: '请输入有效的手机号',
};

/**
 * 密码校验（至少8位，包含大小写字母和数字）
 */
export const password: Rule[] = [
  { required: true, message: '请输入密码' },
  { min: 8, message: '密码长度至少8位' },
  { max: 20, message: '密码长度不能超过20位' },
  {
    pattern: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/,
    message: '密码必须包含大小写字母和数字',
  },
];

/**
 * 简单密码校验（至少6位）
 */
export const simplePassword: Rule[] = [
  { required: true, message: '请输入密码' },
  { min: 6, message: '密码长度至少6位' },
  { max: 20, message: '密码长度不能超过20位' },
];

/**
 * URL 校验
 */
export const url: Rule = {
  type: 'url',
  message: '请输入有效的URL',
};

/**
 * 数字范围校验
 */
export const numberRange = (min: number, max: number): Rule => ({
  type: 'number',
  min,
  max,
  message: `请输入${min}-${max}之间的数字`,
});

/**
 * 字符串长度校验
 */
export const stringLength = (min: number, max: number, fieldName: string = '此字段'): Rule[] => [
  { min, message: `${fieldName}长度至少${min}个字符` },
  { max, message: `${fieldName}长度不能超过${max}个字符` },
];

/**
 * 用户名校验（字母、数字、下划线，3-20位）
 */
export const username: Rule[] = [
  { required: true, message: '请输入用户名' },
  { min: 3, message: '用户名长度至少3个字符' },
  { max: 20, message: '用户名长度不能超过20个字符' },
  {
    pattern: /^[a-zA-Z0-9_]+$/,
    message: '用户名只能包含字母、数字和下划线',
  },
];

/**
 * 确认密码校验
 */
export const confirmPassword = (passwordField: string = 'password'): Rule[] => [
  { required: true, message: '请确认密码' },
  ({ getFieldValue }) => ({
    validator(_, value) {
      if (!value || getFieldValue(passwordField) === value) {
        return Promise.resolve();
      }
      return Promise.reject(new Error('两次输入的密码不一致'));
    },
  }),
];

/**
 * 正整数校验
 */
export const positiveInteger: Rule = {
  pattern: /^[1-9]\d*$/,
  message: '请输入正整数',
};

/**
 * 非负整数校验（包括0）
 */
export const nonNegativeInteger: Rule = {
  pattern: /^\d+$/,
  message: '请输入非负整数',
};

/**
 * 中文姓名校验（2-10个汉字）
 */
export const chineseName: Rule[] = [
  { required: true, message: '请输入姓名' },
  {
    pattern: /^[\u4e00-\u9fa5]{2,10}$/,
    message: '请输入2-10个汉字',
  },
];

/**
 * 身份证号校验（18位）
 */
export const idCard: Rule = {
  pattern: /^[1-9]\d{5}(18|19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dXx]$/,
  message: '请输入有效的身份证号',
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
};

