import { useEffect, useState } from "react";
import {
  Table, Spin, Tag, Button, Modal, Form, InputNumber, Input,
  Select, Space, message, Empty,
} from "antd";
import {
  EditOutlined, LockOutlined, UnlockOutlined,
} from "@ant-design/icons";
import {
  fetchWarehouses, fetchStocks, fetchStockLedger,
  adjustStock, reserveStock, unreserveStock,
  type Warehouse, type Stock, type StockLedgerEntry,
} from "../api/warehouse";

export default function WarehousePage() {
  const [warehouses, setWarehouses] = useState<Warehouse[]>([]);
  const [stocks, setStocks] = useState<Stock[]>([]);
  const [selectedWh, setSelectedWh] = useState<number | undefined>();
  const [loading, setLoading] = useState(true);

  // модалки
  const [adjustOpen, setAdjustOpen] = useState(false);
  const [reserveOpen, setReserveOpen] = useState(false);
  const [unreserveOpen, setUnreserveOpen] = useState(false);
  const [currentStock, setCurrentStock] = useState<Stock | null>(null);
  const [ledger, setLedger] = useState<StockLedgerEntry[]>([]);
  const [ledgerOpen, setLedgerOpen] = useState(false);

  const [adjustForm] = Form.useForm();
  const [reserveForm] = Form.useForm();
  const [unreserveForm] = Form.useForm();

  const load = () => {
    setLoading(true);
    Promise.all([fetchWarehouses(), fetchStocks(selectedWh)])
      .then(([w, s]) => {
        setWarehouses(w);
        setStocks(s);
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, [selectedWh]);

  const doAdjust = async (values: any) => {
    if (!currentStock) return;
    try {
      await adjustStock(currentStock.id, values.new_qty, values.comment || "");
      message.success("Остаток обновлён");
      setAdjustOpen(false);
      load();
    } catch (e: any) {
      message.error(e.response?.data?.error || "Ошибка");
    }
  };

  const doReserve = async (values: any) => {
    if (!currentStock) return;
    try {
      await reserveStock(currentStock.id, values.qty, values.comment || "");
      message.success("Резерв создан");
      setReserveOpen(false);
      load();
    } catch (e: any) {
      message.error(e.response?.data?.error || "Ошибка");
    }
  };

  const doUnreserve = async (values: any) => {
    if (!currentStock) return;
    try {
      await unreserveStock(currentStock.id, values.qty, values.comment || "");
      message.success("Резерв снят");
      setUnreserveOpen(false);
      load();
    } catch (e: any) {
      message.error(e.response?.data?.error || "Ошибка");
    }
  };

  const openLedger = async (stock: Stock) => {
    setCurrentStock(stock);
    const entries = await fetchStockLedger({ variant: stock.variant });
    setLedger(entries);
    setLedgerOpen(true);
  };

  if (loading) return <Spin />;

  return (
    <>
      <Space style={{ marginBottom: 16 }}>
        <span>Склад:</span>
        <Select
          allowClear
          placeholder="Все склады"
          style={{ width: 300 }}
          value={selectedWh}
          onChange={setSelectedWh}
          options={warehouses.map((w) => ({
            value: w.id,
            label: `${w.name} (${w.type})`,
          }))}
        />
      </Space>

      <Table
        dataSource={stocks}
        rowKey="id"
        columns={[
          { title: "Вариант", dataIndex: "variant_name" },
          {
            title: "Склад",
            render: (_, s: Stock) => (
              <span>{s.warehouse_name}</span>
              // <span>{s.warehouse_name} <Tag>{s.warehouse_type}</Tag></span>
            ),
          },
          { title: "Кол-во", dataIndex: "qty" },
          { title: "Резерв", dataIndex: "reserved_qty" },
          {
            title: "Доступно",
            dataIndex: "available_qty",
            render: (v: string) => <Tag color="green">{v}</Tag>,
          },
          {
            title: "Действия",
            render: (_, s: Stock) => (
              <Space>
                <Button
                  size="small"
                  icon={<EditOutlined />}
                  onClick={() => {
                    setCurrentStock(s);
                    adjustForm.setFieldsValue({ new_qty: s.qty });
                    setAdjustOpen(true);
                  }}
                >
                  Инвентаризация
                </Button>
                <Button
                  size="small"
                  icon={<LockOutlined />}
                  onClick={() => {
                    setCurrentStock(s);
                    reserveForm.resetFields();
                    setReserveOpen(true);
                  }}
                >
                  Резерв
                </Button>
                <Button
                  size="small"
                  icon={<UnlockOutlined />}
                  onClick={() => {
                    setCurrentStock(s);
                    unreserveForm.resetFields();
                    setUnreserveOpen(true);
                  }}
                >
                  Снять
                </Button>
                <Button size="small" onClick={() => openLedger(s)}>
                  История
                </Button>
              </Space>
            ),
          },
        ]}
      />

      <Modal
        title={`Инвентаризация: ${currentStock?.variant_name}`}
        open={adjustOpen}
        onCancel={() => setAdjustOpen(false)}
        onOk={() => adjustForm.submit()}
      >
        <Form form={adjustForm} layout="vertical" onFinish={doAdjust}>
          <Form.Item label="Фактический остаток" name="new_qty" rules={[{ required: true }]}>
            <InputNumber min={0} step={0.001} style={{ width: "100%" }} />
          </Form.Item>
          <Form.Item label="Комментарий" name="comment">
            <Input.TextArea rows={2} />
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        title={`Резерв: ${currentStock?.variant_name}`}
        open={reserveOpen}
        onCancel={() => setReserveOpen(false)}
        onOk={() => reserveForm.submit()}
      >
        <Form form={reserveForm} layout="vertical" onFinish={doReserve}>
          <Form.Item label="Количество" name="qty" rules={[{ required: true }]}>
            <InputNumber min={0.001} step={0.001} style={{ width: "100%" }} />
          </Form.Item>
          <Form.Item label="Комментарий" name="comment">
            <Input.TextArea rows={2} />
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        title={`Снятие резерва: ${currentStock?.variant_name}`}
        open={unreserveOpen}
        onCancel={() => setUnreserveOpen(false)}
        onOk={() => unreserveForm.submit()}
      >
        <Form form={unreserveForm} layout="vertical" onFinish={doUnreserve}>
          <Form.Item label="Количество" name="qty" rules={[{ required: true }]}>
            <InputNumber min={0.001} step={0.001} style={{ width: "100%" }} />
          </Form.Item>
          <Form.Item label="Комментарий" name="comment">
            <Input.TextArea rows={2} />
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        title={`История: ${currentStock?.variant_name}`}
        open={ledgerOpen}
        onCancel={() => setLedgerOpen(false)}
        footer={null}
        width={800}
      >
        {ledger.length === 0 ? (
          <Empty />
        ) : (
          <Table
            dataSource={ledger}
            rowKey="id"
            pagination={false}
            size="small"
            columns={[
              { title: "Дата", dataIndex: "created_at" },
              { title: "Тип", dataIndex: "movement_type" },
              { title: "Кол-во", dataIndex: "qty" },
              { title: "Комментарий", dataIndex: "comment" },
            ]}
          />
        )}
      </Modal>
    </>
  );
}