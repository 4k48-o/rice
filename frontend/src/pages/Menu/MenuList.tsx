/**
 * 菜单列表页面
 */
import { useState, useEffect, useMemo } from 'react';
import { Tree, Button, Space, message, Skeleton, Card, Select, Popconfirm, Table, Radio } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, ReloadOutlined, TableOutlined, ApartmentOutlined, DownOutlined, UpOutlined } from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import { Permission } from '@/components/Permission/Permission';
import { useDebounce } from '@/hooks/useDebounce';
import { SearchInput } from '@/components/SearchInput';
import { QueryForm } from '@/components/QueryForm';
import { getMenuTree, deleteMenu } from '@/api/menu';
import { Menu, MenuListParams } from '@/types/menu';
import { formatStatus } from '@/utils/format';
import MenuForm from './MenuForm';
import type { DataNode } from 'antd/es/tree';
import type { ColumnsType } from 'antd/es/table';

type ViewMode = 'tree' | 'table';

export default function MenuList() {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(false);
  const [viewMode, setViewMode] = useState<ViewMode>('table');
  const [treeData, setTreeData] = useState<DataNode[]>([]);
  const [menuList, setMenuList] = useState<Menu[]>([]);
  const [originalTreeData, setOriginalTreeData] = useState<DataNode[]>([]);
  const [originalMenuList, setOriginalMenuList] = useState<Menu[]>([]);
  const [searchParams, setSearchParams] = useState<MenuListParams>({});
  const [formVisible, setFormVisible] = useState(false);
  const [editingMenu, setEditingMenu] = useState<Menu | null>(null);
  const [selectedKeys, setSelectedKeys] = useState<React.Key[]>([]);
  const [expandedKeys, setExpandedKeys] = useState<React.Key[]>([]);
  const [searchKeyword, setSearchKeyword] = useState<string>('');

  // 将菜单树转换为 Ant Design Tree 需要的格式
  const convertToTreeData = (menus: Menu[]): DataNode[] => {
    return menus.map((menu) => ({
      title: (
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span>
            {menu.icon && <span style={{ marginRight: 8 }}>{menu.icon}</span>}
            {menu.title} ({menu.name})
            {menu.type === 1 && <span style={{ marginLeft: 8, color: '#1890ff' }}>[{t('menu.directory')}]</span>}
            {menu.type === 2 && <span style={{ marginLeft: 8, color: '#52c41a' }}>[{t('menu.menu')}]</span>}
            {menu.type === 3 && <span style={{ marginLeft: 8, color: '#faad14' }}>[{t('menu.button')}]</span>}
            {menu.status === 0 && <span style={{ marginLeft: 8, color: '#ff4d4f' }}>[{t('common.disabled')}]</span>}
          </span>
          <Space>
            <Permission permission="menu:update">
              <Button
                type="link"
                size="small"
                icon={<EditOutlined />}
                onClick={(e) => {
                  e.stopPropagation();
                  handleEdit(menu);
                }}
              >
                {t('common.edit')}
              </Button>
            </Permission>
            <Permission permission="menu:delete">
              <Popconfirm
                title={t('common.confirmDelete', { name: menu.title })}
                onConfirm={(e) => {
                  e?.stopPropagation();
                  handleDelete(menu.id);
                }}
                onCancel={(e) => e?.stopPropagation()}
              >
                <Button
                  type="link"
                  size="small"
                  danger
                  icon={<DeleteOutlined />}
                  onClick={(e) => e.stopPropagation()}
                >
                  {t('common.delete')}
                </Button>
              </Popconfirm>
            </Permission>
          </Space>
        </div>
      ),
      key: menu.id,
      menuName: menu.name,
      menuTitle: menu.title,
      menuData: menu,
      children: menu.children ? convertToTreeData(menu.children) : undefined,
    }));
  };

  const loadMenus = async () => {
    setLoading(true);
    try {
      const response = await getMenuTree();
      const menus = response.data || [];
      setMenuList(menus);
      setOriginalMenuList(menus);
      
      const convertedData = convertToTreeData(menus);
      setTreeData(convertedData);
      setOriginalTreeData(convertedData);
      
      // 如果有搜索关键词，重新执行搜索
      if (searchKeyword.trim()) {
        if (viewMode === 'tree') {
          const filtered = filterTreeData(convertedData, searchKeyword);
          setTreeData(filtered);
          if (filtered.length > 0) {
            setExpandedKeys(getAllKeys(filtered));
          } else {
            setExpandedKeys([]);
          }
        } else {
          const filtered = filterTableData(menus, searchKeyword);
          setMenuList(filtered);
        }
      }
    } catch (error: any) {
      message.error(error.message || t('menu.loadMenuListFailed'));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadMenus();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // 防抖的刷新函数
  const debouncedLoadMenus = useDebounce(loadMenus, 300);

  const handleDelete = async (id: string) => {
    try {
      await deleteMenu(id);
      message.success(t('common.deleteSuccess'));
      loadMenus();
    } catch (error: any) {
      // 错误已在 request 拦截器中统一处理
    }
  };

  const handleEdit = (menu: Menu) => {
    setEditingMenu(menu);
    setFormVisible(true);
  };

  const handleCreate = () => {
    setEditingMenu(null);
    setFormVisible(true);
  };

  const handleFormSuccess = () => {
    setFormVisible(false);
    setEditingMenu(null);
    loadMenus();
  };

  // 过滤树数据
  const filterTreeData = (data: DataNode[], keyword: string): DataNode[] => {
    if (!keyword || !keyword.trim()) {
      return data;
    }

    if (!data || data.length === 0) {
      return [];
    }

    const lowerKeyword = keyword.toLowerCase().trim();
    const result: DataNode[] = [];

    const filterNode = (node: DataNode): DataNode | null => {
      const menuName = (node as any).menuName || '';
      const menuTitle = (node as any).menuTitle || '';
      const menu = (node as any).menuData as Menu;
      const path = menu?.path || '';
      
      const matches = 
        menuName.toLowerCase().includes(lowerKeyword) ||
        menuTitle.toLowerCase().includes(lowerKeyword) ||
        path.toLowerCase().includes(lowerKeyword);
      
      let filteredChildren: DataNode[] = [];
      if (node.children && node.children.length > 0) {
        filteredChildren = node.children
          .map(child => filterNode(child))
          .filter((child): child is DataNode => child !== null);
      }

      if (matches || filteredChildren.length > 0) {
        const filteredNode: DataNode = {
          ...node,
          menuName: (node as any).menuName,
          menuTitle: (node as any).menuTitle,
          menuData: (node as any).menuData,
        };
        
        if (filteredChildren.length > 0) {
          filteredNode.children = filteredChildren;
        } else {
          filteredNode.children = undefined;
        }
        
        return filteredNode;
      }

      return null;
    };

    data.forEach(node => {
      const filtered = filterNode(node);
      if (filtered) {
        result.push(filtered);
      }
    });

    return result;
  };

  // 获取所有需要展开的节点key
  const getAllKeys = (data: DataNode[]): React.Key[] => {
    const keys: React.Key[] = [];
    const traverse = (nodes: DataNode[]) => {
      nodes.forEach(node => {
        keys.push(node.key);
        if (node.children && node.children.length > 0) {
          traverse(node.children);
        }
      });
    };
    traverse(data);
    return keys;
  };

  // 全部展开
  const handleExpandAll = () => {
    if (treeData.length > 0) {
      const allKeys = getAllKeys(treeData);
      setExpandedKeys(allKeys);
    }
  };

  // 全部关闭
  const handleCollapseAll = () => {
    setExpandedKeys([]);
  };

  // 转换菜单数据为表格树形结构
  const convertToTableTree = (menus: Menu[], parentTitle: string = ''): Menu[] => {
    return menus.map((menu) => {
      const children = menu.children && menu.children.length > 0 
        ? convertToTableTree(menu.children, menu.title)
        : undefined;
      
      return {
        ...menu,
        parent_title: parentTitle,
        children: children,
      } as any;
    });
  };

  // 扁平化树形数据为表格数据（用于搜索时的扁平列表）
  const flattenMenus = (menus: Menu[], level: number = 0, parentTitle: string = ''): Menu[] => {
    const result: Menu[] = [];
    menus.forEach((menu) => {
      const { children, ...menuWithoutChildren } = menu;
      result.push({
        ...menuWithoutChildren,
        level,
        parent_title: parentTitle,
      } as any);
      if (children && children.length > 0) {
        result.push(...flattenMenus(children, level + 1, menu.title));
      }
    });
    return result;
  };

  // 过滤表格数据
  const filterTableData = (data: Menu[], keyword: string): Menu[] => {
    if (!keyword || !keyword.trim()) {
      return data;
    }
    const lowerKeyword = keyword.toLowerCase().trim();
    const flattened = flattenMenus(data);
    return flattened.filter((menu) => {
      const name = (menu.name || '').toLowerCase();
      const title = (menu.title || '').toLowerCase();
      const path = (menu.path || '').toLowerCase();
      return name.includes(lowerKeyword) || title.includes(lowerKeyword) || path.includes(lowerKeyword);
    });
  };

  // 处理搜索
  const handleSearch = (value: string) => {
    setSearchKeyword(value);
    if (!value.trim()) {
      // 恢复原始数据
      if (viewMode === 'tree') {
        if (originalTreeData.length > 0) {
          setTreeData(originalTreeData);
        }
        setExpandedKeys([]);
      } else {
        if (originalMenuList.length > 0) {
          setMenuList(originalMenuList);
        }
      }
    } else {
      if (viewMode === 'tree') {
        const sourceData = originalTreeData.length > 0 ? originalTreeData : treeData;
        const filtered = filterTreeData(sourceData, value);
        setTreeData(filtered);
        if (filtered.length > 0) {
          setExpandedKeys(getAllKeys(filtered));
        } else {
          setExpandedKeys([]);
        }
      } else {
        const sourceData = originalMenuList.length > 0 ? originalMenuList : menuList;
        const filtered = filterTableData(sourceData, value);
        setMenuList(filtered);
      }
    }
  };

  // 表格列定义
  const columns: ColumnsType<Menu> = [
    {
      title: '',
      key: 'expand',
      width: 50,
      fixed: 'left',
      render: () => null,
    },
    {
      title: t('menu.menuName'),
      dataIndex: 'name',
      key: 'name',
      width: 150,
    },
    {
      title: t('menu.menuTitle'),
      dataIndex: 'title',
      key: 'title',
      width: 150,
    },
    {
      title: t('menu.parentMenu'),
      dataIndex: 'parent_title',
      key: 'parent_title',
      width: 150,
      render: (text: string) => text || '-',
    },
    {
      title: t('menu.menuType'),
      dataIndex: 'type',
      key: 'type',
      width: 100,
      render: (type: number) => {
        const typeMap: Record<number, string> = {
          1: t('menu.directory'),
          2: t('menu.menu'),
          3: t('menu.button'),
        };
        const colorMap: Record<number, string> = {
          1: '#1890ff',
          2: '#52c41a',
          3: '#faad14',
        };
        return <span style={{ color: colorMap[type] }}>{typeMap[type] || '-'}</span>;
      },
    },
    {
      title: t('menu.path'),
      dataIndex: 'path',
      key: 'path',
      width: 200,
      render: (text: string) => text || '-',
    },
    {
      title: t('menu.component'),
      dataIndex: 'component',
      key: 'component',
      width: 200,
      render: (text: string) => text || '-',
    },
    {
      title: t('menu.icon'),
      dataIndex: 'icon',
      key: 'icon',
      width: 100,
      render: (text: string) => text || '-',
    },
    {
      title: t('menu.permissionCode'),
      dataIndex: 'permission_code',
      key: 'permission_code',
      width: 150,
      render: (text: string) => text || '-',
    },
    {
      title: t('menu.sort'),
      dataIndex: 'sort',
      key: 'sort',
      width: 80,
      align: 'center',
    },
    {
      title: t('common.status'),
      dataIndex: 'status',
      key: 'status',
      width: 100,
      align: 'center',
      render: (status: number) => {
        const { text, color } = formatStatus(status);
        return <span style={{ color }}>{text}</span>;
      },
    },
    {
      title: t('menu.visible'),
      dataIndex: 'visible',
      key: 'visible',
      width: 100,
      align: 'center',
      render: (visible: number) => (
        <span style={{ color: visible === 1 ? '#52c41a' : '#ff4d4f' }}>
          {visible === 1 ? t('menu.show') : t('menu.hide')}
        </span>
      ),
    },
    {
      title: t('common.action'),
      key: 'action',
      width: 150,
      fixed: 'right',
      render: (_: any, record: Menu) => (
        <Space size="small">
          <Permission permission="menu:update">
            <Button
              type="link"
              size="small"
              icon={<EditOutlined />}
              onClick={() => handleEdit(record)}
            >
              {t('common.edit')}
            </Button>
          </Permission>
          <Permission permission="menu:delete">
            <Popconfirm
              title={t('common.confirmDelete', { name: record.title })}
              onConfirm={() => handleDelete(record.id)}
            >
              <Button
                type="link"
                size="small"
                danger
                icon={<DeleteOutlined />}
              >
                {t('common.delete')}
              </Button>
            </Popconfirm>
          </Permission>
        </Space>
      ),
    },
  ];

  // 表格数据（树形结构）
  const tableData = useMemo(() => {
    return convertToTableTree(menuList);
  }, [menuList]);

  return (
    <div>
      {/* 查询区域 */}
      <QueryForm title={t('common.queryCondition')}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, flex: 1, minWidth: 300 }}>
            <span style={{ minWidth: 80, flexShrink: 0 }}>{t('menu.searchMenu')}:</span>
            <SearchInput
              placeholder={t('menu.searchMenu')}
              style={{ flex: 1, width: '100%', maxWidth: 300 }}
              allowClear
              value={searchKeyword}
              onChange={(e) => {
                const value = e.target.value;
                setSearchKeyword(value);
                if (!value) {
                  handleSearch('');
                }
              }}
              onSearch={handleSearch}
            />
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ minWidth: 80, flexShrink: 0 }}>{t('menu.menuType')}:</span>
            <Select
              placeholder={t('menu.selectMenuType')}
              allowClear
              style={{ width: 150 }}
              value={searchParams.menu_type}
              onChange={(value) => {
                if (value !== undefined) {
                  setSearchParams({ ...searchParams, menu_type: value });
                } else {
                  const { menu_type, ...rest } = searchParams;
                  setSearchParams(rest);
                }
              }}
            >
              <Select.Option value={1}>{t('menu.directory')}</Select.Option>
              <Select.Option value={2}>{t('menu.menu')}</Select.Option>
              <Select.Option value={3}>{t('menu.button')}</Select.Option>
            </Select>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ minWidth: 80, flexShrink: 0 }}>{t('common.status')}:</span>
            <Select
              placeholder={t('menu.selectStatus')}
              allowClear
              style={{ width: 150 }}
              value={searchParams.status}
              onChange={(value) => {
                if (value !== undefined) {
                  setSearchParams({ ...searchParams, status: value });
                } else {
                  const { status, ...rest } = searchParams;
                  setSearchParams(rest);
                }
              }}
            >
              <Select.Option value={1}>{t('common.normal')}</Select.Option>
              <Select.Option value={0}>{t('common.disabled')}</Select.Option>
            </Select>
          </div>
        </div>
      </QueryForm>

      {/* 操作区域 */}
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Space>
          <Radio.Group
            value={viewMode}
            onChange={(e) => {
              const mode = e.target.value;
              setViewMode(mode);
              // 切换视图时重新加载数据
              if (mode === 'tree') {
                if (originalTreeData.length > 0) {
                  if (searchKeyword.trim()) {
                    const filtered = filterTreeData(originalTreeData, searchKeyword);
                    setTreeData(filtered);
                    if (filtered.length > 0) {
                      setExpandedKeys(getAllKeys(filtered));
                    }
                  } else {
                    setTreeData(originalTreeData);
                    setExpandedKeys([]);
                  }
                }
              } else {
                if (originalMenuList.length > 0) {
                  if (searchKeyword.trim()) {
                    const filtered = filterTableData(originalMenuList, searchKeyword);
                    setMenuList(filtered);
                  } else {
                    setMenuList(originalMenuList);
                  }
                }
              }
            }}
            buttonStyle="solid"
          >
            <Radio.Button value="tree">
              <ApartmentOutlined /> {t('menu.treeView')}
            </Radio.Button>
            <Radio.Button value="table">
              <TableOutlined /> {t('menu.tableView')}
            </Radio.Button>
          </Radio.Group>
          {viewMode === 'tree' && (
            <>
              <Button icon={<DownOutlined />} onClick={handleExpandAll}>
                {t('menu.expandAll')}
              </Button>
              <Button icon={<UpOutlined />} onClick={handleCollapseAll}>
                {t('menu.collapseAll')}
              </Button>
            </>
          )}
        </Space>
        <Space>
          <Button icon={<ReloadOutlined />} onClick={debouncedLoadMenus} loading={loading}>
            {t('common.refresh')}
          </Button>
          <Permission permission="menu:create">
            <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
              {t('menu.createMenu')}
            </Button>
          </Permission>
        </Space>
      </div>

      {/* 列表区域 */}
      <Card>
        {loading && (viewMode === 'tree' ? treeData.length === 0 : menuList.length === 0) ? (
          <Skeleton active paragraph={{ rows: 10 }} />
        ) : viewMode === 'tree' ? (
          <Tree
            treeData={treeData}
            selectedKeys={selectedKeys}
            onSelect={setSelectedKeys}
            expandedKeys={expandedKeys}
            onExpand={(keys) => {
              setExpandedKeys(keys as React.Key[]);
            }}
            showLine
            loading={loading}
            blockNode
          />
        ) : (
          <Table
            columns={columns}
            dataSource={tableData}
            rowKey="id"
            loading={loading}
            scroll={{ x: 1500 }}
            pagination={{
              showSizeChanger: true,
              showTotal: (total) => t('common.total', { total }),
            }}
            defaultExpandAllRows={false}
            indentSize={20}
            expandable={{
              expandIconColumnIndex: 0,
              expandIcon: ({ expanded, onExpand, record }) => {
                const hasChildren = record.children && record.children.length > 0;
                if (!hasChildren) {
                  return <span style={{ display: 'inline-block', width: 24 }} />;
                }
                return (
                  <span
                    onClick={(e) => onExpand(record, e)}
                    style={{ cursor: 'pointer', display: 'inline-block', width: 24, textAlign: 'center' }}
                  >
                    {expanded ? '−' : '+'}
                  </span>
                );
              },
            }}
          />
        )}
      </Card>

      <MenuForm
        visible={formVisible}
        menu={editingMenu}
        menuTree={originalMenuList}
        onCancel={() => {
          setFormVisible(false);
          setEditingMenu(null);
        }}
        onSuccess={handleFormSuccess}
      />
    </div>
  );
}
