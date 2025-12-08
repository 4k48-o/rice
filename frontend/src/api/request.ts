/**
 * Axios请求封装
 */
import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, InternalAxiosRequestConfig } from 'axios';
import { message } from 'antd';
import { storage } from '@/utils/storage';
import { ApiResponse } from '@/types/api';
import i18n from '@/i18n';

// 创建axios实例
const request: AxiosInstance = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
request.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // 添加Token
    const token = storage.getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // 添加租户ID
    const tenantId = storage.getTenantId();
    if (tenantId) {
      config.headers['X-Tenant-ID'] = tenantId.toString();
    }

    // 添加语言偏好
    const language = localStorage.getItem('language') || 'zh-CN';
    config.headers['Accept-Language'] = language;

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
request.interceptors.response.use(
  (response: AxiosResponse<ApiResponse | any[]>) => {
    const res = response.data;

    // 如果返回的是数组（如菜单树），直接返回
    if (Array.isArray(res)) {
      return res;
    }

    // 如果code不是200，说明有错误
    if (res.code !== 200) {
      // Token过期或无效
      if (res.code === 401 || res.code === 20001 || res.code === 20002) {
        // 清除认证信息
        storage.clearAuth();
        // 显示错误消息
        message.error(res.message || i18n.t('common.loginExpired'));
        // 延迟跳转，确保消息能显示
        setTimeout(() => {
          window.location.href = '/login';
        }, 1000);
        return Promise.reject(new Error(res.message || 'Unauthorized'));
      }

      // 无权限
      if (res.code === 403 || res.code === 20003) {
        message.error(res.message || i18n.t('common.noPermission'));
        return Promise.reject(new Error(res.message || 'Forbidden'));
      }

      // 其他错误
      message.error(res.message || i18n.t('common.requestFailed'));
      return Promise.reject(new Error(res.message || 'Request failed'));
    }

    // 返回完整的响应对象，包含code、message、data等
    return res;
  },
  (error) => {
    // 网络错误
    if (!error.response) {
      message.error(i18n.t('common.networkError'));
      return Promise.reject(error);
    }

    // HTTP状态码错误
    const { status, data, config } = error.response;
    const url = config?.url || '';
    
    // 对于登录接口，不在这里显示错误消息，让业务层处理
    const isLoginRequest = url.includes('/auth/login');
    
    let errorMessage = i18n.t('common.requestFailed');

    // 如果后端返回了标准格式的错误响应（包含code字段）
    if (data && typeof data === 'object' && 'code' in data) {
      // 处理标准格式的错误响应
      if (data.code === 401 || data.code === 20001 || data.code === 20002) {
        // 对于登录接口的401错误，不自动跳转和清除认证，让业务层处理
        if (!isLoginRequest) {
          // 清除认证信息
          storage.clearAuth();
          // 显示错误消息
          errorMessage = data.message || i18n.t('common.loginExpired');
          // 延迟跳转，确保消息能显示
          setTimeout(() => {
            window.location.href = '/login';
          }, 1000);
        } else {
          errorMessage = data.message || i18n.t('common.loginExpired');
        }
      } else if (data.code === 403 || data.code === 20003) {
        errorMessage = data.message || i18n.t('common.noPermission');
      } else {
        errorMessage = data.message || i18n.t('common.requestFailed');
      }
    } else if (data && typeof data === 'object' && 'message' in data) {
      errorMessage = data.message || i18n.t('common.requestFailed');
    } else {
      switch (status) {
        case 400:
          errorMessage = data?.message || data?.detail || i18n.t('common.paramError');
          break;
        case 401:
          // 对于登录接口的401错误，不自动跳转和清除认证，让业务层处理
          if (!isLoginRequest) {
            // 清除认证信息
            storage.clearAuth();
            // 显示错误消息
            errorMessage = data?.message || data?.detail || i18n.t('common.loginExpired');
            // 延迟跳转，确保消息能显示
            setTimeout(() => {
              window.location.href = '/login';
            }, 1000);
          } else {
            errorMessage = data?.message || data?.detail || i18n.t('common.loginExpired');
          }
          break;
        case 403:
          errorMessage = data?.message || data?.detail || i18n.t('common.noPermission');
          break;
        case 404:
          errorMessage = data?.message || data?.detail || i18n.t('common.resourceNotFound');
          break;
        case 422:
          // 参数验证错误
          if (data?.errors && Array.isArray(data.errors)) {
            const firstError = data.errors[0];
            errorMessage = firstError?.msg || firstError?.message || i18n.t('common.paramValidationFailed');
          } else {
            errorMessage = data?.message || data?.detail || i18n.t('common.paramValidationFailed');
          }
          break;
        case 500:
          errorMessage = data?.message || data?.detail || i18n.t('common.serverError');
          console.error('Server error:', data);
          break;
        default:
          errorMessage = data?.message || data?.detail || i18n.t('common.requestFailed') + ` (${status})`;
      }
    }

    // 对于登录接口，不在这里显示错误消息
    if (!isLoginRequest) {
      message.error(errorMessage);
    }
    
    // 将错误消息附加到错误对象上，供业务层使用
    error.errorMessage = errorMessage;
    return Promise.reject(error);
  }
);

export default request;

