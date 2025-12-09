/**
 * 用户表单组件
 */
import { useEffect, useState } from 'react';
import { Drawer, Form, Input, Select, message, Button, Row, Col } from 'antd';

const { TextArea } = Input;
import { User, UserCreate, UserUpdate } from '@/types/user';
import { createUser, updateUser } from '@/api/user';
import { useTranslation } from 'react-i18next';
import { Permission } from '@/components/Permission/Permission';
import { useDebounce } from '@/hooks/useDebounce';
// toIdString removed - IDs are now strings
import { normalizeFormData } from '@/utils/formData';
import { DepartmentSelect } from '@/components/DepartmentSelect';
import { formRules } from '@/utils/formRules';

interface UserFormProps {
  visible: boolean;
  user: User | null;
  onCancel: () => void;
  onSuccess: () => void;
}

export default function UserForm({ visible, user, onCancel, onSuccess }: UserFormProps) {
  const { t } = useTranslation();
  const [form] = Form.useForm();
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (visible) {
      if (user) {
        form.setFieldsValue(user);
      } else {
        form.resetFields();
      }
    }
  }, [visible, user, form]);

  // 提交处理函数
  const handleSubmit = async () => {
    if (submitting) return;
    
    try {
      const values = await form.validateFields();
      setSubmitting(true);
      
      // 统一处理表单数据中的ID字段：将string类型的ID转换为number
      // 这样确保后端能正确接收和处理（后端Schema期望int类型）
      const normalizedValues = normalizeFormData(values);
      
      if (user) {
        // 使用公共方法转换 ID，避免 JavaScript 精度丢失
        await updateUser(user.id, normalizedValues as UserUpdate);
        message.success(t('common.updateSuccess'));
      } else {
        await createUser(normalizedValues as UserCreate);
        message.success(t('common.createSuccess'));
      }
      setSubmitting(false);
      onSuccess();
    } catch (error: any) {
      setSubmitting(false);
      if (error.errorFields) {
        // 表单验证错误
        return;
      }
      message.error(error.message || t('common.operationFailed'));
    }
  };

  // 防抖的提交处理
  const debouncedSubmit = useDebounce(handleSubmit, 300);


  return (
    <Drawer
      title={user ? t('user.editUser') : t('user.createUser')}
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
        {!user && (
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="username"
                label={t('user.username')}
                rules={formRules.username}
              >
                <Input />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="password"
                label={t('auth.password')}
                rules={formRules.simplePassword}
              >
                <Input.Password />
              </Form.Item>
            </Col>
          </Row>
        )}

        <Row gutter={16}>
          <Col span={12}>
            <Form.Item name="real_name" label={t('user.realName')}>
              <Input />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item name="nickname" label={t('user.nickname')}>
              <Input />
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={16}>
          <Col span={12}>
            <Form.Item
              name="email"
              label={t('user.email')}
              rules={[formRules.email]}
            >
              <Input />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item 
              name="phone" 
              label={t('user.phone')}
              rules={[formRules.phone]}
            >
              <Input />
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={16}>
          <Col span={12}>
            <Form.Item name="dept_id" label={t('user.department')}>
              <DepartmentSelect
                placeholder={t('common.pleaseSelect', { field: t('user.department') })}
                onlyEnabled={true}
              />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item name="position" label={t('user.position')}>
              <Input />
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={16}>
          <Col span={12}>
            <Form.Item name="gender" label={t('user.gender')}>
              <Select>
                <Select.Option value={0}>{t('user.genderUnknown')}</Select.Option>
                <Select.Option value={1}>{t('user.male')}</Select.Option>
                <Select.Option value={2}>{t('user.female')}</Select.Option>
              </Select>
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item name="status" label={t('user.status')} initialValue={1}>
              <Select>
                <Select.Option value={0}>{t('common.disabled')}</Select.Option>
                <Select.Option value={1}>{t('common.normal')}</Select.Option>
              </Select>
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={16}>
          <Col span={24}>
            <Form.Item name="remark" label={t('user.remark')}>
              <TextArea rows={4} placeholder={t('user.remarkPlaceholder')} />
            </Form.Item>
          </Col>
        </Row>
      </Form>
    </Drawer>
  );
}
