/**
 * 在线用户页面
 */
import { useState, useEffect } from 'react';
import { Table, Button, Space, message, Popconfirm, Skeleton, Card } from 'antd';
import { ReloadOutlined, DisconnectOutlined } from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import { getOnlineUsers, forceLogoutUser } from '@/api/logs';
import { Permission } from '@/components/Permission/Permission';
import { formatDateTime } from '@/utils/format';
import { useDebounce } from '@/hooks/useDebounce';

export default function OnlineUser() {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(false);
  const [users, setUsers] = useState<any[]>([]);

  const loadOnlineUsers = async () => {
    setLoading(true);
    try {
      const response = await getOnlineUsers();
      setUsers(response.data || []);
    } catch (error: any) {
      message.error(error.message || t('monitor.loadOnlineUserFailed'));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadOnlineUsers();
  }, []);

  // 防抖的刷新函数
  const debouncedLoadOnlineUsers = useDebounce(loadOnlineUsers, 300);

  const handleForceLogout = async (userId: number) => {
    try {
      await forceLogoutUser(userId);
      message.success(t('monitor.forceLogoutSuccess'));
      loadOnlineUsers();
    } catch (error: any) {
      message.error(error.message || t('monitor.forceLogoutFailed'));
    }
  };

  const columns = [
    {
      title: t('common.id'),
      dataIndex: 'user_id',
      key: 'user_id',
    },
    {
      title: t('monitor.username'),
      dataIndex: 'username',
      key: 'username',
    },
    {
      title: t('monitor.realName'),
      dataIndex: 'real_name',
      key: 'real_name',
    },
    {
      title: t('monitor.ipAddress'),
      dataIndex: 'ip',
      key: 'ip',
    },
    {
      title: t('monitor.location'),
      dataIndex: 'location',
      key: 'location',
    },
    {
      title: t('monitor.loginTime'),
      dataIndex: 'login_time',
      key: 'login_time',
      render: (time: string) => formatDateTime(time),
    },
    {
      title: t('monitor.lastActive'),
      dataIndex: 'last_active_time',
      key: 'last_active_time',
      render: (time: string) => formatDateTime(time),
    },
    {
      title: t('common.action'),
      key: 'action',
      width: 150,
      render: (_: any, record: any) => (
        <Permission permission="log:online:force-logout">
          <Popconfirm
            title={t('monitor.confirmForceLogout')}
            onConfirm={() => handleForceLogout(record.user_id)}
          >
            <Button type="link" size="small" danger icon={<DisconnectOutlined />}>
              {t('monitor.forceLogout')}
            </Button>
          </Popconfirm>
        </Permission>
      ),
    },
  ];

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
        <Space>
          <Button icon={<ReloadOutlined />} onClick={debouncedLoadOnlineUsers} loading={loading}>
            {t('common.refresh')}
          </Button>
        </Space>
      </div>

      <Card>
        {loading && users.length === 0 ? (
          <Skeleton active paragraph={{ rows: 10 }} />
        ) : (
          <Table
            columns={columns}
            dataSource={users}
            rowKey="user_id"
            loading={loading}
            pagination={false}
          />
        )}
      </Card>
    </div>
  );
}

