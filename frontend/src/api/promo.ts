import { api } from "./client";
import type { Paginated } from "../types";

export interface Promotion {
  id: number;
  workspace_id: string;
  marketplace: string;
  external_id: string;
  name: string;
  starts_at: string;
  ends_at: string;
  discount_percent: string;
  items: PromotionItem[];
  created_at: string;
}

export interface PromotionItem {
  id: number;
  promotion: number;
  variant: number;
  variant_name: string;
  proposed_price: string;
  margin_at_proposed: string | null;
  snapshot_cost: string | null;
  decision: string;
  decided_at: string | null;
  comment: string;
}

export interface Forecast {
  variant: string;
  proposed_price: string;
  cost: string;
  margin: string;
  is_loss: boolean;
}

export async function fetchPromotions(): Promise<Promotion[]> {
  const { data } = await api.get<Paginated<Promotion>>("/promotions/");
  return data.results;
}

export async function fetchPromotionItems(): Promise<PromotionItem[]> {
  const { data } = await api.get<Paginated<PromotionItem>>("/promotion-items/");
  return data.results;
}

export async function decidePromotionItem(
  id: number, decision: "accepted" | "declined" | "pending"
): Promise<PromotionItem> {
  const { data } = await api.post<PromotionItem>(
    `/promotion-items/${id}/decide/`, { decision }
  );
  return data;
}

export async function forecastPromotionItem(id: number): Promise<Forecast> {
  const { data } = await api.get<Forecast>(
    `/promotion-items/${id}/forecast/`
  );
  return data;
}