/**
 * 本地存储工具函数
 */

const TOKEN_KEY = 'access_token';
const REFRESH_TOKEN_KEY = 'refresh_token';
const USER_INFO_KEY = 'user_info';
const TENANT_ID_KEY = 'tenant_id';
const REMEMBER_USERNAME_KEY = 'remember_username';

export const storage = {
  // Token管理
  getToken(): string | null {
    return localStorage.getItem(TOKEN_KEY);
  },

  setToken(token: string): void {
    localStorage.setItem(TOKEN_KEY, token);
  },

  removeToken(): void {
    localStorage.removeItem(TOKEN_KEY);
  },

  // Refresh Token管理
  getRefreshToken(): string | null {
    return localStorage.getItem(REFRESH_TOKEN_KEY);
  },

  setRefreshToken(token: string): void {
    localStorage.setItem(REFRESH_TOKEN_KEY, token);
  },

  removeRefreshToken(): void {
    localStorage.removeItem(REFRESH_TOKEN_KEY);
  },

  // 用户信息管理
  getUserInfo(): any | null {
    const info = localStorage.getItem(USER_INFO_KEY);
    return info ? JSON.parse(info) : null;
  },

  setUserInfo(info: any): void {
    localStorage.setItem(USER_INFO_KEY, JSON.stringify(info));
  },

  removeUserInfo(): void {
    localStorage.removeItem(USER_INFO_KEY);
  },

  // 租户ID管理
  getTenantId(): number | null {
    const id = localStorage.getItem(TENANT_ID_KEY);
    return id ? parseInt(id, 10) : null;
  },

  setTenantId(id: number): void {
    localStorage.setItem(TENANT_ID_KEY, id.toString());
  },

  removeTenantId(): void {
    localStorage.removeItem(TENANT_ID_KEY);
  },

  // 记住用户名
  setRememberUsername(username: string): void {
    localStorage.setItem(REMEMBER_USERNAME_KEY, username);
  },

  getRememberUsername(): string | null {
    return localStorage.getItem(REMEMBER_USERNAME_KEY);
  },

  removeRememberUsername(): void {
    localStorage.removeItem(REMEMBER_USERNAME_KEY);
  },

  // 清除所有认证信息
  clearAuth(): void {
    this.removeToken();
    this.removeRefreshToken();
    this.removeUserInfo();
    this.removeTenantId();
  },
};

