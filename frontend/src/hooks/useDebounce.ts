/**
 * 防抖 Hook
 * 
 * 用于对函数进行防抖处理，常用于按钮点击、搜索输入等场景
 * 
 * @example
 * ```tsx
 * const handleSearch = (value: string) => {
 *   console.log('Search:', value);
 * };
 * 
 * const debouncedSearch = useDebounce(handleSearch, 500);
 * 
 * <Input onChange={(e) => debouncedSearch(e.target.value)} />
 * ```
 */
import { useCallback, useRef, useEffect } from 'react';

export function useDebounce<T extends (...args: any[]) => any>(
  callback: T,
  delay: number = 300
): (...args: Parameters<T>) => void {
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);
  const callbackRef = useRef(callback);

  // 更新 callback 引用
  useEffect(() => {
    callbackRef.current = callback;
  }, [callback]);

  // 清理函数
  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  const debouncedCallback = useCallback(
    (...args: Parameters<T>) => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }

      timeoutRef.current = setTimeout(() => {
        callbackRef.current(...args);
      }, delay);
    },
    [delay]
  );

  return debouncedCallback;
}

