/**
 * 主应用组件
 */
import { useEffect } from 'react';
import { RouterProvider } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import enUS from 'antd/locale/en_US';
import jaJP from 'antd/locale/ja_JP';
import { useTranslation } from 'react-i18next';
import { router } from './routes';
import './i18n';

function App() {
  const { i18n } = useTranslation();

  // 根据i18n语言设置Ant Design语言
  const getAntdLocale = () => {
    switch (i18n.language) {
      case 'en':
        return enUS;
      case 'ja':
        return jaJP;
      default:
        return zhCN;
    }
  };

  return (
    <ConfigProvider locale={getAntdLocale()}>
      <RouterProvider router={router} />
    </ConfigProvider>
  );
}

export default App;

