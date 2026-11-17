import { useEffect, useState } from "react";
import {
  Table, Spin, Tag, Button, Space, message, Popconfirm, Alert,
} from "antd";
import {
  CheckOutlined, CloseOutlined, CalculatorOutlined,
} from "@ant-design/icons";
import {
  fetchPromotionItems, decidePromotionItem, forecastPromotionItem,
  type PromotionItem, type Forecast,
} from "../api/promo";

const DECISION_COLOR: Record<string, string> = {
  pending: "default",
  accepted: "green",
  declined: "red",
};

export default function PromotionsPage() {
  const [items, setItems] = useState<PromotionItem[]>([]);
  const [forecasts, setForecasts] = useState<Record<number, Forecast>>({});
  const [loading, setLoading] = useState(true);

  const load = () => {
    setLoading(true);
    fetchPromotionItems()
      .then(setItems)
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  const onDecide = async (id: number, decision: "accepted" | "declined") => {
    try {
      await decidePromotionItem(id, decision);
      message.success(decision === "accepted" ? "Участвуем" : "Отказались");
      load();
    } catch (e: any) {
      message.error(e.response?.data?.error || "Ошибка");
    }
  };

  const onForecast = async (id: number) => {
    try {
      const f = await forecastPromotionItem(id);
      setForecasts((prev) => ({ ...prev, [id]: f }));
    } catch (e: any) {
      message.error(e.response?.data?.error || "Ошибка прогноза");
    }
  };

  if (loading) return <Spin />;

  return (
    <>
      <Alert
        type="info"
        showIcon
        message="Акции маркетплейсов"
        description="Здесь видно, в какие акции попали ваши товары. Прогноз маржи показывает, выгодно ли участие. Если маржа < 0 — это убыток."
        style={{ marginBottom: 16 }}
      />

      <Table
        dataSource={items}
        rowKey="id"
        columns={[
          { title: "ID", dataIndex: "id", width: 60 },
          { title: "Вариант", dataIndex: "variant_name" },
          {
            title: "Предложенная цена",
            dataIndex: "proposed_price",
            render: (v: string) => `${v} ₽`,
          },
          {
            title: "Маржа",
            render: (_, item: PromotionItem) => {
              const f = forecasts[item.id];
              const margin = f?.margin ?? item.margin_at_proposed;
              if (margin === null || margin === undefined) {
                return <span style={{ color: "#999" }}>— (нажми «Прогноз»)</span>;
              }
              const value = Number(margin);
              const isLoss = value < 0;
              return (
                <Tag color={isLoss ? "red" : value < 100 ? "orange" : "green"}>
                  {value.toFixed(2)} ₽
                  {isLoss && " (УБЫТОК)"}
                </Tag>
              );
            },
          },
          {
            title: "Решение",
            dataIndex: "decision",
            render: (d: string) => (
              <Tag color={DECISION_COLOR[d]}>
                {d === "pending" ? "Не решено" : d === "accepted" ? "Участвуем" : "Отказались"}
              </Tag>
            ),
          },
          {
            title: "Действия",
            render: (_, item: PromotionItem) => (
              <Space>
                <Button
                  size="small"
                  icon={<CalculatorOutlined />}
                  onClick={() => onForecast(item.id)}
                >
                  Прогноз
                </Button>
                <Popconfirm
                  title="Участвовать в акции?"
                  onConfirm={() => onDecide(item.id, "accepted")}
                >
                  <Button
                    size="small"
                    type="primary"
                    icon={<CheckOutlined />}
                    disabled={item.decision === "accepted"}
                  >
                    Участвовать
                  </Button>
                </Popconfirm>
                <Popconfirm
                  title="Отказаться от акции?"
                  onConfirm={() => onDecide(item.id, "declined")}
                >
                  <Button
                    size="small"
                    danger
                    icon={<CloseOutlined />}
                    disabled={item.decision === "declined"}
                  >
                    Отказаться
                  </Button>
                </Popconfirm>
              </Space>
            ),
          },
        ]}
      />
    </>
  );
}