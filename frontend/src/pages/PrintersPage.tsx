import { useEffect, useState } from "react";
import { Table, Spin, Tag } from "antd";
import { fetchPrinters, fetchFarmJobs } from "../api/farm";
import type { FarmPrinter, FarmJob } from "../types";

const STATUS_COLOR: Record<string, string> = {
  free: "green",
  printing: "blue",
  paused: "orange",
  error: "red",
  offline: "default",
};

export default function PrintersPage() {
  const [printers, setPrinters] = useState<FarmPrinter[]>([]);
  const [jobs, setJobs] = useState<FarmJob[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([fetchPrinters(), fetchFarmJobs()])
      .then(([p, j]) => {
        setPrinters(p);
        setJobs(j);
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <Spin />;

  return (
    <>
      <Table
        title={() => "Принтеры"}
        dataSource={printers}
        rowKey="id"
        pagination={false}
        style={{ marginBottom: 24 }}
        columns={[
          { title: "Имя", dataIndex: "name" },
          { title: "Модель", dataIndex: "model" },
          {
            title: "Статус",
            dataIndex: "status",
            render: (s: string) => <Tag color={STATUS_COLOR[s]}>{s}</Tag>,
          },
        ]}
      />
      <Table
        title={() => "Задания"}
        dataSource={jobs}
        rowKey="id"
        columns={[
          { title: "ID", dataIndex: "id", width: 60 },
          { title: "Статус", dataIndex: "status" },
          { title: "План", dataIndex: "qty_planned" },
          { title: "Готово", dataIndex: "qty_done" },
          { title: "Брак", dataIndex: "qty_waste" },
        ]}
      />
    </>
  );
}