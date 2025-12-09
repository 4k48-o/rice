/**
 * 字典数据表单组件
 */
import { useEffect, useState, useMemo } from 'react';
import { Drawer, Form, Input, Select, InputNumber, Switch, message, Button, Row, Col } from 'antd';
import { DictData, DictDataCreate, DictDataUpdate } from '@/types/dict';
import { createDictData, updateDictData } from '@/api/dict';
import { getDictTypeList } from '@/api/dict';
import { DictType } from '@/types/dict';
import { useTranslation } from 'react-i18next';
import { useDebounce } from '@/hooks/useDebounce';
import { formRules } from '@/utils/formRules';
import { IconSelect } from '@/components/IconSelect';

const { TextArea } = Input;

interface DictDataFormProps {
  visible: boolean;
  dictData: DictData | null;
  onCancel: () => void;
  onSuccess: () => void;
}

export default function DictDataForm({ visible, dictData, onCancel, onSuccess }: DictDataFormProps) {
  const { t } = useTranslation();
  const [form] = Form.useForm();
  const [submitting, setSubmitting] = useState(false);
  const [dictTypes, setDictTypes] = useState<DictType[]>([]);
  const [loadingTypes, setLoadingTypes] = useState(false);

  // 加载字典类型列表
  const loadDictTypes = async () => {
    setLoadingTypes(true);
    try {
      const response = await getDictTypeList({ page: 1, page_size: 100, status: 1 });
      setDictTypes(response.data.items);
    } catch (error: any) {
      message.error(error.message || t('dict.loadDictTypeListFailed'));
    } finally {
      setLoadingTypes(false);
    }
  };

  useEffect(() => {
    if (visible) {
      loadDictTypes();
      if (dictData) {
        form.setFieldsValue({
          ...dictData,
        });
      } else {
        form.resetFields();
        form.setFieldsValue({
          status: 1,
          sort: 0,
        });
      }
    }
  }, [visible, dictData, form]);

  // 提交处理函数
  const handleSubmit = async () => {
    if (submitting) return;

    try {
      const values = await form.validateFields();
      setSubmitting(true);

      if (dictData) {
        await updateDictData(dictData.id, values as DictDataUpdate);
        message.success(t('common.updateSuccess'));
      } else {
        await createDictData(values as DictDataCreate);
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
      title={dictData ? t('dict.editData') : t('dict.createData')}
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
          name="dict_type_id"
          label={t('dict.selectType')}
          rules={[formRules.required(t('dict.selectType'))]}
        >
          <Select
            placeholder={t('dict.typePlaceholder')}
            loading={loadingTypes}
            disabled={!!dictData} // 编辑时不允许修改字典类型
          >
            {dictTypes.map((type) => (
              <Select.Option key={type.id} value={type.id}>
                {type.name} ({type.code})
              </Select.Option>
            ))}
          </Select>
        </Form.Item>

        <Row gutter={16}>
          <Col span={12}>
            <Form.Item
              name="label"
              label={t('dict.label')}
              rules={[formRules.required(t('dict.label'))]}
            >
              <Input placeholder={t('dict.labelPlaceholder')} />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item
              name="value"
              label={t('dict.value')}
              rules={[formRules.required(t('dict.value'))]}
            >
              <Input placeholder={t('dict.valuePlaceholder')} />
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={16}>
          <Col span={12}>
            <Form.Item
              name="sort"
              label={t('common.sort')}
              initialValue={0}
            >
              <InputNumber min={0} style={{ width: '100%' }} />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item
              name="status"
              label={t('common.status')}
              valuePropName="checked"
              getValueFromEvent={(checked) => (checked ? 1 : 0)}
              getValueProps={(value) => ({ checked: value === 1 })}
            >
              <Switch checkedChildren={t('common.normal')} unCheckedChildren={t('common.disabled')} />
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={16}>
          <Col span={12}>
            <Form.Item
              name="css_class"
              label={t('dict.cssClass')}
            >
              <Input placeholder={t('dict.cssClassPlaceholder')} />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item
              name="color"
              label={t('dict.color')}
            >
              <Input placeholder={t('dict.colorPlaceholder')} />
            </Form.Item>
          </Col>
        </Row>

        <Form.Item
          name="icon"
          label={t('dict.icon')}
        >
          <IconSelect placeholder={t('dict.iconPlaceholder')} />
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

