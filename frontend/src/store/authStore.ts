/**
 * 认证状态管理
 */
import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { UserInfo } from '@/types/auth';
import { storage } from '@/utils/storage';

interface AuthState {
  token: string | null;
  refreshToken: string | null;
  userInfo: UserInfo | null;
  permissions: string[];
  menus: any[];
  isAuthenticated: boolean;
  
  setToken: (token: string) => void;
  setRefreshToken: (token: string) => void;
  setUserInfo: (info: UserInfo) => void;
  setPermissions: (permissions: string[]) => void;
  setMenus: (menus: any[]) => void;
  clearAuth: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => {
      const token = storage.getToken();
      const refreshToken = storage.getRefreshToken();
      const userInfo = storage.getUserInfo();
      
      return {
        token,
        refreshToken,
        userInfo,
        permissions: [],
        menus: [],
        isAuthenticated: !!token,

        setToken: (token: string) => {
          storage.setToken(token);
          set({ token, isAuthenticated: true });
        },

        setRefreshToken: (token: string) => {
          storage.setRefreshToken(token);
          set({ refreshToken: token });
        },

        setUserInfo: (info: UserInfo) => {
          storage.setUserInfo(info);
          set({ userInfo: info });
        },

        setPermissions: (permissions: string[]) => {
          set({ permissions });
        },

        setMenus: (menus: any[]) => {
          set({ menus });
        },

        clearAuth: () => {
          storage.clearAuth();
          set({
            token: null,
            refreshToken: null,
            userInfo: null,
            permissions: [],
            menus: [],
            isAuthenticated: false,
          });
        },
      };
    },
    {
      name: 'auth-storage',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        token: state.token,
        refreshToken: state.refreshToken,
        userInfo: state.userInfo,
      }),
    }
  )
);

