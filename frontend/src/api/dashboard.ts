import { api } from "./client";
import type { TodayDashboard, Product, Paginated } from "../types";


export interface CurrentWorkspace {
  id: string;
  name: string;
}

export async function fetchCurrentWorkspace(): Promise<CurrentWorkspace> {
  const { data } = await api.get<CurrentWorkspace>("/me/workspace/");
  return data;
}


export async function fetchTodayDashboard(
  workspaceId: string
): Promise<TodayDashboard> {
  const { data } = await api.get<TodayDashboard>("/dashboard/today/", {
    params: { workspace_id: workspaceId },
  });
  return {
    queued_jobs: data.queued_jobs ?? [],
    pending_promotions: data.pending_promotions ?? [],
    low_stocks: data.low_stocks ?? [],
    unread_alerts: data.unread_alerts ?? [],
  };
}

export async function fetchProducts(): Promise<Product[]> {
  const { data } = await api.get<Paginated<Product>>("/products/");
  return data.results;
}