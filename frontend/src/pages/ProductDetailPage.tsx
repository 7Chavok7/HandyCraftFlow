import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import {
  Card, Col, Row, Spin, Empty, Descriptions, Table, Tag, Alert, Button,
  Modal, Form, Input, InputNumber, Upload, Space, message, Popconfirm, Switch,
} from "antd";
import {
  ArrowLeftOutlined, PlusOutlined, EditOutlined, DeleteOutlined, UploadOutlined,
} from "@ant-design/icons";
import { fetchVariantDetail, createVariant, updateVariant, deleteVariant } from "../api/catalog";
import type { VariantDetail } from "../api/catalog";

export default function ProductDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [detail, setDetail] = useState<VariantDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // CRUD
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState<any | null>(null);
  const [form] = Form.useForm();

  const load = () => {
    if (!id) return;
    setLoading(true);
    fetchVariantDetail(Number(id))
      .then(setDetail)
      .catch(() => setError("Не удалось загрузить карточку"))
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, [id]);

  const openCreate = () => {
    setEditing(null);
    form.resetFields();
    setOpen(true);
  };

  const openEdit = (v: any) => {
    setEditing(v);
    form.setFieldsValue({
      name: v.name,
      vendor_code: v.vendor_code,
      barcode: v.barcode,
      extra_cost: v.extra_cost,
      is_active: v.is_active,
    });
    setOpen(true);
  };

  const onSubmit = async (values: any) => {
    if (!detail) return;
    if (!detail.variant.product) {
      message.error("Не удалось определить product_id");
      return;
    }
    const fd = new FormData();
    fd.append("product", String(detail.variant.product));
    // Фактически product_id берём из detail.variant
    fd.delete("product");
    fd.append("product", String((detail as any).variant.product ?? ""));
    fd.append("name", values.name);
    fd.append("vendor_code", values.vendor_code || "");
    fd.append("barcode", values.barcode || "");
    fd.append("extra_cost", String(values.extra_cost ?? 0));
    fd.append("is_active", values.is_active ? "true" : "false");
    if (values.image?.[0]?.originFileObj) {
      fd.append("image", values.image[0].originFileObj);
    }

    try {
      if (editing) {
        await updateVariant(editing.id, fd);
        message.success("Вариант обновлён");
      } else {
        await createVariant(fd);
        message.success("Вариант создан");
      }
      setOpen(false);
      load();
    } catch (e: any) {
      message.error(e.response?.data?.name?.[0] || "Ошибка");
    }
  };

  const onDelete = async (vid: number) => {
    try {
      await deleteVariant(vid);
      message.success("Удалён");
      load();
    } catch {
      message.error("Ошибка удаления");
    }
  };

  if (loading) return <Spin />;
  if (error) return <Alert type="error" message={error} showIcon />;
  if (!detail) return <Empty />;

  const { all_variants, recipe, stocks, economics } = detail;

  return (
    <>
      <Link to="/products">
        <Button icon={<ArrowLeftOutlined />} style={{ marginBottom: 16 }}>
          Назад к товарам
        </Button>
      </Link>

      <Row gutter={16}>
        <Col span={24}>
          <Card
            title={`Варианты товара`}
            size="small"
            style={{ marginBottom: 5 }}
            extra={
              <Button
                type="primary"
                size="small"
                icon={<PlusOutlined />}
                onClick={openCreate}
              >
                Добавить вариант
              </Button>
            }
          >
            <Table
              dataSource={detail.all_variants}
              rowKey="id"
              pagination={false}
              size="small"
              columns={[
                { title: "ID", dataIndex: "id", width: 60 },
                { title: "Название", dataIndex: "name" },
                { title: "Артикул", dataIndex: "vendor_code" },
                { title: "Баркод", dataIndex: "barcode" },
                { title: "Надбавка", dataIndex: "extra_cost" },
                {
                  title: "Активен",
                  dataIndex: "is_active",
                  render: (v: boolean) => (v ? <Tag color="green">Да</Tag> : <Tag>Нет</Tag>),
                },
                {
                  title: "Действия",
                  render: (_, v: any) => (
                    <Space>
                      <Button size="small" icon={<EditOutlined />} onClick={() => openEdit(v)}>
                        Ред.
                      </Button>
                      <Popconfirm title="Удалить?" onConfirm={() => onDelete(v.id)}>
                        <Button size="small" danger icon={<DeleteOutlined />}>
                          Удал.
                        </Button>
                      </Popconfirm>
                    </Space>
                  ),
                },
              ]}
            />
          </Card>
        </Col>

        <Col span={24}>
          <Card title="Рецепт" 
          size="small"
          style={{ marginBottom: 5 }}>
            {!recipe ? (
              <Empty description="Рецепт не задан" />
            ) : (
              <>
                <Descriptions column={3} size="small" style={{ marginBottom: 16 }}>
                  <Descriptions.Item label="Труд">
                    {recipe.labor_minutes} мин
                  </Descriptions.Item>
                  <Descriptions.Item label="Источник норм">
                    {recipe.norms_source}
                  </Descriptions.Item>
                  <Descriptions.Item label="Кэш себестоимости">
                    {recipe.avg_cost_cached ?? "—"}
                  </Descriptions.Item>
                </Descriptions>
                <Table
                  dataSource={recipe.lines}
                  rowKey="id"
                  pagination={false}
                  size="small"
                  columns={[
                    { title: "Материал", dataIndex: "material_type_name" },
                    { title: "Кол-во на ед.", dataIndex: "qty_per_unit" },
                    { title: "Брак, %", dataIndex: "waste_percent" },
                  ]}
                />
              </>
            )}
          </Card>
        </Col>

        <Col span={12}>
          <Card title="Экономика (WB)" size="small" style={{ marginBottom: 16 }}>
            <Descriptions column={1} size="small">
              <Descriptions.Item label="Себестоимость">
                <strong>{economics.cost} ₽</strong>
              </Descriptions.Item>
              <Descriptions.Item label="Минимальная цена">
                <Tag color="red">{economics.min_price} ₽</Tag>
              </Descriptions.Item>
              <Descriptions.Item label="Доход с часа принтера">
                {economics.profit_per_production_hour} ₽/ч
              </Descriptions.Item>
            </Descriptions>
          </Card>
        </Col>

        <Col span={12}>
          <Card title="Остатки" size="small" style={{ marginBottom: 16 }}>
            {stocks.length === 0 ? (
              <Empty description="Нет остатков" />
            ) : (
              <Table
                dataSource={stocks}
                rowKey="id"
                pagination={false}
                size="small"
                columns={[
                  { title: "Склад", render: (_, s) => s.warehouse_name ?? s.warehouse },
                  { title: "Кол-во", dataIndex: "qty" },
                  { title: "Резерв", dataIndex: "reserved_qty" },
                  { title: "Доступно", dataIndex: "available_qty" },
                ]}
              />
            )}
          </Card>
        </Col>

      </Row>

      <Modal
        title={editing ? `Редактировать вариант: ${editing.name}` : "Новый вариант"}
        open={open}
        onCancel={() => setOpen(false)}
        onOk={() => form.submit()}
        okText="Сохранить"
      >
        <Form form={form} layout="vertical" onFinish={onSubmit}>
          <Form.Item label="Название варианта" name="name" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item label="Артикул продавца" name="vendor_code">
            <Input />
          </Form.Item>
          <Form.Item label="Баркод" name="barcode">
            <Input />
          </Form.Item>
          <Form.Item label="Надбавка к себестоимости, ₽" name="extra_cost" initialValue={0}>
            <InputNumber min={0} step={0.01} style={{ width: "100%" }} />
          </Form.Item>
          <Form.Item label="Активен" name="is_active" valuePropName="checked" initialValue={true}>
            <Switch />
          </Form.Item>
          <Form.Item label="Фото" name="image" valuePropName="fileList" getValueFromEvent={(e) => e?.fileList}>
            <Upload beforeUpload={() => false} listType="picture" maxCount={1}>
              <Button icon={<UploadOutlined />}>Загрузить</Button>
            </Upload>
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
}