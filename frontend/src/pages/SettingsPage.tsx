import { useEffect, useState } from "react";
import {
  Card, Form, InputNumber, Select, Button, Spin, message, Row, Col,
  Alert, Divider, Typography, Radio,
} from "antd";
import { SaveOutlined } from "@ant-design/icons";
import {
  fetchSettings, updateSettings, type WorkspaceSettings,
} from "../api/settings";

const { Title, Text } = Typography;

export default function SettingsPage() {
  const [settings, setSettings] = useState<WorkspaceSettings | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [form] = Form.useForm();

  const laborMode = Form.useWatch("labor_mode", form);

  const load = () => {
    setLoading(true);
    fetchSettings()
      .then((s) => {
        setSettings(s);
        form.setFieldsValue({
          labor_mode: s.labor_mode,
          labor_rate: s.labor_rate ? Number(s.labor_rate) : null,
          income_goal: s.income_goal ? Number(s.income_goal) : null,
          work_hours_per_day: Number(s.work_hours_per_day),
          target_margin_percent: Number(s.target_margin_percent),
          electricity_rate: Number(s.electricity_rate),
          tax_rate: Number(s.tax_rate),
          equipment_hour_cost: Number(s.equipment_hour_cost),
        });
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  const onSave = async (values: any) => {
    if (!settings) return;
    setSaving(true);
    try {
      await updateSettings(settings.workspace, {
        labor_mode: values.labor_mode,
        labor_rate: values.labor_rate ? String(values.labor_rate) : null,
        income_goal: values.income_goal ? String(values.income_goal) : null,
        work_hours_per_day: String(values.work_hours_per_day),
        target_margin_percent: String(values.target_margin_percent),
        electricity_rate: String(values.electricity_rate),
        tax_rate: String(values.tax_rate),
        equipment_hour_cost: String(values.equipment_hour_cost),
      });
      message.success("Настройки сохранены");
      load();
    } catch (e: any) {
      message.error(e.response?.data?.detail || "Ошибка сохранения");
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <Spin />;

  return (
    <Row gutter={16}>
      <Col span={16}>
        <Card title="Настройки кабинета">
          <Alert
            type="info"
            showIcon
            message="Эти настройки влияют на расчёт себестоимости, маржи и минимальной цены."
            style={{ marginBottom: 16 }}
          />
          <Form form={form} layout="vertical" onFinish={onSave}>
            <Divider orientation="left">Труд</Divider>
            <Form.Item label="Режим расчёта труда" name="labor_mode">
              <Radio.Group>
                <Radio.Button value="ignore_labor">Не учитывать мой труд</Radio.Button>
                <Radio.Button value="manual_rate">Моё время стоит X ₽/час</Radio.Button>
                <Radio.Button value="income_goal">Хочу зарабатывать Y ₽/мес</Radio.Button>
              </Radio.Group>
            </Form.Item>

            {laborMode === "manual_rate" && (
              <Form.Item label="Ставка часа, ₽" name="labor_rate">
                <InputNumber min={0} style={{ width: "100%" }} />
              </Form.Item>
            )}

            {laborMode === "income_goal" && (
              <>
                <Form.Item label="Цель дохода в месяц, ₽" name="income_goal">
                  <InputNumber min={0} style={{ width: "100%" }} />
                </Form.Item>
                <Form.Item label="Часов работы в день" name="work_hours_per_day">
                  <InputNumber min={0} max={24} step={0.5} style={{ width: "100%" }} />
                </Form.Item>
              </>
            )}

            <Divider orientation="left">Экономика</Divider>
            <Form.Item label="Целевая маржа, %" name="target_margin_percent">
              <InputNumber min={0} max={100} style={{ width: "100%" }} />
            </Form.Item>
            <Form.Item label="Налог, %" name="tax_rate">
              <InputNumber min={0} max={100} style={{ width: "100%" }} />
            </Form.Item>
            <Form.Item label="Тариф электричества, ₽/кВт·ч" name="electricity_rate">
              <InputNumber min={0} step={0.01} style={{ width: "100%" }} />
            </Form.Item>
            <Form.Item label="Стоимость часа оборудования, ₽" name="equipment_hour_cost">
              <InputNumber min={0} step={0.01} style={{ width: "100%" }} />
            </Form.Item>

            <Form.Item>
              <Button type="primary" htmlType="submit" loading={saving} icon={<SaveOutlined />}>
                Сохранить
              </Button>
            </Form.Item>
          </Form>
        </Card>
      </Col>

      <Col span={8}>
        <Card title="Текущая эффективная ставка">
          <Title level={2}>{settings?.effective_labor_rate} ₽/час</Title>
          <Text type="secondary">
            Рассчитывается по выбранному режиму труда. Влияет на себестоимость и красную линию цены.
          </Text>
        </Card>
      </Col>
    </Row>
  );
}