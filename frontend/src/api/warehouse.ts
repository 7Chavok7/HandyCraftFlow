import { api } from "./client";
import type { Paginated } from "../types";

export interface Warehouse {
  id: number;
  workspace_id: string;
  name: string;
  type: string;
  seller_account: number | null;
  is_active: boolean;
}

export interface Stock {
  id: number;
  variant: number;
  variant_name: string;
  warehouse: number;
  qty: string;
  reserved_qty: string;
  available_qty: string;
  updated_at: string;
}

export interface StockLedgerEntry {
  id: number;
  variant: number;
  warehouse: number;
  movement_type: string;
  qty: string;
  comment: string;
  created_at: string;
}

export async function fetchWarehouses(): Promise<Warehouse[]> {
  const { data } = await api.get<Paginated<Warehouse>>("/warehouses/");
  return data.results;
}

export async function fetchStocks(warehouseId?: number): Promise<Stock[]> {
  const params = warehouseId ? { warehouse: warehouseId } : {};
  const { data } = await api.get<Paginated<Stock>>("/stocks/", { params });
  return data.results;
}

export async function adjustStock(
  id: number, newQty: string, comment = ""
): Promise<Stock> {
  const { data } = await api.post<Stock>(`/stocks/${id}/adjust/`, {
    new_qty: newQty, comment,
  });
  return data;
}

export async function reserveStock(
  id: number, qty: string, comment = ""
): Promise<Stock> {
  const { data } = await api.post<Stock>(`/stocks/${id}/reserve/`, {
    qty, comment,
  });
  return data;
}

export async function unreserveStock(
  id: number, qty: string, comment = ""
): Promise<Stock> {
  const { data } = await api.post<Stock>(`/stocks/${id}/unreserve/`, {
    qty, comment,
  });
  return data;
}

export async function fetchStockLedger(params: {
  variant?: number;
  warehouse?: number;
}): Promise<StockLedgerEntry[]> {
  const { data } = await api.get<Paginated<StockLedgerEntry>>(
    "/stock-ledger/", { params }
  );
  return data.results;
}