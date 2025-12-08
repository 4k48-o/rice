/**
 * 用户表单组件
 */
import { useEffect, useState, useRef } from 'react';
import { Drawer, Form, Input, Select, message, Button, Row, Col } from 'antd';

const { TextArea } = Input;
import { User, UserCreate, UserUpdate } from '@/types/user';
import { createUser, updateUser } from '@/api/user';
import { getDepartmentTree } from '@/api/department';
import { Department } from '@/types/department';
import { useTranslation } from 'react-i18next';
import { Permission } from '@/components/Permission/Permission';
import { debounce } from '@/utils/debounce';

interface UserFormProps {
  visible: boolean;
  user: User | null;
  onCancel: () => void;
  onSuccess: () => void;
}

export default function UserForm({ visible, user, onCancel, onSuccess }: UserFormProps) {
  const { t } = useTranslation();
  const [form] = Form.useForm();
  const [departments, setDepartments] = useState<Department[]>([]);
  const [submitting, setSubmitting] = useState(false);
  const handleSubmitRef = useRef<() => Promise<void>>();

  useEffect(() => {
    if (visible) {
      loadDepartments();
      if (user) {
        form.setFieldsValue(user);
      } else {
        form.resetFields();
      }
    }
  }, [visible, user, form]);

  const loadDepartments = async () => {
    try {
      const response = await getDepartmentTree();
      setDepartments(response.data);
    } catch (error) {
      console.error('Failed to load departments:', error);
    }
  };

  // 更新提交函数引用
  useEffect(() => {
    handleSubmitRef.current = async () => {
      if (submitting) return;
      
      try {
        const values = await form.validateFields();
        setSubmitting(true);
        
        if (user) {
          await updateUser(user.id, values as UserUpdate);
          message.success(t('common.updateSuccess'));
        } else {
          await createUser(values as UserCreate);
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
  }, [user, submitting, form, onSuccess]);

  // 防抖的提交处理
  const handleSubmitDebounced = useRef(
    debounce(() => {
      if (handleSubmitRef.current) {
        handleSubmitRef.current();
      }
    }, 300)
  ).current;

  // 递归构建部门选项
  const buildDepartmentOptions = (depts: Department[]): any[] => {
    const options: any[] = [];
    depts.forEach((dept) => {
      const deptName = dept.name || dept.dept_name || `部门-${dept.id}`;
      const option: any = {
        value: dept.id,
        label: deptName,
      };
      if (dept.children && dept.children.length > 0) {
        option.children = buildDepartmentOptions(dept.children);
      }
      options.push(option);
    });
    return options;
  };

  const departmentOptions = buildDepartmentOptions(departments);

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
          <Button type="primary" onClick={handleSubmitDebounced} loading={submitting}>
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
                rules={[{ required: true, message: t('common.pleaseInput', { field: t('user.username') }) }]}
              >
                <Input />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="password"
                label={t('auth.password')}
                rules={[
                  { required: true, message: t('common.pleaseInput', { field: t('auth.password') }) },
                  { min: 8, message: t('common.passwordMinLength') },
                ]}
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
              rules={[{ type: 'email', message: t('common.invalidEmail') }]}
            >
              <Input />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item name="phone" label={t('user.phone')}>
              <Input />
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={16}>
          <Col span={12}>
            <Form.Item name="dept_id" label={t('user.department')}>
              <Select
                placeholder={t('common.pleaseSelect', { field: t('user.department') })}
                options={departmentOptions}
                showSearch
                filterOption={(input, option) =>
                  (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
                }
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
