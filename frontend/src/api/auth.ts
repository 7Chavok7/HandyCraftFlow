import { api } from "./client";

export interface Me {
  id: number;
  username: string;
  email: string;
  workspace_id: string | null;
  workspace_name: string;
}

export async function login(username: string, password: string): Promise<void> {
  await api.post("/auth/login/", { username, password });
}

export async function logout(): Promise<void> {
  await api.post("/auth/logout/");
}

export async function fetchMe(): Promise<Me> {
  const { data } = await api.get<Me>("/auth/me/");
  return data;
}