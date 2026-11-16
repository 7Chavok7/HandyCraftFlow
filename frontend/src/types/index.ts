export interface Paginated<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface Unit {
  id: number;
  name: string;
  short_name: string;
}

export interface Product {
  id: number;
  name: string;
  category: number | null;
  description: string;
  is_active: boolean;
  variants: ProductVariant[];
  created_at: string;
}

export interface ProductVariant {
  id: number;
  name: string;
  color: number | null;
  vendor_code: string;
  barcode: string;
  extra_cost: string;
  is_active: boolean;
}

export interface TodayDashboard {
  queued_jobs: Array<{
    id: string;
    variant: string;
    qty_planned: number;
    status: string;
  }>;
  pending_promotions: Array<{
    id: string;
    promotion: string;
    variant: string;
    proposed_price: string;
    decision: string;
  }>;
  low_stocks: Array<{
    variant: string;
    warehouse: string;
    qty: string;
    available: string;
  }>;
  unread_alerts: Array<{
    id: string;
    type: string;
    severity: string;
    title: string;
  }>;
}

export interface FarmPrinter {
  id: number;
  workspace_id: string;
  name: string;
  model: string;
  status: string;
  is_active: boolean;
}

export interface FarmJob {
  id: number;
  production_job_id: string;
  printer: number;
  status: string;
  qty_planned: number;
  qty_done: number;
  qty_waste: number;
  created_at: string;
}