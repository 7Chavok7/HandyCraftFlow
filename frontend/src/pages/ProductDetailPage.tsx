import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import {
  Card, Col, Row, Spin, Empty, Descriptions, Table, Tag, Alert, Button,
} from "antd";
import { ArrowLeftOutlined } from "@ant-design/icons";
import { fetchVariantDetail } from "../api/catalog";
import type { VariantDetail } from "../api/catalog";

export default function ProductDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [detail, setDetail] = useState<VariantDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    fetchVariantDetail(Number(id))
      .then(setDetail)
      .catch(() => setError("Не удалось загрузить карточку"))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <Spin />;
  if (error) return <Alert type="error" message={error} showIcon />;
  if (!detail) return <Empty />;

  const { variant, recipe, stocks, economics } = detail;

  return (
    <>
      <Link to="/products">
        <Button icon={<ArrowLeftOutlined />} style={{ marginBottom: 16 }}>
          Назад к товарам
        </Button>
      </Link>

      <Row gutter={16}>
        <Col span={24}>
          <Card title={`Вариант: ${variant.name}`} size="small" style={{ marginBottom: 16 }}>
            <Descriptions column={3} size="small">
              <Descriptions.Item label="Артикул">{variant.vendor_code || "—"}</Descriptions.Item>
              <Descriptions.Item label="Баркод">{variant.barcode || "—"}</Descriptions.Item>
              <Descriptions.Item label="Надбавка">
                {variant.extra_cost} ₽
              </Descriptions.Item>
            </Descriptions>
          </Card>
        </Col>

        <Col span={12}>
          <Card title="Экономика (WB)" size="small" style={{ marginBottom: 16 }}>
            <Descriptions column={1} size="small">
              <Descriptions.Item label="Себестоимость">
                <strong>{economics.cost} ₽</strong>
              </Descriptions.Item>
              <Descriptions.Item label="Красная линия">
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
                  { title: "Склад", render: (_, s) => s.warehouse },
                  { title: "Кол-во", dataIndex: "qty" },
                  { title: "Резерв", dataIndex: "reserved_qty" },
                  { title: "Доступно", dataIndex: "available_qty" },
                ]}
              />
            )}
          </Card>
        </Col>

        <Col span={24}>
          <Card title="Рецепт" size="small">
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
      </Row>
    </>
  );
}