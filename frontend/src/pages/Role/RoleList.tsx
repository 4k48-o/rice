/**
 * 角色列表页面
 */
import { useState, useEffect } from 'react';
import { Table, Button, Space, Input, message, Popconfirm } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, ReloadOutlined } from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import { Permission } from '@/components/Permission/Permission';

const { Search } = Input;

export default function RoleList() {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(false);
  const [roles, setRoles] = useState<any[]>([]);

  const loadRoles = async () => {
    setLoading(true);
    try {
      // TODO: 调用角色列表API
      // const response = await getRoleList();
      // setRoles(response.data);
      message.info(t('role.roleManagementDeveloping'));
    } catch (error: any) {
      message.error(error.message || t('role.loadRoleListFailed'));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadRoles();
  }, []);

  const columns = [
    {
      title: t('common.id'),
      dataIndex: 'id',
      key: 'id',
      width: 80,
    },
    {
      title: t('role.roleName'),
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: t('role.roleCode'),
      dataIndex: 'code',
      key: 'code',
    },
    {
      title: t('role.dataScope'),
      dataIndex: 'data_scope',
      key: 'data_scope',
      render: (scope: number) => {
        const scopeMap: Record<number, string> = {
          1: t('role.all'),
          2: t('role.deptAndSub'),
          3: t('role.deptOnly'),
          4: t('role.selfOnly'),
          5: t('role.custom'),
        };
        return scopeMap[scope] || t('common.unknown');
      },
    },
    {
      title: t('common.status'),
      dataIndex: 'status',
      key: 'status',
      render: (status: number) => (status === 1 ? t('common.normal') : t('common.disabled')),
    },
    {
      title: t('common.action'),
      key: 'action',
      width: 200,
      render: (_: any, record: any) => (
        <Space>
          <Permission permission="role:update">
            <Button type="link" size="small">
              {t('common.edit')}
            </Button>
          </Permission>
          <Permission permission="role:delete">
            <Popconfirm title={t('common.confirmDelete', { name: t('role.roleManagement') })}>
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
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
        <Space>
          <Search placeholder={t('role.searchRole')} style={{ width: 300 }} />
        </Space>
        <Space>
          <Button icon={<ReloadOutlined />} onClick={loadRoles}>
            {t('common.refresh')}
          </Button>
          <Permission permission="role:create">
            <Button type="primary" icon={<PlusOutlined />}>
              {t('role.createRole')}
            </Button>
          </Permission>
        </Space>
      </div>

      <Table
        columns={columns}
        dataSource={roles}
        rowKey="id"
        loading={loading}
        pagination={{
          showSizeChanger: true,
          showTotal: (total) => t('common.total', { total }),
        }}
      />
    </div>
  );
}

