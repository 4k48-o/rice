/**
 * 登录日志页面
 */
import { useState, useEffect } from 'react';
import { Table, Button, Space, Input, Select, DatePicker, message, Skeleton, Card } from 'antd';
import { ReloadOutlined } from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import { getLoginLogs } from '@/api/logs';
import { formatDateTime } from '@/utils/format';
import { useDebounce } from '@/hooks/useDebounce';
import { SearchInput } from '@/components/SearchInput';
import dayjs from 'dayjs';

const { RangePicker } = DatePicker;

export default function LoginLog() {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(false);
  const [logs, setLogs] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [searchParams, setSearchParams] = useState<any>({});

  const loadLogs = async () => {
    setLoading(true);
    try {
      const params: any = {
        page,
        page_size: pageSize,
        ...searchParams,
      };

      // 处理时间范围
      if (searchParams.dateRange) {
        params.start_time = searchParams.dateRange[0].toISOString();
        params.end_time = searchParams.dateRange[1].toISOString();
        delete params.dateRange;
      }

      const response = await getLoginLogs(params);
      setLogs(response.data.items || []);
      setTotal(response.data.total || 0);
    } catch (error: any) {
      message.error(error.message || t('monitor.loadLoginLogFailed'));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadLogs();
  }, [page, pageSize, searchParams]);

  // 防抖的刷新函数
  const debouncedLoadLogs = useDebounce(loadLogs, 300);

  const handleSearch = (value: string) => {
    setSearchParams({ ...searchParams, username: value });
    setPage(1);
  };

  const handleStatusChange = (value: number | undefined) => {
    setSearchParams({ ...searchParams, status: value });
    setPage(1);
  };

  const handleDateRangeChange = (dates: any) => {
    setSearchParams({ ...searchParams, dateRange: dates });
    setPage(1);
  };

  const columns = [
    {
      title: t('common.id'),
      dataIndex: 'id',
      key: 'id',
      width: 80,
    },
    {
      title: t('monitor.username'),
      dataIndex: 'username',
      key: 'username',
    },
    {
      title: t('common.status'),
      dataIndex: 'status',
      key: 'status',
      render: (status: number) => (
        <span style={{ color: status === 1 ? '#52c41a' : '#ff4d4f' }}>
          {status === 1 ? t('common.success') : t('common.failed')}
        </span>
      ),
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
      title: t('monitor.browser'),
      dataIndex: 'browser',
      key: 'browser',
    },
    {
      title: t('monitor.os'),
      dataIndex: 'os',
      key: 'os',
    },
    {
      title: t('monitor.message'),
      dataIndex: 'msg',
      key: 'msg',
    },
    {
      title: t('monitor.loginTime'),
      dataIndex: 'login_time',
      key: 'login_time',
      render: (time: string) => formatDateTime(time),
    },
  ];

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: 8 }}>
        <Space wrap>
          <SearchInput
            placeholder={t('user.searchUsername')}
            onSearch={handleSearch}
            style={{ width: 300 }}
            allowClear
          />
          <Select
            placeholder={t('common.status')}
            style={{ width: 120 }}
            allowClear
            onChange={handleStatusChange}
          >
            <Select.Option value={1}>{t('common.success')}</Select.Option>
            <Select.Option value={0}>{t('common.failed')}</Select.Option>
          </Select>
          <RangePicker
            showTime
            onChange={handleDateRangeChange}
            format="YYYY-MM-DD HH:mm:ss"
          />
        </Space>
        <Space>
          <Button icon={<ReloadOutlined />} onClick={debouncedLoadLogs} loading={loading}>
            {t('common.refresh')}
          </Button>
        </Space>
      </div>

      <Card>
        {loading && logs.length === 0 ? (
          <Skeleton active paragraph={{ rows: 10 }} />
        ) : (
          <Table
            columns={columns}
            dataSource={logs}
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
    </div>
  );
}

