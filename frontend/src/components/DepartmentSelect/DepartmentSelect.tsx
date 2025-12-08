/**
 * 部门选择组件
 * 
 * 可复用的部门选择下拉框组件，使用 TreeSelect 实现树形结构展示
 * 支持树形结构的部门数据，层级关系清晰直观
 */
import { useEffect, useState, useMemo } from 'react';
import { TreeSelect, Spin } from 'antd';
import { getDepartmentTree } from '@/api/department';
import { Department } from '@/types/department';
import { useTranslation } from 'react-i18next';

export interface DepartmentSelectProps {
  /**
   * 选中的部门ID
   */
  value?: number | string;
  
  /**
   * 值变化回调
   */
  onChange?: (value: number | string | undefined) => void;
  
  /**
   * 是否禁用
   */
  disabled?: boolean;
  
  /**
   * 占位符
   */
  placeholder?: string;
  
  /**
   * 是否允许清空
   */
  allowClear?: boolean;
  
  /**
   * 样式
   */
  style?: React.CSSProperties;
  
  /**
   * 类名
   */
  className?: string;
  
  /**
   * 是否加载中
   */
  loading?: boolean;
  
  /**
   * 是否只显示启用状态的部门
   */
  onlyEnabled?: boolean;
  
  /**
   * 排除的部门ID列表（不显示这些部门及其子部门）
   */
  excludeIds?: (number | string)[];
  
  /**
   * 是否默认展开所有节点
   */
  treeDefaultExpandAll?: boolean;
  
  /**
   * 是否显示搜索框
   */
  showSearch?: boolean;
  
  /**
   * 树节点过滤函数
   */
  filterTreeNode?: (inputValue: string, node: any) => boolean;
  
  /**
   * 是否显示连接线
   */
  treeLine?: boolean;
  
  /**
   * 下拉框的最大高度
   */
  maxTagCount?: number;
  
  /**
   * 下拉框的宽度
   */
  dropdownStyle?: React.CSSProperties;
}

/**
 * 转换部门树为 TreeSelect 格式
 * @param depts 部门树数据
 * @param onlyEnabled 是否只显示启用状态的部门
 * @param excludeIds 排除的部门ID列表
 * @param parentPath 父级路径（用于构建完整路径，包含编码）
 * @returns TreeSelect 格式的数据
 */
function convertToTreeData(
  depts: Department[],
  onlyEnabled: boolean = false,
  excludeIds?: (number | string)[],
  parentPath: string = ''
): any[] {
  return depts
    .filter((dept) => {
      // 排除指定部门及其子部门
      if (excludeIds?.includes(dept.id)) {
        return false;
      }
      // 只显示启用状态的部门
      if (onlyEnabled && dept.status !== 1) {
        return false;
      }
      return true;
    })
    .map((dept) => {
      const deptName = dept.name || dept.dept_name || `部门-${dept.id}`;
      const deptCode = dept.code || dept.dept_code || '';
      
      // 编码处理：如果编码较长，显示缩写（前2个字符 + ..）
      // 例如：market -> ma.., sales -> sa..
      const formatCode = (code: string): string => {
        if (!code) return '';
        // 如果编码长度超过4个字符，显示前2个字符 + ..
        if (code.length > 4) {
          return `${code.substring(0, 2)}..`;
        }
        return code;
      };
      
      // 构建当前部门的显示文本：部门名(编码) 或 部门名
      const formattedCode = formatCode(deptCode);
      const deptDisplay = formattedCode ? `${deptName}(${formattedCode})` : deptName;
      
      // 构建完整路径：父路径 / 当前部门显示文本
      // 格式：市场部(ma..) / 销售部(sa..) / 总经办(ad..)
      // 注意：使用 `/` 分隔，前后有空格以便阅读
      const fullPath = parentPath ? `${parentPath} / ${deptDisplay}` : deptDisplay;
      
      // 树节点显示：部门名称 (编码) - 用于下拉框中的树节点显示
      const title = deptCode ? `${deptName} (${deptCode})` : deptName;
      
      const node: any = {
        title,
        value: dept.id,
        key: String(dept.id),
        // 保存完整路径（包含编码），用于选中后显示
        // 使用 label 属性，配合 treeNodeLabelProp="label" 可以直接显示完整路径
        label: fullPath,
        // 保留 fullPath 用于 displayRender（如果需要自定义渲染）
        fullPath,
        // 保存部门名称（不含编码）
        deptName,
        // 保存部门编码
        deptCode,
      };
      
      // 递归处理子部门，传递完整路径
      if (dept.children && dept.children.length > 0) {
        const children = convertToTreeData(dept.children, onlyEnabled, excludeIds, fullPath);
        if (children.length > 0) {
          node.children = children;
        }
      }
      
      return node;
    });
}

/**
 * 在树数据中查找指定 value 的节点
 */
function findNodeByValue(treeData: any[], value: number | string): any | null {
  for (const node of treeData) {
    if (String(node.value) === String(value)) {
      return node;
    }
    if (node.children && node.children.length > 0) {
      const found = findNodeByValue(node.children, value);
      if (found) {
        return found;
      }
    }
  }
  return null;
}

/**
 * 部门选择组件
 */
export default function DepartmentSelect({
  value,
  onChange,
  disabled = false,
  placeholder,
  allowClear = true,
  style,
  className,
  loading: externalLoading,
  onlyEnabled = false,
  excludeIds,
  treeDefaultExpandAll = false,
  showSearch = true,
  filterTreeNode,
  treeLine = false,
  maxTagCount,
  dropdownStyle,
}: DepartmentSelectProps) {
  const { t } = useTranslation();
  const [departments, setDepartments] = useState<Department[]>([]);
  const [loading, setLoading] = useState(false);
  
  // 加载部门树
  useEffect(() => {
    loadDepartments();
  }, []);
  
  const loadDepartments = async () => {
    setLoading(true);
    try {
      const response = await getDepartmentTree();
      setDepartments(response.data || []);
    } catch (error) {
      console.error('Failed to load departments:', error);
    } finally {
      setLoading(false);
    }
  };
  
  // 转换为 TreeSelect 格式
  const treeData = useMemo(() => {
    return convertToTreeData(departments, onlyEnabled, excludeIds);
  }, [departments, onlyEnabled, excludeIds]);
  
  // 默认过滤函数
  const defaultFilterTreeNode = (inputValue: string, node: any) => {
    if (!inputValue) return true;
    const searchText = inputValue.toLowerCase();
    const title = node.title as string;
    const fullPath = node.fullPath as string;
    // 同时搜索标题和完整路径
    return (
      title?.toLowerCase().includes(searchText) ||
      fullPath?.toLowerCase().includes(searchText)
    ) ?? false;
  };
  
  // 自定义显示渲染函数：显示完整路径
  const displayRender = useMemo(() => {
    return (label: React.ReactNode, selectedNode: any) => {
      if (!value) {
        return label;
      }
      
      // 从 treeData 中查找选中的节点
      const node = findNodeByValue(treeData, value);
      
      if (node && node.fullPath) {
        // 显示完整路径，更直观
        // 例如：选择"前端组"时显示"技术部 / 开发组 / 前端组"
        return (
          <span title={node.fullPath} style={{ display: 'inline-block', width: '100%' }}>
            {node.fullPath}
          </span>
        );
      }
      
      // 如果找不到节点，返回原始标签
      return label;
    };
  }, [treeData, value]);
  
  const isLoading = externalLoading !== undefined ? externalLoading : loading;
  
  return (
    <TreeSelect
      value={value}
      onChange={onChange}
      disabled={disabled}
      placeholder={placeholder || t('common.pleaseSelect', { field: t('user.department') })}
      treeData={treeData}
      allowClear={allowClear}
      style={style}
      className={className}
      loading={isLoading}
      showSearch={showSearch}
      treeDefaultExpandAll={treeDefaultExpandAll}
      filterTreeNode={filterTreeNode || defaultFilterTreeNode}
      treeLine={treeLine}
      maxTagCount={maxTagCount}
      dropdownStyle={dropdownStyle}
      notFoundContent={isLoading ? <Spin size="small" /> : null}
      // 使用 label 属性显示完整路径（更简洁高效）
      // 根据 Ant Design 文档，treeNodeLabelProp 可以指定选中节点显示的属性
      treeNodeLabelProp="label"
      // 如果需要自定义渲染，可以使用 displayRender
      // displayRender={displayRender}
    />
  );
}
