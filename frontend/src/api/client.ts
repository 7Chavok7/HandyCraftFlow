import axios from "axios";

export const api = axios.create({
  baseURL: "/api/v1",
  headers: { "Content-Type": "application/json" },
});

export const farmApi = axios.create({
  baseURL: "/farm/api/v1",
  headers: { "Content-Type": "application/json" },
});

// Interceptor для логирования ошибок (потом уберём/заменим)
api.interceptors.response.use(
  (r) => r,
  (error) => {
    console.error("API error:", error.response?.data || error.message);
    return Promise.reject(error);
  }
);