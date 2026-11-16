import { useEffect, useState } from "react";
import { Table, Spin, Tag } from "antd";
import { fetchProducts } from "../api/dashboard";
import type { Product } from "../types";

export default function ProductsPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchProducts()
      .then(setProducts)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <Spin />;

  return (
    <Table
      dataSource={products}
      rowKey="id"
      columns={[
        { title: "ID", dataIndex: "id", width: 60 },
        { title: "Название", dataIndex: "name" },
        { title: "Вариантов", render: (_, r) => r.variants.length },
        {
          title: "Активен",
          dataIndex: "is_active",
          render: (v: boolean) => (v ? <Tag color="green">Да</Tag> : <Tag>Нет</Tag>),
        },
      ]}
    />
  );
}