/**
 * 角色表单组件
 */
import { useEffect, useState, useMemo } from 'react';
import { Drawer, Form, Input, Select, Tree, TreeSelect, message, Button, Row, Col, Space, Checkbox } from 'antd';
import { Role, RoleCreate, RoleUpdate, PermissionTreeNode } from '@/types/role';
import { createRole, updateRole, getRoleDetail, getPermissionTree } from '@/api/role';
import { getDepartmentTree } from '@/api/department';
import { Department } from '@/types/department';
import { useTranslation } from 'react-i18next';
import { useDebounce } from '@/hooks/useDebounce';
import { formRules } from '@/utils/formRules';
import type { DataNode } from 'antd/es/tree';

const { TextArea } = Input;

interface RoleFormProps {
  visible: boolean;
  role: Role | null;
  onCancel: () => void;
  onSuccess: () => void;
}

export default function RoleForm({ visible, role, onCancel, onSuccess }: RoleFormProps) {
  const { t } = useTranslation();
  const [form] = Form.useForm();
  const [submitting, setSubmitting] = useState(false);
  const [permissionTree, setPermissionTree] = useState<PermissionTreeNode[]>([]);
  const [checkedKeys, setCheckedKeys] = useState<React.Key[]>([]);
  const [loadingPermissions, setLoadingPermissions] = useState(false);
  const [departmentTree, setDepartmentTree] = useState<Department[]>([]);
  const [loadingDepartments, setLoadingDepartments] = useState(false);

  // 加载权限树和部门树
  useEffect(() => {
    if (visible) {
      loadPermissionTree();
      loadDepartmentTree();
    }
  }, [visible]);

  // 加载角色详情（编辑模式）
  useEffect(() => {
    if (visible && role) {
      loadRoleDetail();
    } else if (visible && !role) {
      form.resetFields();
      setCheckedKeys([]);
    }
  }, [visible, role, form]);

  const loadPermissionTree = async () => {
    setLoadingPermissions(true);
    try {
      const response = await getPermissionTree();
      const treeData = response.data || [];
      console.log('权限树数据:', treeData);
      setPermissionTree(treeData);
      if (treeData.length === 0) {
        console.warn('权限树数据为空');
      }
    } catch (error: any) {
      console.error('加载权限树失败:', error);
      message.error(error.message || t('role.loadPermissionTreeFailed'));
    } finally {
      setLoadingPermissions(false);
    }
  };

  const loadDepartmentTree = async () => {
    setLoadingDepartments(true);
    try {
      const response = await getDepartmentTree();
      setDepartmentTree(response.data || []);
    } catch (error: any) {
      message.error(error.message || t('role.loadDepartmentTreeFailed'));
    } finally {
      setLoadingDepartments(false);
    }
  };

  const loadRoleDetail = async () => {
    if (!role) return;
    
    try {
      const response = await getRoleDetail(role.id);
      const roleData = response.data;
      
      // 设置表单值
      form.setFieldsValue({
        name: roleData.name,
        code: roleData.code,
        sort: roleData.sort,
        status: roleData.status,
        data_scope: roleData.data_scope,
        department_ids: (roleData as any).department_ids || undefined,
      });

      // 设置选中的权限
      if (roleData.permissions && roleData.permissions.length > 0) {
        const permissionIds = roleData.permissions.map((p: PermissionTreeNode) => p.id);
        setCheckedKeys(permissionIds);
      } else {
        setCheckedKeys([]);
      }
    } catch (error: any) {
      message.error(error.message || t('role.loadRoleDetailFailed'));
    }
  };

  // 转换权限树为 Tree 组件需要的格式
  const treeData = useMemo(() => {
    if (!permissionTree || permissionTree.length === 0) {
      console.warn('权限树为空，无法渲染');
      return [];
    }
    
    const convertToTreeData = (nodes: PermissionTreeNode[]): DataNode[] => {
      if (!nodes || nodes.length === 0) {
        return [];
      }
      
      return nodes.map((node) => ({
        title: node.name || node.code || node.id,
        key: node.id,
        children: node.children && node.children.length > 0 
          ? convertToTreeData(node.children) 
          : undefined,
      }));
    };
    
    const result = convertToTreeData(permissionTree);
    console.log('转换后的树数据:', result);
    return result;
  }, [permissionTree]);

  // 处理权限树选择
  const handlePermissionCheck = (checked: React.Key[] | { checked: React.Key[]; halfChecked: React.Key[] }) => {
    if (Array.isArray(checked)) {
      setCheckedKeys(checked);
    } else {
      setCheckedKeys(checked.checked);
    }
  };

  // 全选/取消全选权限
  const handleSelectAllPermissions = (checked: boolean) => {
    const getAllKeys = (nodes: PermissionTreeNode[]): string[] => {
      let keys: string[] = [];
      nodes.forEach((node) => {
        keys.push(node.id);
        if (node.children && node.children.length > 0) {
          keys = keys.concat(getAllKeys(node.children));
        }
      });
      return keys;
    };
    
    if (checked) {
      const allKeys = getAllKeys(permissionTree);
      setCheckedKeys(allKeys);
    } else {
      setCheckedKeys([]);
    }
  };

  // 提交处理函数
  const handleSubmit = async () => {
    if (submitting) return;
    
    try {
      const values = await form.validateFields();
      setSubmitting(true);
      
      const roleData: RoleCreate | RoleUpdate = {
        ...values,
        permission_ids: checkedKeys as string[],
      };

      // 如果数据权限是自定义，需要包含部门ID
      if (values.data_scope === 5 && values.department_ids) {
        roleData.department_ids = values.department_ids;
      }

      if (role) {
        await updateRole(role.id, roleData as RoleUpdate);
        message.success(t('common.updateSuccess'));
      } else {
        await createRole(roleData as RoleCreate);
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

  // 数据权限选项
  const dataScopeOptions = [
    { value: 1, label: t('role.all') },
    { value: 2, label: t('role.deptAndSub') },
    { value: 3, label: t('role.deptOnly') },
    { value: 4, label: t('role.selfOnly') },
    { value: 5, label: t('role.custom') },
  ];

  // 监听数据权限变化，清空部门选择（当不是自定义时）
  const dataScope = Form.useWatch('data_scope', form);

  return (
    <Drawer
      title={role ? t('role.editRole') : t('role.createRole')}
      open={visible}
      onClose={onCancel}
      width={1200}
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
      <Row gutter={24}>
        {/* 左侧：表单 */}
        <Col span={10}>
          <Form form={form} layout="vertical">
            <Form.Item
              name="name"
              label={t('role.roleName')}
              rules={[
                formRules.required(t('role.roleName')),
                ...formRules.stringLength(2, 50, t('role.roleName')),
              ]}
            >
              <Input placeholder={t('role.roleNamePlaceholder')} />
            </Form.Item>

            <Form.Item
              name="code"
              label={t('role.roleCode')}
              rules={[
                formRules.required(t('role.roleCode')),
                {
                  pattern: /^[a-zA-Z0-9_]+$/,
                  message: t('role.roleCodeFormatError'),
                },
                ...formRules.stringLength(2, 50, t('role.roleCode')),
              ]}
            >
              <Input placeholder={t('role.roleCodePlaceholder')} />
            </Form.Item>

            <Form.Item
              name="sort"
              label={t('role.sort')}
              initialValue={0}
              rules={[formRules.nonNegativeInteger]}
            >
              <Input type="number" placeholder={t('role.sortPlaceholder')} />
            </Form.Item>

            <Form.Item
              name="status"
              label={t('common.status')}
              initialValue={1}
              rules={[formRules.required(t('common.status'))]}
            >
              <Select>
                <Select.Option value={0}>{t('common.disabled')}</Select.Option>
                <Select.Option value={1}>{t('common.normal')}</Select.Option>
              </Select>
            </Form.Item>

            <Form.Item
              name="data_scope"
              label={t('role.dataScope')}
              initialValue={1}
              rules={[formRules.required(t('role.dataScope'))]}
            >
              <Select>
                {dataScopeOptions.map((option) => (
                  <Select.Option key={option.value} value={option.value}>
                    {option.label}
                  </Select.Option>
                ))}
              </Select>
            </Form.Item>

            {/* 自定义部门选择（当数据权限为自定义时显示） */}
            {dataScope === 5 && (
              <Form.Item
                name="department_ids"
                label={t('role.customDepartments')}
                rules={[formRules.required(t('role.customDepartments'))]}
              >
                <TreeSelect
                  multiple
                  treeData={convertDepartmentToTreeData(departmentTree)}
                  placeholder={t('role.selectCustomDepartments')}
                  style={{ width: '100%' }}
                  treeCheckable
                  showCheckedStrategy="SHOW_ALL"
                  treeDefaultExpandAll
                  loading={loadingDepartments}
                />
              </Form.Item>
            )}
          </Form>
        </Col>

        {/* 右侧：权限树 */}
        <Col span={14}>
          <div style={{ borderLeft: '1px solid #f0f0f0', paddingLeft: 24, height: '100%' }}>
            <div style={{ marginBottom: 16 }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
                <span style={{ fontSize: 16, fontWeight: 500 }}>{t('role.permissions')}</span>
                <span style={{ color: '#999', fontSize: 14 }}>
                  {t('role.selectedCount', { count: checkedKeys.length })}
                </span>
              </div>
              <Checkbox
                checked={checkedKeys.length > 0 && checkedKeys.length === getAllPermissionCount(permissionTree)}
                indeterminate={
                  checkedKeys.length > 0 &&
                  checkedKeys.length < getAllPermissionCount(permissionTree)
                }
                onChange={(e) => handleSelectAllPermissions(e.target.checked)}
              >
                {t('role.selectAllPermissions')}
              </Checkbox>
            </div>
            <div
              style={{
                border: '1px solid #d9d9d9',
                borderRadius: 4,
                padding: 12,
                height: 'calc(100vh - 350px)',
                minHeight: 500,
                overflow: 'auto',
                backgroundColor: '#fafafa',
              }}
            >
              <Tree
                checkable
                checkedKeys={checkedKeys}
                onCheck={handlePermissionCheck}
                treeData={treeData}
                defaultExpandAll
                loading={loadingPermissions}
                style={{ backgroundColor: 'transparent' }}
              />
            </div>
          </div>
        </Col>
      </Row>
    </Drawer>
  );
}

// 获取所有权限数量
function getAllPermissionCount(nodes: PermissionTreeNode[]): number {
  let count = 0;
  nodes.forEach((node) => {
    count++;
    if (node.children && node.children.length > 0) {
      count += getAllPermissionCount(node.children);
    }
  });
  return count;
}

// 转换部门数据为 TreeSelect 格式
function convertDepartmentToTreeData(departments: Department[]): DataNode[] {
  return departments.map((dept) => ({
    title: dept.dept_name,
    value: dept.id,
    key: dept.id,
    children: dept.children ? convertDepartmentToTreeData(dept.children) : undefined,
  }));
}

