/**
 * 字典类型表单组件
 */
import { useEffect, useState } from 'react';
import { Drawer, Form, Input, InputNumber, Switch, message, Button } from 'antd';
import { DictType, DictTypeCreate, DictTypeUpdate } from '@/types/dict';
import { createDictType, updateDictType } from '@/api/dict';
import { useTranslation } from 'react-i18next';
import { useDebounce } from '@/hooks/useDebounce';
import { formRules } from '@/utils/formRules';

const { TextArea } = Input;

interface DictTypeFormProps {
  visible: boolean;
  dictType: DictType | null;
  onCancel: () => void;
  onSuccess: () => void;
}

export default function DictTypeForm({ visible, dictType, onCancel, onSuccess }: DictTypeFormProps) {
  const { t } = useTranslation();
  const [form] = Form.useForm();
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (visible) {
      if (dictType) {
        form.setFieldsValue({
          ...dictType,
        });
      } else {
        form.resetFields();
        form.setFieldsValue({
          status: 1,
          sort: 0,
        });
      }
    }
  }, [visible, dictType, form]);

  // 提交处理函数
  const handleSubmit = async () => {
    if (submitting) return;

    try {
      const values = await form.validateFields();
      setSubmitting(true);

      if (dictType) {
        await updateDictType(dictType.id, values as DictTypeUpdate);
        message.success(t('common.updateSuccess'));
      } else {
        await createDictType(values as DictTypeCreate);
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

  return (
    <Drawer
      title={dictType ? t('dict.editType') : t('dict.createType')}
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
        <Form.Item
          name="name"
          label={t('dict.typeName')}
          rules={[formRules.required(t('dict.typeName'))]}
        >
          <Input placeholder={t('dict.typeNamePlaceholder')} />
        </Form.Item>

        <Form.Item
          name="code"
          label={t('dict.typeCode')}
          rules={[
            formRules.required(t('dict.typeCode')),
            {
              pattern: /^[a-zA-Z0-9_]+$/,
              message: t('dict.codePattern'),
            },
          ]}
        >
          <Input placeholder={t('dict.typeCodePlaceholder')} />
        </Form.Item>

        <Form.Item
          name="sort"
          label={t('common.sort')}
          initialValue={0}
        >
          <InputNumber min={0} style={{ width: '100%' }} />
        </Form.Item>

        <Form.Item
          name="status"
          label={t('common.status')}
          valuePropName="checked"
          getValueFromEvent={(checked) => (checked ? 1 : 0)}
          getValueProps={(value) => ({ checked: value === 1 })}
        >
          <Switch checkedChildren={t('common.normal')} unCheckedChildren={t('common.disabled')} />
        </Form.Item>

        <Form.Item
          name="remark"
          label={t('common.remark')}
          rules={formRules.remark}
        >
          <TextArea rows={4} placeholder={t('common.remarkPlaceholder')} />
        </Form.Item>
      </Form>
    </Drawer>
  );
}

