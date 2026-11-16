import { farmApi } from "./client";
import type { FarmPrinter, FarmJob, Paginated } from "../types";

export async function fetchPrinters(): Promise<FarmPrinter[]> {
  const { data } = await farmApi.get<Paginated<FarmPrinter>>("/printers/");
  return data.results;
}

export async function fetchFarmJobs(): Promise<FarmJob[]> {
  const { data } = await farmApi.get<Paginated<FarmJob>>("/jobs/");
  return data.results;
}