/**
 * 字典管理主页面
 * 使用Tabs切换字典类型和字典数据
 */
import { useState } from 'react';
import { Tabs } from 'antd';
import { useTranslation } from 'react-i18next';
import DictTypeList from './DictTypeList';
import DictDataList from './DictDataList';

export default function DictList() {
  const { t } = useTranslation();
  const [activeTab, setActiveTab] = useState('types');

  const tabItems = [
    {
      key: 'types',
      label: t('dict.typeManagement'),
      children: <DictTypeList />,
    },
    {
      key: 'data',
      label: t('dict.dataManagement'),
      children: <DictDataList />,
    },
  ];

  return (
    <div>
      <Tabs
        activeKey={activeTab}
        onChange={setActiveTab}
        items={tabItems}
      />
    </div>
  );
}

