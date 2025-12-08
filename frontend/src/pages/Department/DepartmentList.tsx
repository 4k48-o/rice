/**
 * 部门列表页面
 */
import { useState, useEffect, useMemo } from 'react';
import { Tree, Button, Space, Input, message, Popconfirm, Skeleton, Card, Table, Radio } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, ReloadOutlined, TableOutlined, ApartmentOutlined, DownOutlined, UpOutlined } from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import { getDepartmentTree, deleteDepartment } from '@/api/department';
import { Department } from '@/types/department';
import { Permission } from '@/components/Permission/Permission';
import { QueryForm } from '@/components/QueryForm';
import DepartmentForm from './DepartmentForm';
import type { DataNode } from 'antd/es/tree';
import type { ColumnsType } from 'antd/es/table';

type ViewMode = 'tree' | 'table';

export default function DepartmentList() {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(false);
  const [viewMode, setViewMode] = useState<ViewMode>('table');
  const [departments, setDepartments] = useState<Department[]>([]);
  const [treeData, setTreeData] = useState<DataNode[]>([]);
  const [originalTreeData, setOriginalTreeData] = useState<DataNode[]>([]);
  const [originalDepartments, setOriginalDepartments] = useState<Department[]>([]);
  const [formVisible, setFormVisible] = useState(false);
  const [editingDept, setEditingDept] = useState<Department | null>(null);
  const [selectedKeys, setSelectedKeys] = useState<React.Key[]>([]);
  const [searchKeyword, setSearchKeyword] = useState<string>('');
  const [expandedKeys, setExpandedKeys] = useState<React.Key[]>([]);

  const loadDepartments = async () => {
    setLoading(true);
    try {
      const response = await getDepartmentTree();
      const deptData = response.data;
      setDepartments(deptData);
      setOriginalDepartments(deptData);
      
      const convertedData = convertToTreeData(deptData);
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
          const filtered = filterTableData(deptData, searchKeyword);
          setDepartments(filtered);
        }
      }
    } catch (error: any) {
      message.error(error.message || t('department.loadDepartmentListFailed'));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDepartments();
  }, []);

  // 转换部门数据为Tree组件格式
  const convertToTreeData = (departments: Department[]): DataNode[] => {
    return departments.map((dept) => {
      const deptName = dept.name || dept.dept_name || `部门-${dept.id}`;
      return {
        title: (
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span>{deptName}</span>
            <Space>
              <Permission permission="dept:update">
                <Button
                  type="link"
                  size="small"
                  icon={<EditOutlined />}
                  onClick={(e) => {
                    e.stopPropagation();
                    handleEdit(dept);
                  }}
                >
                  {t('common.edit')}
                </Button>
              </Permission>
              <Permission permission="dept:delete">
                <Popconfirm
                  title={t('common.confirmDelete', { name: t('department.departmentManagement') })}
                  onConfirm={(e) => {
                    e?.stopPropagation();
                    handleDelete(dept.id);
                  }}
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
        key: dept.id.toString(),
        // 添加原始部门名称用于搜索
        deptName: deptName,
        // 保存完整的部门数据，用于编辑
        departmentData: dept,
        children: dept.children ? convertToTreeData(dept.children) : undefined,
      };
    });
  };

  const handleDelete = async (id: number | string) => {
    try {
      // 保持 ID 为字符串类型，避免 JavaScript 精度丢失
      // 后端会接收字符串并转换为 BigInteger
      const deptId = String(id);
      if (!deptId) {
        console.error('Invalid department ID for delete:', id);
        message.error(t('common.invalidId') || '无效的部门ID');
        return;
      }
      await deleteDepartment(deptId);
      message.success(t('common.deleteSuccess'));
      loadDepartments();
    } catch (error: any) {
      message.error(error.message || t('common.deleteFailed'));
    }
  };

  const handleEdit = (dept: Department) => {
    // 验证部门对象是否包含有效的 ID
    if (!dept || !dept.id) {
      console.error('Invalid department object:', dept);
      message.error(t('common.invalidData') || '部门数据无效');
      return;
    }
    console.log('Editing department:', { id: dept.id, name: dept.name || dept.dept_name, dept });
    setEditingDept(dept);
    setFormVisible(true);
  };

  const handleCreate = () => {
    setEditingDept(null);
    setFormVisible(true);
  };

  const handleFormSuccess = () => {
    setFormVisible(false);
    setEditingDept(null);
    loadDepartments();
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
      // 从节点的 deptName 属性中获取部门名称
      const deptName = (node as any).deptName || '';
      const matches = deptName && deptName.toLowerCase().includes(lowerKeyword);
      
      // 如果有子节点，递归过滤
      let filteredChildren: DataNode[] = [];
      if (node.children && node.children.length > 0) {
        filteredChildren = node.children
          .map(child => filterNode(child))
          .filter((child): child is DataNode => child !== null);
      }

      // 如果当前节点匹配或有匹配的子节点，则包含此节点
      if (matches || filteredChildren.length > 0) {
        const filteredNode: DataNode = {
          ...node,
          // 确保保留 deptName 和 departmentData 属性
          deptName: (node as any).deptName,
          departmentData: (node as any).departmentData,
        };
        
        // 只有当有过滤后的子节点时才设置 children
        if (filteredChildren.length > 0) {
          filteredNode.children = filteredChildren;
        } else {
          // 如果当前节点匹配但没有子节点，移除 children
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

  // 转换部门数据为表格树形结构（保留 children）
  const convertToTableTree = (depts: Department[], parentName: string = ''): Department[] => {
    return depts.map((dept) => {
      const deptName = dept.name || dept.dept_name || `部门-${dept.id}`;
      const deptCode = dept.code || dept.dept_code || '';
      const children = dept.children && dept.children.length > 0 
        ? convertToTableTree(dept.children, deptName)
        : undefined;
      
      return {
        ...dept,
        name: deptName,
        dept_name: deptName,
        code: deptCode,
        dept_code: deptCode,
        parent_name: parentName,
        children: children,
      } as any;
    });
  };

  // 扁平化树形数据为表格数据（用于搜索时的扁平列表）
  const flattenDepartments = (depts: Department[], level: number = 0, parentName: string = ''): Department[] => {
    const result: Department[] = [];
    depts.forEach((dept) => {
      const deptName = dept.name || dept.dept_name || `部门-${dept.id}`;
      const deptCode = dept.code || dept.dept_code || '';
      // 创建一个新对象，排除 children 属性，用于搜索过滤
      const { children, ...deptWithoutChildren } = dept;
      result.push({
        ...deptWithoutChildren,
        name: deptName,
        dept_name: deptName,
        code: deptCode,
        dept_code: deptCode,
        // 添加层级和父级名称用于显示
        level,
        parent_name: parentName,
      } as any);
      if (children && children.length > 0) {
        result.push(...flattenDepartments(children, level + 1, deptName));
      }
    });
    return result;
  };

  // 过滤表格数据
  const filterTableData = (data: Department[], keyword: string): Department[] => {
    if (!keyword || !keyword.trim()) {
      return data;
    }
    const lowerKeyword = keyword.toLowerCase().trim();
    const flattened = flattenDepartments(data);
    return flattened.filter((dept) => {
      const deptName = (dept.name || dept.dept_name || '').toLowerCase();
      return deptName.includes(lowerKeyword);
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
        // 清空展开的节点
        setExpandedKeys([]);
      } else {
        if (originalDepartments.length > 0) {
          setDepartments(originalDepartments);
        }
      }
    } else {
      if (viewMode === 'tree') {
        // 使用原始数据进行过滤
        const sourceData = originalTreeData.length > 0 ? originalTreeData : treeData;
        const filtered = filterTreeData(sourceData, value);
        setTreeData(filtered);
        // 如果有搜索结果，展开所有节点以便查看
        if (filtered.length > 0) {
          setExpandedKeys(getAllKeys(filtered));
        } else {
          setExpandedKeys([]);
        }
      } else {
        const sourceData = originalDepartments.length > 0 ? originalDepartments : departments;
        const filtered = filterTableData(sourceData, value);
        setDepartments(filtered);
      }
    }
  };

  // 表格列定义
  const columns: ColumnsType<Department> = [
    {
      title: '',
      key: 'expand',
      width: 50,
      fixed: 'left',
      render: () => null, // 展开图标会显示在这里
    },
    {
      title: t('department.departmentCode'),
      dataIndex: 'code',
      key: 'code',
      width: 120,
      render: (text: string, record: Department) => {
        return text || record.dept_code || '-';
      },
    },
    {
      title: t('department.departmentName'),
      dataIndex: 'name',
      key: 'name',
      width: 200,
      render: (text: string, record: Department) => {
        return text || record.dept_name || `部门-${record.id}`;
      },
    },
    {
      title: t('department.parentDepartment'),
      dataIndex: 'parent_name',
      key: 'parent_name',
      width: 150,
      render: (text: string) => text || '-',
    },
    {
      title: t('department.leader'),
      dataIndex: 'leader_name',
      key: 'leader_name',
      width: 120,
      render: (text: string) => text || '-',
    },
    {
      title: t('department.phone'),
      dataIndex: 'phone',
      key: 'phone',
      width: 120,
      render: (text: string) => text || '-',
    },
    {
      title: t('department.email'),
      dataIndex: 'email',
      key: 'email',
      width: 180,
      render: (text: string) => text || '-',
    },
    {
      title: t('department.sortOrder'),
      dataIndex: 'sort_order',
      key: 'sort_order',
      width: 100,
      align: 'center',
    },
    {
      title: t('common.status'),
      dataIndex: 'status',
      key: 'status',
      width: 100,
      align: 'center',
      render: (status: number) => (
        <span style={{ color: status === 1 ? '#52c41a' : '#ff4d4f' }}>
          {status === 1 ? t('common.normal') : t('common.disabled')}
        </span>
      ),
    },
    {
      title: t('common.action'),
      key: 'action',
      width: 150,
      fixed: 'right',
      render: (_: any, record: Department) => (
        <Space size="small">
          <Permission permission="dept:update">
            <Button
              type="link"
              size="small"
              icon={<EditOutlined />}
              onClick={() => handleEdit(record)}
            >
              {t('common.edit')}
            </Button>
          </Permission>
          <Permission permission="dept:delete">
            <Popconfirm
              title={t('common.confirmDelete', { name: t('department.departmentManagement') })}
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
    return convertToTableTree(departments);
  }, [departments]);

  return (
    <div>
      {/* 查询区域 */}
      <QueryForm title={t('common.queryCondition')}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span style={{ minWidth: 80, flexShrink: 0 }}>{t('department.departmentName')}:</span>
          <Input.Search
            placeholder={t('department.searchDepartment')}
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
                if (originalDepartments.length > 0) {
                  if (searchKeyword.trim()) {
                    const filtered = filterTableData(originalDepartments, searchKeyword);
                    setDepartments(filtered);
                  } else {
                    setDepartments(originalDepartments);
                  }
                }
              }
            }}
            buttonStyle="solid"
          >
            <Radio.Button value="tree">
              <ApartmentOutlined /> {t('department.treeView')}
            </Radio.Button>
            <Radio.Button value="table">
              <TableOutlined /> {t('department.tableView')}
            </Radio.Button>
          </Radio.Group>
          {viewMode === 'tree' && (
            <>
              <Button icon={<DownOutlined />} onClick={handleExpandAll}>
                {t('department.expandAll')}
              </Button>
              <Button icon={<UpOutlined />} onClick={handleCollapseAll}>
                {t('department.collapseAll')}
              </Button>
            </>
          )}
        </Space>
        <Space>
          <Button icon={<ReloadOutlined />} onClick={loadDepartments} loading={loading}>
            {t('common.refresh')}
          </Button>
          <Permission permission="dept:create">
            <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
              {t('department.createDepartment')}
            </Button>
          </Permission>
        </Space>
      </div>

      {/* 列表区域 */}
      <Card>
        {loading && (viewMode === 'tree' ? treeData.length === 0 : departments.length === 0) ? (
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
          />
        ) : (
          <Table
            columns={columns}
            dataSource={tableData}
            rowKey="id"
            loading={loading}
            scroll={{ x: 1200 }}
            pagination={{
              showSizeChanger: true,
              showTotal: (total) => t('common.total', { total }),
            }}
            defaultExpandAllRows={false}
            indentSize={20}
            expandable={{
              expandIconColumnIndex: 0, // 将展开图标放在第一列
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

      {formVisible && (
        <DepartmentForm
          visible={formVisible}
          department={editingDept}
          onCancel={() => {
            setFormVisible(false);
            setEditingDept(null);
          }}
          onSuccess={handleFormSuccess}
        />
      )}
    </div>
  );
}

