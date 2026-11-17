import { useEffect, useState } from "react";
import {
  Table, Spin, Tag, Button, Modal, Form, Input, Upload, Space,
  message, Popconfirm, Image,
} from "antd";
import { PlusOutlined, EditOutlined, DeleteOutlined, UploadOutlined } from "@ant-design/icons";
import { useNavigate } from "react-router-dom";
import { fetchProducts } from "../api/dashboard";
import { fetchCurrentWorkspace } from "../api/dashboard";
import { createProduct, updateProduct, deleteProduct } from "../api/catalog";
import type { Product } from "../types";

export default function ProductsPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState<Product | null>(null);
  const [form] = Form.useForm();
  const navigate = useNavigate();

  const load = () => {
    setLoading(true);
    fetchProducts()
      .then(setProducts)
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  const openCreate = () => {
    setEditing(null);
    form.resetFields();
    setOpen(true);
  };

  const openEdit = (p: Product) => {
    setEditing(p);
    form.setFieldsValue({
      name: p.name,
      description: p.description,
      is_active: p.is_active,
    });
    setOpen(true);
  };

  const [workspaceId, setWorkspaceId] = useState("");

  useEffect(() => {
    fetchCurrentWorkspace().then((ws) => setWorkspaceId(ws.id));
  }, []);
  

  const onSubmit = async (values: any) => {
    const fd = new FormData();
    fd.append("name", values.name);
    fd.append("description", values.description || "");
    fd.append("is_active", values.is_active ? "true" : "false");
    fd.append("workspace_id", workspaceId);
    if (values.image?.[0]?.originFileObj)
     {
      fd.append("image", values.image[0].originFileObj);
    }

    try {
      if (editing) {
        await updateProduct(editing.id, fd);
        message.success("Товар обновлён");
      } else {
        await createProduct(fd);
        message.success("Товар создан");
      }
      setOpen(false);
      load();
    } catch (e: any) {
      message.error(e.response?.data?.name?.[0] || "Ошибка");
    }
  };

  const onDelete = async (id: number) => {
    try {
      await deleteProduct(id);
      message.success("Удалён");
      load();
    } catch {
      message.error("Ошибка удаления");
    }
  };

  if (loading) return <Spin />;

  return (
    <>
      <Button
        type="primary"
        icon={<PlusOutlined />}
        onClick={openCreate}
        style={{ marginBottom: 16 }}
      >
        Создать товар
      </Button>

      <Table
        dataSource={products}
        rowKey="id"
        columns={[
          {
            title: "Фото",
            width: 80,
            render: (_, p: Product) =>
              p.image ? <Image src={p.image} width={50} /> : "—",
          },
          { title: "ID", dataIndex: "id", width: 60 },
          {
            title: "Название",
            dataIndex: "name",
            render: (name, p) => (
              p.variants.length > 0 ? (
                <a onClick={() => navigate(`/products/${p.variants[0].id}`)}>
                  {name}
                </a>
              ) : (
                <span>{name} <Tag color="orange">нет вариантов</Tag></span>
              )
            ),
          },
          { title: "Вариантов", render: (_, r) => r.variants.length },
          {
            title: "Активен",
            dataIndex: "is_active",
            render: (v: boolean) => (v ? <Tag color="green">Да</Tag> : <Tag>Нет</Tag>),
          },
          {
            title: "Действия",
            render: (_, p: Product) => (
              <Space>
                <Button size="small" icon={<EditOutlined />} onClick={() => openEdit(p)}>
                  Ред.
                </Button>
                <Popconfirm title="Удалить?" onConfirm={() => onDelete(p.id)}>
                  <Button size="small" danger icon={<DeleteOutlined />}>
                    Удал.
                  </Button>
                </Popconfirm>
              </Space>
            ),
          },
        ]}
      />

      <Modal
        title={editing ? `Редактировать: ${editing.name}` : "Создать товар"}
        open={open}
        onCancel={() => setOpen(false)}
        onOk={() => form.submit()}
        okText="Сохранить"
      >
        <Form form={form} layout="vertical" onFinish={onSubmit}>
          <Form.Item label="Название" name="name" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item label="Описание" name="description">
            <Input.TextArea rows={3} />
          </Form.Item>
          <Form.Item label="Активен" name="is_active" valuePropName="checked" initialValue={true}>
            <Input type="checkbox" /> {/* можно Switch */}
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