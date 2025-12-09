/**
 * 图标选择器组件
 * 
 * 提供常用 Ant Design 图标的选择功能
 */
import { useState, useEffect } from 'react';
import { Input, Popover, Space, Row, Col, Button } from 'antd';
import { AppstoreOutlined } from '@ant-design/icons';
import * as Icons from '@ant-design/icons';
import { useTranslation } from 'react-i18next';

const { Search } = Input;

// 常用图标列表（去重并分类）
const commonIcons = [
  // 基础图标
  'HomeOutlined',
  'UserOutlined',
  'TeamOutlined',
  'SettingOutlined',
  'MenuOutlined',
  'ApartmentOutlined',
  
  // 文件相关
  'FileOutlined',
  'FileTextOutlined',
  'FileImageOutlined',
  'FilePdfOutlined',
  'FileWordOutlined',
  'FileExcelOutlined',
  'FilePptOutlined',
  'FileZipOutlined',
  'FolderOutlined',
  'FolderOpenOutlined',
  'InboxOutlined',
  
  // 数据相关
  'DatabaseOutlined',
  'TableOutlined',
  'BarChartOutlined',
  'LineChartOutlined',
  'PieChartOutlined',
  'AreaChartOutlined',
  'DashboardOutlined',
  
  // 设备相关
  'DesktopOutlined',
  'LaptopOutlined',
  'TabletOutlined',
  'MobileOutlined',
  'PhoneOutlined',
  'MonitorOutlined',
  'CameraOutlined',
  'VideoCameraOutlined',
  
  // 操作相关
  'PlusOutlined',
  'MinusOutlined',
  'EditOutlined',
  'DeleteOutlined',
  'CopyOutlined',
  'ScissorOutlined',
  'SnippetsOutlined',
  'SaveOutlined',
  'DownloadOutlined',
  'UploadOutlined',
  'ImportOutlined',
  'ExportOutlined',
  'ReloadOutlined',
  'SyncOutlined',
  'RedoOutlined',
  'UndoOutlined',
  'SearchOutlined',
  'FilterOutlined',
  'SortAscendingOutlined',
  'SortDescendingOutlined',
  
  // 列表相关
  'BarsOutlined',
  'UnorderedListOutlined',
  'OrderedListOutlined',
  
  // 应用相关
  'AppstoreOutlined',
  'CloudOutlined',
  'ShopOutlined',
  'ShoppingOutlined',
  'ShoppingCartOutlined',
  
  // 金融相关
  'DollarOutlined',
  'EuroOutlined',
  'PoundOutlined',
  'YenOutlined',
  'WalletOutlined',
  'AccountBookOutlined',
  'CalculatorOutlined',
  'BankOutlined',
  'CreditCardOutlined',
  'CarOutlined',
  
  // 消息通知
  'MailOutlined',
  'MessageOutlined',
  'NotificationOutlined',
  'BellOutlined',
  'SoundOutlined',
  'CustomerServiceOutlined',
  
  // 状态图标
  'QuestionCircleOutlined',
  'InfoCircleOutlined',
  'CheckCircleOutlined',
  'CloseCircleOutlined',
  'ExclamationCircleOutlined',
  'WarningOutlined',
  'StopOutlined',
  'CloseOutlined',
  'CheckOutlined',
  'EyeOutlined',
  'EyeInvisibleOutlined',
  
  // 安全相关
  'LockOutlined',
  'UnlockOutlined',
  'KeyOutlined',
  'SafetyOutlined',
  'SafetyCertificateOutlined',
  'ShieldOutlined',
  
  // 工具相关
  'ToolOutlined',
  'BuildOutlined',
  'CodeOutlined',
  'BugOutlined',
  'ApiOutlined',
  
  // 方向箭头
  'UpOutlined',
  'DownOutlined',
  'LeftOutlined',
  'RightOutlined',
  'ArrowUpOutlined',
  'ArrowDownOutlined',
  'ArrowLeftOutlined',
  'ArrowRightOutlined',
  'CaretUpOutlined',
  'CaretDownOutlined',
  'CaretLeftOutlined',
  'CaretRightOutlined',
  'DoubleLeftOutlined',
  'DoubleRightOutlined',
  'VerticalLeftOutlined',
  'VerticalRightOutlined',
  
  // 媒体控制
  'PlayCircleOutlined',
  'PauseCircleOutlined',
  'FastForwardOutlined',
  'StepForwardOutlined',
  'StepBackwardOutlined',
  'BackwardOutlined',
  'ForwardOutlined',
  
  // 其他常用
  'PictureOutlined',
  'StarOutlined',
  'HeartOutlined',
  'LikeOutlined',
  'DislikeOutlined',
  'ThunderboltOutlined',
  'FireOutlined',
  'RocketOutlined',
  'TrophyOutlined',
  'GiftOutlined',
  'CrownOutlined',
  'GlobalOutlined',
  'EnvironmentOutlined',
  'CalendarOutlined',
  'ClockCircleOutlined',
  'ScheduleOutlined',
  'HistoryOutlined',
  'TagOutlined',
  'TagsOutlined',
  'FlagOutlined',
  'BookOutlined',
  'ReadOutlined',
  'PrinterOutlined',
  'ScanOutlined',
  'QrcodeOutlined',
  'BarcodeOutlined',
  'IdcardOutlined',
  'ContactsOutlined',
  'UsergroupAddOutlined',
  'UsergroupDeleteOutlined',
  'UserSwitchOutlined',
  'RobotOutlined',
  'SmileOutlined',
  'MehOutlined',
  'FrownOutlined',
  'ZoomInOutlined',
  'ZoomOutOutlined',
  'FullscreenOutlined',
  'FullscreenExitOutlined',
  'CompressOutlined',
  'ExpandOutlined',
  'EnterOutlined',
  'LogoutOutlined',
  'PoweroffOutlined',
  'DisconnectOutlined',
  'LinkOutlined',
  'WifiOutlined',
  'CloudServerOutlined',
  'PartitionOutlined',
  'NodeIndexOutlined',
  'SubnodeOutlined',
  'SwitcherOutlined',
  'ClusterOutlined',
  'DeploymentUnitOutlined',
  'GatewayOutlined',
  'ExperimentOutlined',
  'FundProjectionScreenOutlined',
  'FundViewOutlined',
  'GoldOutlined',
  'ReconciliationOutlined',
  'RedEnvelopeOutlined',
  'RestOutlined',
  'SecurityScanOutlined',
  'SelectOutlined',
  'SendOutlined',
  'ShareAltOutlined',
  'SkinOutlined',
  'SolutionOutlined',
  'SplitCellsOutlined',
  'MergeCellsOutlined',
  'TrademarkOutlined',
  'TransactionOutlined',
  'TranslationOutlined',
  'UsbOutlined',
  'WomanOutlined',
  'ManOutlined',
  'VerticalAlignTopOutlined',
  'VerticalAlignMiddleOutlined',
  'VerticalAlignBottomOutlined',
  'RiseOutlined',
  'FallOutlined',
  'StockOutlined',
  'BoxPlotOutlined',
  'FundOutlined',
  'SlackOutlined',
  'Html5Outlined',
  'GithubOutlined',
  'WechatOutlined',
  'WeiboOutlined',
  'QqOutlined',
  'AlipayOutlined',
  'TaobaoOutlined',
  'ZhihuOutlined',
  'DingtalkOutlined',
  'SkypeOutlined',
  'LinkedinOutlined',
  'FacebookOutlined',
  'TwitterOutlined',
  'InstagramOutlined',
  'YoutubeOutlined',
  'GoogleOutlined',
  'AmazonOutlined',
  'AppleOutlined',
  'WindowsOutlined',
  'AndroidOutlined',
  'IeOutlined',
  'ChromeOutlined',
  'FirefoxOutlined',
  'SafariOutlined',
  'OperaOutlined',
  'EdgeOutlined',
  'CodeSandboxOutlined',
  'CodepenOutlined',
  'ConsoleSqlOutlined',
  'FunctionOutlined',
  'PropertySafetyOutlined',
  'LayoutOutlined',
  'MacCommandOutlined',
];

export interface IconSelectProps {
  value?: string;
  onChange?: (value: string) => void;
  placeholder?: string;
  allowClear?: boolean;
  style?: React.CSSProperties;
}

export default function IconSelect({ value, onChange, placeholder, allowClear = true, style }: IconSelectProps) {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const [searchText, setSearchText] = useState('');
  const [inputValue, setInputValue] = useState(value || '');

  // 同步外部 value 到内部 inputValue
  useEffect(() => {
    setInputValue(value || '');
  }, [value]);

  // 获取图标组件
  const getIconComponent = (iconName: string) => {
    if (!iconName) return null;
    const IconComponent = (Icons as any)[iconName];
    return IconComponent ? <IconComponent /> : null;
  };

  // 过滤图标
  const filteredIcons = commonIcons.filter((iconName) =>
    iconName.toLowerCase().includes(searchText.toLowerCase())
  );

  // 图标选择内容
  const iconSelectContent = (
    <div style={{ width: 400, maxHeight: 400, overflowY: 'auto' }}>
      <Search
        placeholder={t('menu.searchIcon')}
        value={searchText}
        onChange={(e) => setSearchText(e.target.value)}
        style={{ marginBottom: 12 }}
        allowClear
      />
      <Row gutter={[8, 8]}>
        {filteredIcons.map((iconName) => {
          const IconComponent = (Icons as any)[iconName];
          const isSelected = value === iconName;
          return (
            <Col span={4} key={iconName}>
              <div
                onClick={() => {
                  onChange?.(iconName);
                  setInputValue(iconName);
                  setOpen(false);
                  setSearchText('');
                }}
                style={{
                  padding: '8px',
                  textAlign: 'center',
                  cursor: 'pointer',
                  border: isSelected ? '2px solid #1890ff' : '1px solid #d9d9d9',
                  borderRadius: '4px',
                  backgroundColor: isSelected ? '#e6f7ff' : '#fff',
                  transition: 'all 0.3s',
                }}
                onMouseEnter={(e) => {
                  if (!isSelected) {
                    e.currentTarget.style.borderColor = '#1890ff';
                    e.currentTarget.style.backgroundColor = '#f0f0f0';
                  }
                }}
                onMouseLeave={(e) => {
                  if (!isSelected) {
                    e.currentTarget.style.borderColor = '#d9d9d9';
                    e.currentTarget.style.backgroundColor = '#fff';
                  }
                }}
                title={iconName}
              >
                <div style={{ fontSize: '20px', marginBottom: '4px' }}>
                  {IconComponent ? <IconComponent /> : null}
                </div>
                <div style={{ fontSize: '10px', color: '#666', wordBreak: 'break-all' }}>
                  {iconName.replace('Outlined', '')}
                </div>
              </div>
            </Col>
          );
        })}
      </Row>
      {filteredIcons.length === 0 && (
        <div style={{ textAlign: 'center', padding: '20px', color: '#999' }}>
          {t('menu.noIconFound')}
        </div>
      )}
    </div>
  );

  return (
    <Input.Group compact style={{ display: 'flex' }}>
      <Input
        value={inputValue}
        onChange={(e) => {
          const newValue = e.target.value;
          setInputValue(newValue);
          onChange?.(newValue);
        }}
        placeholder={placeholder || t('menu.iconPlaceholder')}
        allowClear={allowClear}
        style={{ flex: 1, ...style }}
        suffix={inputValue ? getIconComponent(inputValue) : null}
      />
      <Popover
        content={iconSelectContent}
        trigger="click"
        open={open}
        onOpenChange={setOpen}
        placement="bottomRight"
        overlayStyle={{ maxWidth: 'none' }}
      >
        <Button
          icon={<AppstoreOutlined />}
          onClick={() => setOpen(true)}
          type="default"
        >
          {t('menu.selectIcon')}
        </Button>
      </Popover>
    </Input.Group>
  );
}

