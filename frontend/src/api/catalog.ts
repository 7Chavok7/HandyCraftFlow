import { api } from "./client";
import type { Product, Paginated } from "../types";

export interface VariantDetail {
  variant: {
    id: number;
    name: string;
    color: number | null;
    vendor_code: string;
    barcode: string;
    extra_cost: string;
    is_active: boolean;
  };
  recipe: {
    id: number;
    variant: number;
    profile: number | null;
    labor_minutes: number;
    norms_source: string;
    avg_cost_cached: string | null;
    lines: Array<{
      id: number;
      material_type: number;
      material_type_name: string;
      qty_per_unit: string;
      waste_percent: string;
    }>;
  } | null;
  stocks: Array<{
    id: number;
    variant: number;
    variant_name: string;
    warehouse: number;
    qty: string;
    reserved_qty: string;
    available_qty: string;
  }>;
  economics: {
    marketplace: string;
    price: string;
    cost: string;
    min_price: string;
    profit_per_production_hour: string;
  };
}

export async function fetchVariantDetail(
  variantId: number,
  marketplace = "wb",
  price = "0"
): Promise<VariantDetail> {
  const { data } = await api.get<VariantDetail>(
    `/variants/${variantId}/detail/`,
    { params: { marketplace, price } }
  );
  return data;
}

export async function fetchProductsList(): Promise<Product[]> {
  const { data } = await api.get<Paginated<Product>>("/products/");
  return data.results;
}