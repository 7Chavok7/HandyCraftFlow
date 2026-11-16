import { useEffect, useState } from "react";
import { Table, Spin, Tag, Button, Modal, Form, InputNumber, Input, message } from "antd";
import { CheckOutlined } from "@ant-design/icons";
import { fetchJobs, completeJob } from "../api/production";
import type { ProductionJob } from "../api/production";

const STATUS_COLOR: Record<string, string> = {
  queued: "default",
  assigned: "blue",
  printing: "processing",
  done: "green",
  cancelled: "red",
  error: "red",
};

export default function ProductionPage() {
  const [jobs, setJobs] = useState<ProductionJob[]>([]);
  const [loading, setLoading] = useState(true);
  const [completeOpen, setCompleteOpen] = useState(false);
  const [currentJob, setCurrentJob] = useState<ProductionJob | null>(null);
  const [form] = Form.useForm();

  const load = () => {
    setLoading(true);
    fetchJobs()
      .then(setJobs)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
  }, []);

  const openComplete = (job: ProductionJob) => {
    setCurrentJob(job);
    form.setFieldsValue({
      qty_done: job.qty_planned,
      qty_waste: 0,
      actual_weight: job.expected_weight ?? "",
      actual_time_min: job.expected_time_min ?? "",
    });
    setCompleteOpen(true);
  };

  const submitComplete = async (values: any) => {
    if (!currentJob) return;
    try {
      await completeJob(currentJob.id, values);
      message.success("Задание завершено, склад обновлён");
      setCompleteOpen(false);
      load();
    } catch (e: any) {
      message.error(e.response?.data?.error || "Ошибка");
    }
  };

  if (loading) return <Spin />;

  return (
    <>
      <Table
        title={() => "Производственные задания"}
        dataSource={jobs}
        rowKey="id"
        columns={[
          { title: "ID", dataIndex: "id", width: 60 },
          { title: "Вариант", dataIndex: "variant_name" },
          {
            title: "Статус",
            dataIndex: "status",
            render: (s: string) => <Tag color={STATUS_COLOR[s]}>{s}</Tag>,
          },
          { title: "План", dataIndex: "qty_planned" },
          { title: "Готово", dataIndex: "qty_done" },
          { title: "Брак", dataIndex: "qty_waste" },
          {
            title: "Действие",
            render: (_, j: ProductionJob) =>
              j.status !== "done" && j.status !== "cancelled" ? (
                <Button
                  type="primary"
                  size="small"
                  icon={<CheckOutlined />}
                  onClick={() => openComplete(j)}
                >
                  Завершить
                </Button>
              ) : null,
          },
        ]}
      />

      <Modal
        title={`Завершить задание #${currentJob?.id}`}
        open={completeOpen}
        onCancel={() => setCompleteOpen(false)}
        onOk={() => form.submit()}
      >
        <Form form={form} layout="vertical" onFinish={submitComplete}>
          <Form.Item label="Готово, шт" name="qty_done" rules={[{ required: true }]}>
            <InputNumber min={0} style={{ width: "100%" }} />
          </Form.Item>
          <Form.Item label="Брак, шт" name="qty_waste">
            <InputNumber min={0} style={{ width: "100%" }} />
          </Form.Item>
          <Form.Item label="Фактический вес, г" name="actual_weight">
            <InputNumber min={0} step={0.001} style={{ width: "100%" }} />
          </Form.Item>
          <Form.Item label="Фактическое время, мин" name="actual_time_min">
            <InputNumber min={0} style={{ width: "100%" }} />
          </Form.Item>
          <Form.Item label="Комментарий" name="comment">
            <Input.TextArea rows={2} />
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
}