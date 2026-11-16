import { api } from "./client";
import type { Paginated } from "../types";

export interface ProductionJob {
  id: number;
  workspace_id: string;
  variant: number;
  variant_name: string;
  profile: number | null;
  material_batch: number | null;
  equipment_id: string | null;
  qty_planned: number;
  qty_done: number;
  qty_waste: number;
  expected_weight: string | null;
  expected_time_min: number | null;
  actual_weight: string | null;
  actual_time_min: number | null;
  status: string;
  comment: string;
  created_at: string;
  started_at: string | null;
  finished_at: string | null;
}

export async function fetchJobs(): Promise<ProductionJob[]> {
  const { data } = await api.get<Paginated<ProductionJob>>("/jobs/");
  return data.results;
}

export async function createJob(payload: {
  workspace_id: string;
  variant: number;
  qty_planned: number;
  material_batch?: number | null;
}): Promise<ProductionJob> {
  const { data } = await api.post<ProductionJob>("/jobs/", payload);
  return data;
}

export async function completeJob(
  id: number,
  payload: {
    qty_done: number;
    qty_waste?: number;
    actual_weight?: string;
    actual_time_min?: number;
    comment?: string;
  }
): Promise<ProductionJob> {
  const { data } = await api.post<ProductionJob>(
    `/jobs/${id}/complete/`, payload
  );
  return data;
}