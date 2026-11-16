import { useEffect, useState } from "react";
import { Alert, Card, Col, Row, List, Tag, Spin, Empty } from "antd";
import { fetchTodayDashboard, fetchCurrentWorkspace } from "../api/dashboard";
import type { TodayDashboard } from "../types";

const SEVERITY_COLOR: Record<string, string> = {
  info: "blue",
  warning: "orange",
  critical: "red",
};

export default function TodayPage() {
  const [data, setData] = useState<TodayDashboard | null>(null);
  const [workspaceName, setWorkspaceName] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const ws = await fetchCurrentWorkspace();
        console.log("WS FROM API:", ws);
        setWorkspaceName(ws.name);
        console.log("CALLING DASHBOARD WITH ws.id =", ws.id);
        const dashboard = await fetchTodayDashboard(ws.id);
        console.log("DASHBOARD DATA:", JSON.stringify(dashboard, null, 2));  
        setData(dashboard);
      } catch (e: any) {
        const status = e.response?.status;
        if (status === 404) {
          setError(
            "Workspace не найден. Создайте его в админке: " +
              "/admin/workspaces/workspace/add/"
          );
        } else {
          setError(
            "Ошибка загрузки данных. Проверьте, что Core запущен на :8000."
          );
        }
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  // 1. Сначала loading
  if (loading) return <Spin />;

  // 2. Потом error
  if (error) {
    return (
      <Alert type="warning" message="Нет данных" description={error} showIcon />
    );
  }

  // 3. Потом пустота
  if (!data) return <Empty description="Нет данных" />;

  // 4. Только теперь рендер
  console.log("RENDER: data =", data);
  console.log("RENDER: queued_jobs =", data?.queued_jobs);
  console.log("RENDER: pending_promotions =", data?.pending_promotions);
  console.log("RENDER: low_stocks =", data?.low_stocks);
  console.log("RENDER: unread_alerts =", data?.unread_alerts);
  return (
    <>
      <div style={{ marginBottom: 16, fontSize: 16 }}>
        Кабинет: <strong>{workspaceName}</strong>
      </div>

      <Row gutter={16}>
        <Col span={12}>
          <Card title="Очередь производства" size="small">
            {data.queued_jobs.length === 0 ? (
              <Empty description="Нет заданий" />
            ) : (
              <List
                dataSource={data.queued_jobs}
                renderItem={(j) => (
                  <List.Item>
                    <span>{j.variant}</span>
                    <Tag>{j.status}</Tag>
                    <span>{j.qty_planned} шт</span>
                  </List.Item>
                )}
              />
            )}
          </Card>
        </Col>

        <Col span={12}>
          <Card title="Акции, ждут решения" size="small">
            {data.pending_promotions.length === 0 ? (
              <Empty description="Нет акций" />
            ) : (
              <List
                dataSource={data.pending_promotions}
                renderItem={(p) => (
                  <List.Item>
                    <span>{p.promotion}</span>
                    <span>{p.variant}</span>
                    <span>{p.proposed_price} ₽</span>
                  </List.Item>
                )}
              />
            )}
          </Card>
        </Col>

        <Col span={12} style={{ marginTop: 16 }}>
          <Card title="Заканчивается" size="small">
            {data.low_stocks.length === 0 ? (
              <Empty description="Всё в порядке" />
            ) : (
              <List
                dataSource={data.low_stocks}
                renderItem={(s) => (
                  <List.Item>
                    <span>{s.variant}</span>
                    <span>@ {s.warehouse}</span>
                    <Tag color="orange">{s.qty}</Tag>
                  </List.Item>
                )}
              />
            )}
          </Card>
        </Col>

        <Col span={12} style={{ marginTop: 16 }}>
          <Card title="Уведомления" size="small">
            {data.unread_alerts.length === 0 ? (
              <Empty description="Нет уведомлений" />
            ) : (
              <List
                dataSource={data.unread_alerts}
                renderItem={(a) => (
                  <List.Item>
                    <Tag color={SEVERITY_COLOR[a.severity]}>{a.severity}</Tag>
                    <span>{a.title}</span>
                  </List.Item>
                )}
              />
            )}
          </Card>
        </Col>
      </Row>
    </>
  );
}