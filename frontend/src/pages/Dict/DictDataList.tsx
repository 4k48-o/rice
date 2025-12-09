/**
 * 字典数据列表页面
 */
import { useState, useEffect } from 'react';
import { Table, Button, Space, Select, message, Popconfirm, Skeleton, Card, Row, Col } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, ReloadOutlined } from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import { getDictDataList, deleteDictData, getDictTypeList } from '@/api/dict';
import { DictData, DictDataListParams } from '@/types/dict';
import { DictType } from '@/types/dict';
import { formatStatus } from '@/utils/format';
import { Permission } from '@/components/Permission/Permission';
import { QueryForm } from '@/components/QueryForm';
import { SearchInput } from '@/components/SearchInput';
import DictDataForm from './DictDataForm';
import { useDebounce } from '@/hooks/useDebounce';

export default function DictDataList() {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(false);
  const [dictData, setDictData] = useState<DictData[]>([]);
  const [dictTypes, setDictTypes] = useState<DictType[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [searchParams, setSearchParams] = useState<DictDataListParams>({});
  const [formVisible, setFormVisible] = useState(false);
  const [editingDictData, setEditingDictData] = useState<DictData | null>(null);

  // 加载字典类型列表（用于筛选）
  const loadDictTypes = async () => {
    try {
      const response = await getDictTypeList({ page: 1, page_size: 100, status: 1 });
      setDictTypes(response.data.items);
    } catch (error: any) {
      // 静默失败，不影响主流程
      console.error('Failed to load dict types:', error);
    }
  };

  useEffect(() => {
    loadDictTypes();
  }, []);

  const loadDictData = async () => {
    setLoading(true);
    try {
      const params: DictDataListParams = {
        page,
        page_size: pageSize,
        ...searchParams,
      };

      const response = await getDictDataList(params);
      setDictData(response.data.items);
      setTotal(response.data.total);
    } catch (error: any) {
      message.error(error.message || t('dict.loadDictDataListFailed'));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDictData();
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
  const debouncedLoadDictData = useDebounce(loadDictData, 500);

  const handleDelete = async (id: string) => {
    try {
      await deleteDictData(id);
      message.success(t('common.deleteSuccess'));
      loadDictData();
    } catch (error: any) {
      message.error(error.message || t('common.deleteFailed'));
    }
  };

  const handleEdit = (data: DictData) => {
    setEditingDictData(data);
    setFormVisible(true);
  };

  const handleCreate = () => {
    setEditingDictData(null);
    setFormVisible(true);
  };

  const handleFormSuccess = () => {
    setFormVisible(false);
    setEditingDictData(null);
    loadDictData();
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
      title: t('dict.selectType'),
      dataIndex: 'dict_type',
      key: 'dict_type',
      width: 150,
      render: (dictType: DictType | null) => dictType?.name || '-',
    },
    {
      title: t('dict.label'),
      dataIndex: 'label',
      key: 'label',
      width: 150,
    },
    {
      title: t('dict.value'),
      dataIndex: 'value',
      key: 'value',
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
      title: t('dict.cssClass'),
      dataIndex: 'css_class',
      key: 'css_class',
      width: 120,
    },
    {
      title: t('dict.color'),
      dataIndex: 'color',
      key: 'color',
      width: 100,
      render: (color: string) => (
        color ? (
          <span style={{ color }}>●</span>
        ) : '-'
      ),
    },
    {
      title: t('dict.icon'),
      dataIndex: 'icon',
      key: 'icon',
      width: 100,
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
      render: (_: any, record: DictData) => (
        <Space>
          <Permission permission="dict:update">
            <Button type="link" size="small" onClick={() => handleEdit(record)}>
              {t('common.edit')}
            </Button>
          </Permission>
          <Permission permission="dict:delete">
            <Popconfirm
              title={t('common.confirmDelete', { name: record.label })}
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
              <span style={{ minWidth: 80, flexShrink: 0 }}>{t('dict.searchData')}:</span>
              <SearchInput
                placeholder={t('dict.searchDataPlaceholder')}
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
              <span style={{ minWidth: 80, flexShrink: 0 }}>{t('dict.selectType')}:</span>
              <Select
                placeholder={t('dict.typePlaceholder')}
                style={{ flex: 1, width: '100%' }}
                allowClear
                value={searchParams.dict_type_id}
                onChange={(value) => {
                  if (value !== undefined) {
                    setSearchParams({ ...searchParams, dict_type_id: value });
                  } else {
                    const { dict_type_id, ...rest } = searchParams;
                    setSearchParams(rest);
                  }
                  setPage(1);
                }}
              >
                {dictTypes.map((type) => (
                  <Select.Option key={type.id} value={type.id}>
                    {type.name} ({type.code})
                  </Select.Option>
                ))}
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
              </Select>
            </div>
          </Col>
          <Col xs={24} sm={24} md={24} lg={24}>
            <Space>
              <Button type="primary" onClick={debouncedLoadDictData} loading={loading}>
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
          <Button icon={<ReloadOutlined />} onClick={debouncedLoadDictData} loading={loading}>
            {t('common.refresh')}
          </Button>
          <Permission permission="dict:create">
            <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
              {t('dict.createData')}
            </Button>
          </Permission>
        </Space>
      </div>

      {/* 列表区域 */}
      <Card>
        {loading && dictData.length === 0 ? (
          <Skeleton active paragraph={{ rows: 10 }} />
        ) : (
          <Table
            columns={columns}
            dataSource={dictData}
            rowKey="id"
            loading={loading}
            scroll={{ x: 1500 }}
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
        <DictDataForm
          visible={formVisible}
          dictData={editingDictData}
          onCancel={() => {
            setFormVisible(false);
            setEditingDictData(null);
          }}
          onSuccess={handleFormSuccess}
        />
      )}
    </div>
  );
}

