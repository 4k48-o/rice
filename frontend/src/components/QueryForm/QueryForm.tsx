/**
 * 查询表单组件（带标题）
 */
import { ReactNode } from 'react';
import { Card } from 'antd';

interface QueryFormProps {
  title?: string;
  children: ReactNode;
  style?: React.CSSProperties;
}

import { useTranslation } from 'react-i18next';

export default function QueryForm({ title, children, style }: QueryFormProps) {
  const { t } = useTranslation();
  const defaultTitle = title || t('common.queryCondition');
  return (
    <Card title={defaultTitle} size="small" style={{ marginBottom: 16, ...style }}>
      {children}
    </Card>
  );
}

