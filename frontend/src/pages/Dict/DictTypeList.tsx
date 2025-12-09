/**
 * 字典类型列表页面
 */
import { useState, useEffect } from 'react';
import { Table, Button, Space, Select, message, Popconfirm, Skeleton, Card, Row, Col } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, ReloadOutlined } from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import { getDictTypeList, deleteDictType } from '@/api/dict';
import { DictType, DictTypeListParams } from '@/types/dict';
import { formatStatus } from '@/utils/format';
import { Permission } from '@/components/Permission/Permission';
import { QueryForm } from '@/components/QueryForm';
import { SearchInput } from '@/components/SearchInput';
import DictTypeForm from './DictTypeForm';
import { useDebounce } from '@/hooks/useDebounce';

export default function DictTypeList() {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(false);
  const [dictTypes, setDictTypes] = useState<DictType[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [searchParams, setSearchParams] = useState<DictTypeListParams>({});
  const [formVisible, setFormVisible] = useState(false);
  const [editingDictType, setEditingDictType] = useState<DictType | null>(null);

  const loadDictTypes = async () => {
    setLoading(true);
    try {
      const params: DictTypeListParams = {
        page,
        page_size: pageSize,
        ...searchParams,
      };

      const response = await getDictTypeList(params);
      setDictTypes(response.data.items);
      setTotal(response.data.total);
    } catch (error: any) {
      message.error(error.message || t('dict.loadDictTypeListFailed'));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDictTypes();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, pageSize, searchParams]);

  const handleSearch = (value: string) => {
    setSearchParams({ ...searchParams, keyword: value });
    setPage(1);
  };

  const handleReset = () => {
    setSearchParams({});
    setPage(1);
  };

  // 防抖的查询和刷新函数
  const debouncedLoadDictTypes = useDebounce(loadDictTypes, 500);

  const handleDelete = async (id: string) => {
    try {
      await deleteDictType(id);
      message.success(t('common.deleteSuccess'));
      loadDictTypes();
    } catch (error: any) {
      message.error(error.message || t('common.deleteFailed'));
    }
  };

  const handleEdit = (dictType: DictType) => {
    setEditingDictType(dictType);
    setFormVisible(true);
  };

  const handleCreate = () => {
    setEditingDictType(null);
    setFormVisible(true);
  };

  const handleFormSuccess = () => {
    setFormVisible(false);
    setEditingDictType(null);
    loadDictTypes();
  };

  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 100,
      fixed: 'left' as const,
    },
    {
      title: t('dict.typeName'),
      dataIndex: 'name',
      key: 'name',
      width: 150,
    },
    {
      title: t('dict.typeCode'),
      dataIndex: 'code',
      key: 'code',
      width: 150,
    },
    {
      title: t('common.sort'),
      dataIndex: 'sort',
      key: 'sort',
      width: 100,
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
      title: t('common.remark'),
      dataIndex: 'remark',
      key: 'remark',
      ellipsis: true,
    },
    {
      title: t('common.action'),
      key: 'action',
      width: 200,
      fixed: 'right' as const,
      render: (_: any, record: DictType) => (
        <Space>
          <Permission permission="dict:update">
            <Button type="link" size="small" onClick={() => handleEdit(record)}>
              {t('common.edit')}
            </Button>
          </Permission>
          <Permission permission="dict:delete">
            <Popconfirm
              title={t('common.confirmDelete', { name: record.name })}
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
              <span style={{ minWidth: 80, flexShrink: 0 }}>{t('dict.searchType')}:</span>
              <SearchInput
                placeholder={t('dict.searchTypePlaceholder')}
                onSearch={handleSearch}
                style={{ flex: 1, width: '100%' }}
                allowClear
                value={searchParams.keyword || ''}
                onChange={(e) => {
                  const value = e.target.value;
                  if (value) {
                    setSearchParams({ ...searchParams, keyword: value });
                  } else {
                    const { keyword, ...rest } = searchParams;
                    setSearchParams(rest);
                  }
                }}
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
                  setPage(1);
                }}
              >
                <Select.Option value={1}>{t('common.normal')}</Select.Option>
                <Select.Option value={0}>{t('common.disabled')}</Select.Option>
              </Select>
            </div>
          </Col>
          <Col xs={24} sm={24} md={24} lg={24}>
            <Space>
              <Button type="primary" onClick={debouncedLoadDictTypes} loading={loading}>
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
          <Button icon={<ReloadOutlined />} onClick={debouncedLoadDictTypes} loading={loading}>
            {t('common.refresh')}
          </Button>
          <Permission permission="dict:create">
            <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
              {t('dict.createType')}
            </Button>
          </Permission>
        </Space>
      </div>

      {/* 列表区域 */}
      <Card>
        {loading && dictTypes.length === 0 ? (
          <Skeleton active paragraph={{ rows: 10 }} />
        ) : (
          <Table
            columns={columns}
            dataSource={dictTypes}
            rowKey="id"
            loading={loading}
            scroll={{ x: 1200 }}
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
        <DictTypeForm
          visible={formVisible}
          dictType={editingDictType}
          onCancel={() => {
            setFormVisible(false);
            setEditingDictType(null);
          }}
          onSuccess={handleFormSuccess}
        />
      )}
    </div>
  );
}

