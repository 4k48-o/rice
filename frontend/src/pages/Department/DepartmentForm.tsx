/**
 * 部门表单组件
 */
import { useEffect, useState } from 'react';
import { Drawer, Form, Input, Select, TreeSelect, message, Button, Row, Col } from 'antd';
import { Department, DepartmentCreate, DepartmentUpdate } from '@/types/department';
import { createDepartment, updateDepartment, getDepartmentTree } from '@/api/department';
import { useTranslation } from 'react-i18next';
import { useDebounce } from '@/hooks/useDebounce';
// toIdString removed - IDs are now strings
import { normalizeFormData } from '@/utils/formData';
import { formRules } from '@/utils/formRules';

interface DepartmentFormProps {
  visible: boolean;
  department: Department | null;
  onCancel: () => void;
  onSuccess: () => void;
}

export default function DepartmentForm({ visible, department, onCancel, onSuccess }: DepartmentFormProps) {
  const { t } = useTranslation();
  const [form] = Form.useForm();
  const [departments, setDepartments] = useState<Department[]>([]);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (visible) {
      loadDepartments();
      if (department) {
        // 确保 department 有 id
        if (!department.id) {
          console.error('Department object missing id:', department);
          message.error(t('common.invalidData') || '部门数据无效');
          return;
        }
        // 将部门数据转换为表单需要的格式
        const formValues = {
          dept_code: department.code || department.dept_code || '',
          dept_name: department.name || department.dept_name || '',
          parent_id: department.parent_id,
          leader_id: department.leader_id,
          phone: department.phone || '',
          email: department.email || '',
          sort_order: department.sort || department.sort_order || 0,
          status: department.status !== undefined ? department.status : 1,
          remark: department.remark || '',
        };
        form.setFieldsValue(formValues);
      } else {
        form.resetFields();
      }
    }
  }, [visible, department, form, t]);

  const loadDepartments = async () => {
    try {
      const response = await getDepartmentTree();
      setDepartments(response.data);
    } catch (error) {
      console.error('Failed to load departments:', error);
    }
  };

  // 提交处理函数
  const handleSubmit = async () => {
    if (submitting) return;
    
    try {
      const values = await form.validateFields();
      setSubmitting(true);
      
      // 映射前端字段名到后端字段名
      const mappedValues: any = {
        code: values.dept_code,
        name: values.dept_name,
        parent_id: values.parent_id,
        leader_id: values.leader_id,
        phone: values.phone,
        email: values.email,
        sort: values.sort_order,
        status: values.status,
        remark: values.remark,
      };
      
      // 统一处理表单数据中的ID字段：将string类型的ID转换为number
      const normalizedValues = normalizeFormData(mappedValues);
      
      if (department) {
        // 使用公共方法转换 ID，避免 JavaScript 精度丢失
        await updateDepartment(department.id, normalizedValues as DepartmentUpdate);
        message.success(t('common.updateSuccess'));
      } else {
        await createDepartment(mappedValues as DepartmentCreate);
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

  // 转换部门树为TreeSelect格式
  const convertToTreeData = (depts: Department[]): any[] => {
    return depts.map((dept) => {
      const deptName = dept.name || dept.dept_name || `部门-${dept.id}`;
      return {
        title: deptName,
        value: dept.id,
        key: dept.id,
        children: dept.children ? convertToTreeData(dept.children) : undefined,
      };
    });
  };

  return (
    <Drawer
      title={department ? t('department.editDepartment') : t('department.createDepartment')}
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
              name="dept_code"
              label={t('department.departmentCode')}
              rules={[formRules.required(t('department.departmentCode'))]}
            >
              <Input />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item
              name="dept_name"
              label={t('department.departmentName')}
              rules={[formRules.required(t('department.departmentName'))]}
            >
              <Input />
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={16}>
          <Col span={12}>
            <Form.Item name="parent_id" label={t('department.parentDepartment')}>
              <TreeSelect
                placeholder={t('common.pleaseSelect', { field: t('department.parentDepartment') })}
                treeData={convertToTreeData(departments)}
                allowClear
                showSearch
                treeDefaultExpandAll
                filterTreeNode={(inputValue, node) =>
                  (node.title as string)?.toLowerCase().includes(inputValue.toLowerCase()) ?? false
                }
              />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item name="leader_id" label={t('department.leader')}>
              <Input placeholder={t('department.leaderPlaceholder')} />
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={16}>
          <Col span={12}>
            <Form.Item 
              name="phone" 
              label={t('department.phone')}
              rules={[formRules.phone]}
            >
              <Input />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item
              name="email"
              label={t('department.email')}
              rules={[formRules.email]}
            >
              <Input />
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={16}>
          <Col span={12}>
            <Form.Item name="sort_order" label={t('department.sortOrder')} initialValue={0}>
              <Input type="number" />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item name="status" label={t('department.status')} initialValue={1}>
              <Select>
                <Select.Option value={0}>{t('common.disabled')}</Select.Option>
                <Select.Option value={1}>{t('common.normal')}</Select.Option>
              </Select>
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={16}>
          <Col span={24}>
            <Form.Item name="remark" label={t('common.remark')}>
              <Input.TextArea rows={4} placeholder={t('common.remarkPlaceholder')} />
            </Form.Item>
          </Col>
        </Row>
      </Form>
    </Drawer>
  );
}

