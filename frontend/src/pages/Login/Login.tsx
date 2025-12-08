/**
 * 登录页面
 */
import { useState, useEffect } from 'react';
import { Form, Input, Button, Checkbox, message } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { useAuth } from '@/hooks/useAuth';
import { LoginRequest } from '@/types/auth';
import { useTranslation } from 'react-i18next';
import { storage } from '@/utils/storage';
import './Login.css';

export default function Login() {
  const { login } = useAuth();
  const { t } = useTranslation();
  const [loading, setLoading] = useState(false);
  const [form] = Form.useForm();

  // 页面加载时，如果有记住的用户名，自动填充
  useEffect(() => {
    const rememberedUsername = storage.getRememberUsername();
    if (rememberedUsername) {
      form.setFieldsValue({ username: rememberedUsername, remember: true });
    }
  }, [form]);

  const handleSubmit = async (values: LoginRequest & { remember?: boolean }) => {
    setLoading(true);
    try {
      // 处理记住我功能
      if (values.remember) {
        // 记住用户名
        storage.setRememberUsername(values.username);
      } else {
        // 清除记住的用户名
        storage.removeRememberUsername();
      }

      // 提交登录（不包含remember字段）
      const { remember, ...loginData } = values;
      await login(loginData);
    } catch (error) {
      // 错误已在login函数中处理
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <div className="login-header">
          <h1>{t('auth.login')}</h1>
        </div>
        <Form
          form={form}
          name="login"
          onFinish={handleSubmit}
          autoComplete="off"
          size="large"
        >
          <Form.Item
            name="username"
            rules={[{ required: true, message: t('common.pleaseInput', { field: t('auth.username') }) }]}
          >
            <Input
              prefix={<UserOutlined />}
              placeholder={t('auth.username')}
            />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[{ required: true, message: t('common.pleaseInput', { field: t('auth.password') }) }]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder={t('auth.password')}
            />
          </Form.Item>

          <Form.Item>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <Form.Item name="remember" valuePropName="checked" noStyle>
                <Checkbox>{t('auth.rememberMe')}</Checkbox>
              </Form.Item>
            </div>
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" block loading={loading}>
              {t('auth.login')}
            </Button>
          </Form.Item>
        </Form>
      </div>
    </div>
  );
}

