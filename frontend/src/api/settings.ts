import { api } from "./client";

export interface WorkspaceSettings {
  workspace: string;
  workspace_name: string;
  labor_mode: "manual_rate" | "income_goal" | "ignore_labor";
  labor_rate: string | null;
  income_goal: string | null;
  work_hours_per_day: string;
  target_margin_percent: string;
  electricity_rate: string;
  tax_rate: string;
  equipment_hour_cost: string;
  effective_labor_rate: string;
}

export async function fetchSettings(): Promise<WorkspaceSettings> {
  const { data } = await api.get<WorkspaceSettings>("/settings/current/");
  return data;
}

export async function updateSettings(
  workspaceId: string, payload: Partial<WorkspaceSettings>
): Promise<WorkspaceSettings> {
  // Находим id настроек по workspace — или используем /settings/current/
  const list = await api.get("/settings/", {
    params: { workspace_id: workspaceId },
  });
  const id = list.data.results[0]?.id;
  if (!id) throw new Error("Settings not found");
  const { data } = await api.patch<WorkspaceSettings>(
    `/settings/${id}/`, payload
  );
  return data;
}