/**
 * 菜单列表页面
 */
import { useState, useEffect } from 'react';
import { Tree, Button, Space, message, Skeleton, Card } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, ReloadOutlined } from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import { Permission } from '@/components/Permission/Permission';
import { useDebounce } from '@/hooks/useDebounce';
import { SearchInput } from '@/components/SearchInput';
import type { DataNode } from 'antd/es/tree';

export default function MenuList() {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(false);
  const [treeData, setTreeData] = useState<DataNode[]>([]);

  const loadMenus = async () => {
    setLoading(true);
    try {
      // TODO: 调用菜单树API
      // const response = await getMenuTree();
      // setTreeData(convertToTreeData(response.data));
      message.info(t('menu.menuManagementDeveloping'));
    } catch (error: any) {
      message.error(error.message || t('menu.loadMenuListFailed'));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadMenus();
  }, []);

  // 防抖的刷新函数
  const debouncedLoadMenus = useDebounce(loadMenus, 300);

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
        <Space>
          <SearchInput placeholder={t('menu.searchMenu')} style={{ width: 300 }} />
        </Space>
        <Space>
          <Button icon={<ReloadOutlined />} onClick={debouncedLoadMenus} loading={loading}>
            {t('common.refresh')}
          </Button>
          <Permission permission="menu:create">
            <Button type="primary" icon={<PlusOutlined />}>
              {t('menu.createMenu')}
            </Button>
          </Permission>
        </Space>
      </div>

      <Card>
        {loading && treeData.length === 0 ? (
          <Skeleton active paragraph={{ rows: 10 }} />
        ) : (
          <Tree
            treeData={treeData}
            defaultExpandAll
            showLine
            loading={loading}
          />
        )}
      </Card>
    </div>
  );
}

