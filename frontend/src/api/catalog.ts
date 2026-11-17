import { api } from "./client";
import type { Product, Paginated, ProductVariant } from "../types";

export interface VariantDetail {
  variant: {
    id: number;
    product: number;
    name: string;
    color: number | null;
    vendor_code: string;
    barcode: string;
    extra_cost: string;
    is_active: boolean;
  };
  all_variants: Array<{
    id: number;
    product: number;
    product_name: string;
    name: string;
    vendor_code: string;
    barcode: string;
    extra_cost: string;
    is_active: boolean;
    image: string | null;
  }>;
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
    warehouse_name: string;
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
  return {
    ...data,
    all_variants: data.all_variants ?? [],
    stocks: data.stocks ?? [],
  };
}

export async function fetchProductsList(): Promise<Product[]> {
  const { data } = await api.get<Paginated<Product>>("/products/");
  return data.results;
}

export async function createProduct(formData: FormData): Promise<Product> {
  const { data } = await api.post<Product>("/products/", formData);
  return data;
}

export async function updateProduct(
  id: number, formData: FormData
): Promise<Product> {
  const { data } = await api.patch<Product>(`/products/${id}/`, formData);
  return data;
}

export async function deleteProduct(id: number): Promise<void> {
  await api.delete(`/products/${id}/`);
}

export async function createVariant(formData: FormData): Promise<ProductVariant> {
  const { data } = await api.post<ProductVariant>("/variants/", formData);
  return data;
}

export async function updateVariant(
  id: number, formData: FormData
): Promise<ProductVariant> {
  const { data } = await api.patch<ProductVariant>(`/variants/${id}/`, formData);
  return data;
}

export async function deleteVariant(id: number): Promise<void> {
  await api.delete(`/variants/${id}/`);
}