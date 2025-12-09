/**
 * 搜索输入框组件
 * 
 * 使用 Space.Compact 替代 Input.Search，避免 addonAfter 弃用警告
 */
import { Input, Button, Space } from 'antd';
import { SearchOutlined } from '@ant-design/icons';
import { CSSProperties } from 'react';

export interface SearchInputProps {
  /**
   * 占位符
   */
  placeholder?: string;
  
  /**
   * 搜索值
   */
  value?: string;
  
  /**
   * 值变化回调
   */
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void;
  
  /**
   * 搜索回调
   */
  onSearch?: (value: string) => void;
  
  /**
   * 是否允许清空
   */
  allowClear?: boolean;
  
  /**
   * 样式
   */
  style?: CSSProperties;
  
  /**
   * 类名
   */
  className?: string;
  
  /**
   * 是否禁用
   */
  disabled?: boolean;
  
  /**
   * 输入框大小
   */
  size?: 'large' | 'middle' | 'small';
  
  /**
   * 按 Enter 键时是否触发搜索
   */
  enterButton?: boolean | React.ReactNode;
}

/**
 * 搜索输入框组件
 */
export default function SearchInput({
  placeholder,
  value,
  onChange,
  onSearch,
  allowClear = true,
  style,
  className,
  disabled = false,
  size = 'middle',
  enterButton = true,
}: SearchInputProps) {
  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && onSearch) {
      e.preventDefault();
      onSearch(value || '');
    }
  };

  const handleSearch = () => {
    if (onSearch) {
      onSearch(value || '');
    }
  };

  const buttonContent = enterButton === true ? <SearchOutlined /> : enterButton;

  return (
    <Space.Compact style={style} className={className}>
      <Input
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        onPressEnter={handleKeyPress}
        allowClear={allowClear}
        disabled={disabled}
        size={size}
        style={{ flex: 1 }}
      />
      {enterButton && (
        <Button
          type="primary"
          icon={buttonContent}
          onClick={handleSearch}
          disabled={disabled}
          size={size}
        >
          {typeof enterButton === 'string' ? enterButton : ''}
        </Button>
      )}
    </Space.Compact>
  );
}

