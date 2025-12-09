/**
 * 角色列表页面
 */
import { useState, useEffect } from 'react';
import { Table, Button, Space, Select, message, Popconfirm, Skeleton, Card, Row, Col } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, ReloadOutlined } from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import { Permission } from '@/components/Permission/Permission';
import { useDebounce } from '@/hooks/useDebounce';
import { SearchInput } from '@/components/SearchInput';
import { QueryForm } from '@/components/QueryForm';
import { getRoleList, deleteRole } from '@/api/role';
import { Role, RoleListParams } from '@/types/role';
import { formatDataScope } from '@/utils/format';
import { formatStatus } from '@/utils/format';
import RoleForm from './RoleForm';

export default function RoleList() {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(false);
  const [roles, setRoles] = useState<Role[]>([]);
  const [searchParams, setSearchParams] = useState<RoleListParams>({});
  const [formVisible, setFormVisible] = useState(false);
  const [editingRole, setEditingRole] = useState<Role | null>(null);

  const loadRoles = async () => {
    setLoading(true);
    try {
      const response = await getRoleList(searchParams);
      setRoles(response.data || []);
    } catch (error: any) {
      message.error(error.message || t('role.loadRoleListFailed'));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadRoles();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams]);

  // 防抖的查询和刷新函数
  const debouncedLoadRoles = useDebounce(loadRoles, 500);

  const handleSearch = (value: string) => {
    if (value) {
      setSearchParams({ ...searchParams, name: value });
    } else {
      const { name, ...rest } = searchParams;
      setSearchParams(rest);
    }
  };

  const handleReset = () => {
    setSearchParams({});
  };

  const handleDelete = async (id: string) => {
    try {
      await deleteRole(id);
      message.success(t('common.deleteSuccess'));
      loadRoles();
    } catch (error: any) {
      message.error(error.message || t('common.deleteFailed'));
    }
  };

  const handleEdit = (role: Role) => {
    setEditingRole(role);
    setFormVisible(true);
  };

  const handleCreate = () => {
    setEditingRole(null);
    setFormVisible(true);
  };

  const handleFormSuccess = () => {
    setFormVisible(false);
    setEditingRole(null);
    loadRoles();
  };

  const columns = [
    {
      title: t('common.id'),
      dataIndex: 'id',
      key: 'id',
      width: 80,
      fixed: 'left' as const,
    },
    {
      title: t('role.roleName'),
      dataIndex: 'name',
      key: 'name',
      width: 150,
    },
    {
      title: t('role.roleCode'),
      dataIndex: 'code',
      key: 'code',
      width: 150,
    },
    {
      title: t('role.dataScope'),
      dataIndex: 'data_scope',
      key: 'data_scope',
      width: 120,
      render: (scope: number) => formatDataScope(scope, t),
    },
    {
      title: t('common.status'),
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: number) => {
        const { text, color } = formatStatus(status);
        return <span style={{ color }}>{text}</span>;
      },
    },
    {
      title: t('common.action'),
      key: 'action',
      width: 200,
      fixed: 'right' as const,
      render: (_: any, record: Role) => (
        <Space>
          <Permission permission="role:update">
            <Button type="link" size="small" onClick={() => handleEdit(record)}>
              {t('common.edit')}
            </Button>
          </Permission>
          <Permission permission="role:delete">
            <Popconfirm
              title={t('common.confirmDelete', { name: t('role.roleManagement') })}
              onConfirm={() => handleDelete(record.id)}
            >
              <Button type="link" size="small" danger>
                {t('common.delete')}
              </Button>
            </Popconfirm>
          </Permission>
        </Space>
      ),
    },
  ];

  return (
    <div>
      {/* 查询区域 */}
      <QueryForm title={t('common.queryCondition')}>
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={12} md={8} lg={6}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <span style={{ minWidth: 80, flexShrink: 0 }}>{t('role.roleName')}:</span>
              <SearchInput
                placeholder={t('role.searchRole')}
                style={{ flex: 1, width: '100%' }}
                allowClear
                value={searchParams.name || ''}
                onChange={(e) => {
                  const value = e.target.value;
                  if (value) {
                    setSearchParams({ ...searchParams, name: value });
                  } else {
                    const { name, ...rest } = searchParams;
                    setSearchParams(rest);
                  }
                }}
                onSearch={handleSearch}
              />
            </div>
          </Col>
          <Col xs={24} sm={12} md={8} lg={6}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <span style={{ minWidth: 80, flexShrink: 0 }}>{t('common.status')}:</span>
              <Select
                placeholder={t('common.status')}
                style={{ flex: 1, width: '100%' }}
                allowClear
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
          </Col>
          <Col xs={24} sm={24} md={24} lg={24}>
            <Space>
              <Button type="primary" onClick={debouncedLoadRoles} loading={loading}>
                {t('common.search')}
              </Button>
              <Button onClick={handleReset}>
                {t('common.reset')}
              </Button>
            </Space>
          </Col>
        </Row>
      </QueryForm>

      {/* 操作区域 */}
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
        <div></div>
        <Space>
          <Button icon={<ReloadOutlined />} onClick={debouncedLoadRoles} loading={loading}>
            {t('common.refresh')}
          </Button>
          <Permission permission="role:create">
            <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
              {t('role.createRole')}
            </Button>
          </Permission>
        </Space>
      </div>

      {/* 列表区域 */}
      <Card>
        {loading && roles.length === 0 ? (
          <Skeleton active paragraph={{ rows: 10 }} />
        ) : (
          <Table
            columns={columns}
            dataSource={roles}
            rowKey="id"
            loading={loading}
            scroll={{ x: 1200 }}
            pagination={false}
          />
        )}
      </Card>

      {formVisible && (
        <RoleForm
          visible={formVisible}
          role={editingRole}
          onCancel={() => {
            setFormVisible(false);
            setEditingRole(null);
          }}
          onSuccess={handleFormSuccess}
        />
      )}
    </div>
  );
}
