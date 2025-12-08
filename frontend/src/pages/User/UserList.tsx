/**
 * 用户列表页面
 */
import { useState, useEffect } from 'react';
import { Table, Button, Space, Input, Select, DatePicker, message, Popconfirm, Skeleton, Card, Row, Col } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, ReloadOutlined } from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import { getUserList, deleteUser } from '@/api/user';
import { getDepartmentTree } from '@/api/department';
import { User, UserListParams } from '@/types/user';
import { Department } from '@/types/department';
import { formatDateTime, formatStatus, formatUserType } from '@/utils/format';
import { Permission } from '@/components/Permission/Permission';
import { QueryForm } from '@/components/QueryForm';
import UserForm from './UserForm';
import dayjs, { Dayjs } from 'dayjs';

const { Search } = Input;
const { RangePicker } = DatePicker;

export default function UserList() {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(false);
  const [users, setUsers] = useState<User[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [searchParams, setSearchParams] = useState<UserListParams>({});
  const [formVisible, setFormVisible] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [lastLoginRange, setLastLoginRange] = useState<[Dayjs | null, Dayjs | null] | null>(null);

  // 加载部门树
  const loadDepartments = async () => {
    try {
      const response = await getDepartmentTree();
      setDepartments(response.data || []);
    } catch (error) {
      console.error('Failed to load departments:', error);
    }
  };

  // 递归构建部门选项
  const buildDepartmentOptions = (depts: Department[]): any[] => {
    const options: any[] = [];
    depts.forEach((dept) => {
      // 后端返回的字段是 name，兼容处理 dept_name
      const deptName = dept.name || dept.dept_name || `部门-${dept.id}`;
      options.push({
        value: dept.id,
        label: deptName,
      });
      if (dept.children && dept.children.length > 0) {
        const childOptions = buildDepartmentOptions(dept.children);
        options.push(...childOptions);
      }
    });
    return options;
  };

  const loadUsers = async () => {
    setLoading(true);
    try {
      const params: UserListParams = {
        page,
        page_size: pageSize,
        ...searchParams,
      };

      // 处理最后登录时间范围
      if (lastLoginRange && lastLoginRange[0] && lastLoginRange[1]) {
        params.last_login_start = lastLoginRange[0].startOf('day').toISOString();
        params.last_login_end = lastLoginRange[1].endOf('day').toISOString();
      }

      const response = await getUserList(params);
      setUsers(response.data.items);
      setTotal(response.data.total);
    } catch (error: any) {
      message.error(error.message || t('user.loadUserListFailed'));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDepartments();
  }, []);

  useEffect(() => {
    loadUsers();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, pageSize, searchParams, lastLoginRange]);

  const handleSearch = (value: string) => {
    setSearchParams({ ...searchParams, username: value });
    setPage(1);
  };

  const handleReset = () => {
    setSearchParams({});
    setLastLoginRange(null);
    setPage(1);
  };

  const handleDelete = async (id: number) => {
    try {
      await deleteUser(id);
      message.success(t('common.deleteSuccess'));
      loadUsers();
    } catch (error: any) {
      message.error(error.message || t('common.deleteFailed'));
    }
  };

  const handleEdit = (user: User) => {
    setEditingUser(user);
    setFormVisible(true);
  };

  const handleCreate = () => {
    setEditingUser(null);
    setFormVisible(true);
  };

  const handleFormSuccess = () => {
    setFormVisible(false);
    setEditingUser(null);
    loadUsers();
  };

  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
    },
    {
      title: t('user.username'),
      dataIndex: 'username',
      key: 'username',
    },
    {
      title: t('user.realName'),
      dataIndex: 'real_name',
      key: 'real_name',
    },
    {
      title: t('user.email'),
      dataIndex: 'email',
      key: 'email',
    },
    {
      title: t('user.phone'),
      dataIndex: 'phone',
      key: 'phone',
    },
    {
      title: t('user.department'),
      dataIndex: 'dept_name',
      key: 'dept_name',
    },
    {
      title: t('user.userType'),
      dataIndex: 'user_type',
      key: 'user_type',
      render: (type: number) => formatUserType(type),
    },
    {
      title: t('user.status'),
      dataIndex: 'status',
      key: 'status',
      render: (status: number) => {
        const { text, color } = formatStatus(status);
        return <span style={{ color }}>{text}</span>;
      },
    },
    {
      title: t('user.lastLoginTime'),
      dataIndex: 'last_login_time',
      key: 'last_login_time',
      render: (time: string) => formatDateTime(time),
    },
    {
      title: t('common.action'),
      key: 'action',
      width: 200,
      render: (_: any, record: User) => (
        <Space>
          <Permission permission="user:detail">
            <Button type="link" size="small" onClick={() => handleEdit(record)}>
              {t('common.edit')}
            </Button>
          </Permission>
          <Permission permission="user:delete">
            <Popconfirm
              title={t('common.confirmDelete', { name: t('user.userManagement') })}
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
              <span style={{ minWidth: 80, flexShrink: 0 }}>{t('user.username')}:</span>
              <Search
                placeholder={t('user.searchUsername')}
                onSearch={handleSearch}
                style={{ flex: 1, width: '100%' }}
                allowClear
                value={searchParams.username || ''}
                onChange={(e) => {
                  const value = e.target.value;
                  if (value) {
                    setSearchParams({ ...searchParams, username: value });
                  } else {
                    const { username, ...rest } = searchParams;
                    setSearchParams(rest);
                  }
                }}
              />
            </div>
          </Col>
          <Col xs={24} sm={12} md={8} lg={6}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <span style={{ minWidth: 80, flexShrink: 0 }}>{t('user.email')}:</span>
              <Input
                placeholder={t('user.email')}
                style={{ flex: 1, width: '100%' }}
                allowClear
                value={searchParams.email}
                onChange={(e) => {
                  const value = e.target.value;
                  if (value) {
                    setSearchParams({ ...searchParams, email: value });
                  } else {
                    const { email, ...rest } = searchParams;
                    setSearchParams(rest);
                  }
                }}
                onPressEnter={() => {
                  setPage(1);
                  loadUsers();
                }}
              />
            </div>
          </Col>
          <Col xs={24} sm={12} md={8} lg={6}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <span style={{ minWidth: 80, flexShrink: 0 }}>{t('user.department')}:</span>
              <Select
                placeholder={t('user.department')}
                style={{ flex: 1, width: '100%' }}
                allowClear
                showSearch
                optionFilterProp="label"
                value={searchParams.dept_id}
                onChange={(value) => {
                  if (value !== undefined) {
                    setSearchParams({ ...searchParams, dept_id: value });
                  } else {
                    const { dept_id, ...rest } = searchParams;
                    setSearchParams(rest);
                  }
                  setPage(1);
                }}
                options={buildDepartmentOptions(departments)}
              />
            </div>
          </Col>
          <Col xs={24} sm={12} md={8} lg={6}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <span style={{ minWidth: 80, flexShrink: 0 }}>{t('user.userType')}:</span>
              <Select
                placeholder={t('user.userType')}
                style={{ flex: 1, width: '100%' }}
                allowClear
                value={searchParams.user_type}
                onChange={(value) => {
                  if (value !== undefined) {
                    setSearchParams({ ...searchParams, user_type: value });
                  } else {
                    const { user_type, ...rest } = searchParams;
                    setSearchParams(rest);
                  }
                  setPage(1);
                }}
              >
                <Select.Option value={0}>{t('user.superAdmin')}</Select.Option>
                <Select.Option value={1}>{t('user.tenantAdmin')}</Select.Option>
                <Select.Option value={2}>{t('user.normalUser')}</Select.Option>
              </Select>
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
                  setPage(1);
                }}
              >
                <Select.Option value={1}>{t('common.normal')}</Select.Option>
                <Select.Option value={0}>{t('common.disabled')}</Select.Option>
                <Select.Option value={2}>{t('common.locked')}</Select.Option>
              </Select>
            </div>
          </Col>
          <Col xs={24} sm={12} md={8} lg={6}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <span style={{ minWidth: 80, flexShrink: 0 }}>{t('user.lastLoginTime')}:</span>
              <RangePicker
                style={{ flex: 1, width: '100%' }}
                value={lastLoginRange}
                onChange={(dates) => {
                  setLastLoginRange(dates);
                  setPage(1);
                }}
                allowClear
              />
            </div>
          </Col>
          <Col xs={24} sm={24} md={24} lg={24}>
            <Space>
              <Button type="primary" onClick={() => loadUsers()}>
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
          <Button icon={<ReloadOutlined />} onClick={loadUsers} loading={loading}>
            {t('common.refresh')}
          </Button>
          <Permission permission="user:create">
            <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
              {t('user.createUser')}
            </Button>
          </Permission>
        </Space>
      </div>

      {/* 列表区域 */}
      <Card>
        {loading && users.length === 0 ? (
          <Skeleton active paragraph={{ rows: 10 }} />
        ) : (
          <Table
            columns={columns}
            dataSource={users}
            rowKey="id"
            loading={loading}
            pagination={{
              current: page,
              pageSize,
              total,
              showSizeChanger: true,
              showTotal: (total) => t('common.total', { total }),
              onChange: (page, pageSize) => {
                setPage(page);
                setPageSize(pageSize);
              },
            }}
          />
        )}
      </Card>

      {formVisible && (
        <UserForm
          visible={formVisible}
          user={editingUser}
          onCancel={() => {
            setFormVisible(false);
            setEditingUser(null);
          }}
          onSuccess={handleFormSuccess}
        />
      )}
    </div>
  );
}

