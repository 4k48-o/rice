/**
 * 菜单列表页面
 */
import { useState, useEffect } from 'react';
import { Tree, Button, Space, Input, message } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, ReloadOutlined } from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import { Permission } from '@/components/Permission/Permission';
import type { DataNode } from 'antd/es/tree';

const { Search } = Input;

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

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
        <Space>
          <Search placeholder={t('menu.searchMenu')} style={{ width: 300 }} />
        </Space>
        <Space>
          <Button icon={<ReloadOutlined />} onClick={loadMenus}>
            {t('common.refresh')}
          </Button>
          <Permission permission="menu:create">
            <Button type="primary" icon={<PlusOutlined />}>
              {t('menu.createMenu')}
            </Button>
          </Permission>
        </Space>
      </div>

      <Tree
        treeData={treeData}
        defaultExpandAll
        showLine
        loading={loading}
      />
    </div>
  );
}

