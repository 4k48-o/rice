/**
 * 菜单表单组件
 */
import { useEffect, useState, useMemo } from 'react';
import { Drawer, Form, Input, Select, TreeSelect, message, Button, Row, Col, InputNumber, Switch } from 'antd';
import { Menu, MenuCreate, MenuUpdate } from '@/types/menu';
import { createMenu, updateMenu } from '@/api/menu';
import { useTranslation } from 'react-i18next';
import { useDebounce } from '@/hooks/useDebounce';
import { formRules } from '@/utils/formRules';
import { IconSelect } from '@/components/IconSelect';

const { TextArea } = Input;

interface MenuFormProps {
  visible: boolean;
  menu: Menu | null;
  menuTree: Menu[];
  onCancel: () => void;
  onSuccess: () => void;
}

export default function MenuForm({ visible, menu, menuTree, onCancel, onSuccess }: MenuFormProps) {
  const { t } = useTranslation();
  const [form] = Form.useForm();
  const [submitting, setSubmitting] = useState(false);

  // 将菜单树转换为 TreeSelect 需要的格式
  const treeSelectData = useMemo(() => {
    const convertToTreeSelect = (menus: Menu[], excludeId?: string): any[] => {
      return menus
        .filter((m) => m.id !== excludeId) // 排除当前编辑的菜单，避免循环引用
        .map((m) => ({
          title: `${m.title} (${m.name})`,
          value: m.id,
          key: m.id,
          children: m.children ? convertToTreeSelect(m.children, excludeId) : undefined,
        }));
    };
    return convertToTreeSelect(menuTree, menu?.id);
  }, [menuTree, menu?.id]);

  useEffect(() => {
    if (visible) {
      if (menu) {
        form.setFieldsValue({
          ...menu,
          parent_id: menu.parent_id || undefined,
        });
      } else {
        form.resetFields();
        form.setFieldsValue({
          type: 2,
          status: 1,
          visible: 1,
          is_cache: 0,
          is_external: 0,
          sort: 0,
        });
      }
    }
  }, [visible, menu, form]);

  // 提交处理函数
  const handleSubmit = async () => {
    if (submitting) return;

    try {
      const values = await form.validateFields();
      setSubmitting(true);

      // 处理 parent_id：空字符串或 undefined 转为 null
      const formData = {
        ...values,
        parent_id: values.parent_id || null,
      };

      if (menu) {
        await updateMenu(menu.id, formData as MenuUpdate);
        message.success(t('common.updateSuccess'));
      } else {
        await createMenu(formData as MenuCreate);
        message.success(t('common.createSuccess'));
      }
      setSubmitting(false);
      onSuccess();
    } catch (error: any) {
      setSubmitting(false);
      if (error.errorFields) {
        // 表单验证错误（前端校验失败）
        return;
      }
      // API 错误已经在 request 拦截器中统一处理并显示消息了
    }
  };

  // 防抖的提交处理
  const debouncedSubmit = useDebounce(handleSubmit, 300);

  // 根据菜单类型显示/隐藏字段
  const menuType = Form.useWatch('type', form);

  return (
    <Drawer
      title={menu ? t('menu.editMenu') : t('menu.createMenu')}
      open={visible}
      onClose={onCancel}
      width={720}
      destroyOnClose
      footer={
        <div style={{ textAlign: 'right', padding: '10px 0' }}>
          <Button onClick={onCancel} disabled={submitting} style={{ marginRight: 8 }}>
            {t('common.cancel')}
          </Button>
          <Button type="primary" onClick={debouncedSubmit} loading={submitting}>
            {t('common.save')}
          </Button>
        </div>
      }
    >
      <Form form={form} layout="vertical">
        <Row gutter={16}>
          <Col span={12}>
            <Form.Item
              name="name"
              label={t('menu.menuName')}
              rules={[
                formRules.required(t('menu.menuName')),
                ...formRules.username.filter((r) => r.required !== true), // 复用用户名规则但不要求必填（已用 required）
              ]}
            >
              <Input placeholder={t('menu.menuNamePlaceholder')} />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item
              name="title"
              label={t('menu.menuTitle')}
              rules={[formRules.required(t('menu.menuTitle'))]}
            >
              <Input placeholder={t('menu.menuTitlePlaceholder')} />
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={16}>
          <Col span={12}>
            <Form.Item name="parent_id" label={t('menu.parentMenu')}>
              <TreeSelect
                placeholder={t('menu.selectParentMenu')}
                allowClear
                treeData={treeSelectData}
                treeDefaultExpandAll
                showSearch
                treeNodeFilterProp="title"
              />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item
              name="type"
              label={t('menu.menuType')}
              rules={[formRules.required(t('menu.menuType'))]}
            >
              <Select>
                <Select.Option value={1}>{t('menu.directory')}</Select.Option>
                <Select.Option value={2}>{t('menu.menu')}</Select.Option>
                <Select.Option value={3}>{t('menu.button')}</Select.Option>
              </Select>
            </Form.Item>
          </Col>
        </Row>

        {menuType !== 3 && (
          <>
            <Row gutter={16}>
              <Col span={12}>
                <Form.Item name="path" label={t('menu.path')}>
                  <Input placeholder={t('menu.pathPlaceholder')} />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item name="component" label={t('menu.component')}>
                  <Input placeholder={t('menu.componentPlaceholder')} />
                </Form.Item>
              </Col>
            </Row>

            <Row gutter={16}>
              <Col span={12}>
                <Form.Item name="redirect" label={t('menu.redirect')}>
                  <Input placeholder={t('menu.redirectPlaceholder')} />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item name="icon" label={t('menu.icon')}>
                  <IconSelect placeholder={t('menu.iconPlaceholder')} />
                </Form.Item>
              </Col>
            </Row>
          </>
        )}

        <Row gutter={16}>
          <Col span={12}>
            <Form.Item name="permission_code" label={t('menu.permissionCode')}>
              <Input placeholder={t('menu.permissionCodePlaceholder')} />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item name="sort" label={t('menu.sort')} initialValue={0}>
              <InputNumber min={0} style={{ width: '100%' }} />
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={16}>
          <Col span={12}>
            <Form.Item name="status" label={t('common.status')} valuePropName="checked" getValueFromEvent={(checked) => (checked ? 1 : 0)} getValueProps={(value) => ({ checked: value === 1 })}>
              <Switch checkedChildren={t('common.normal')} unCheckedChildren={t('common.disabled')} />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item name="visible" label={t('menu.visible')} valuePropName="checked" getValueFromEvent={(checked) => (checked ? 1 : 0)} getValueProps={(value) => ({ checked: value === 1 })}>
              <Switch checkedChildren={t('menu.show')} unCheckedChildren={t('menu.hide')} />
            </Form.Item>
          </Col>
        </Row>

        {menuType === 2 && (
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="is_cache" label={t('menu.isCache')} valuePropName="checked" getValueFromEvent={(checked) => (checked ? 1 : 0)} getValueProps={(value) => ({ checked: value === 1 })}>
                <Switch checkedChildren={t('menu.show')} unCheckedChildren={t('menu.hide')} />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="is_external" label={t('menu.isExternal')} valuePropName="checked" getValueFromEvent={(checked) => (checked ? 1 : 0)} getValueProps={(value) => ({ checked: value === 1 })}>
                <Switch checkedChildren={t('menu.show')} unCheckedChildren={t('menu.hide')} />
              </Form.Item>
            </Col>
          </Row>
        )}
      </Form>
    </Drawer>
  );
}

