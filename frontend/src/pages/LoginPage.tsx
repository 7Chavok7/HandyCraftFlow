import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button, Card, Form, Input, Typography, Alert } from "antd";
import { login } from "../api/auth";
import { useAuth } from "../context/AuthContext";

const { Title } = Typography;

export default function LoginPage() {
  const navigate = useNavigate();
  const { refresh } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onFinish = async (values: { username: string; password: string }) => {
    setLoading(true);
    setError(null);
    try {
      await login(values.username, values.password);
      await refresh();
      navigate("/");
    } catch (e: any) {
      setError(
        e.response?.data?.detail ||
        e.response?.data?.non_field_errors?.[0] ||
        "Неверный логин или пароль"
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      display: "flex", justifyContent: "center", alignItems: "center",
      minHeight: "100vh", background: "#f0f2f5",
    }}>
      <Card style={{ width: 360 }}>
        <Title level={4} style={{ textAlign: "center", marginBottom: 24 }}>
          HCF — вход
        </Title>
        {error && (
          <Alert type="error" message={error} showIcon style={{ marginBottom: 16 }} />
        )}
        <Form layout="vertical" onFinish={onFinish}>
          <Form.Item
            label="Логин"
            name="username"
            rules={[{ required: true, message: "Введите логин" }]}
          >
            <Input autoComplete="username" />
          </Form.Item>
          <Form.Item
            label="Пароль"
            name="password"
            rules={[{ required: true, message: "Введите пароль" }]}
          >
            <Input.Password autoComplete="current-password" />
          </Form.Item>
          <Button type="primary" htmlType="submit" block loading={loading}>
            Войти
          </Button>
        </Form>
      </Card>
    </div>
  );
}