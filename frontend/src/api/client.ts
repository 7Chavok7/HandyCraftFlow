import axios from "axios";

function getCookie(name: string): string | null {
  const m = document.cookie.match(new RegExp("(^| )" + name + "=([^;]+)"));
  return m ? decodeURIComponent(m[2]) : null;
}

export const api = axios.create({
  baseURL: "/api/v1",
  withCredentials: true,
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use((config) => {
  const method = (config.method || "").toLowerCase();
  if (["post", "put", "patch", "delete"].includes(method)) {
    const token = getCookie("csrftoken");
    if (token) {
      // Для axios 1.x: используем headers.set()
      if (config.headers && typeof (config.headers as any).set === "function") {
        (config.headers as any).set("X-CSRFToken", token);
      } else {
        config.headers = config.headers || {};
        (config.headers as any)["X-CSRFToken"] = token;
      }
    }
  }
  return config;
});

api.interceptors.response.use(
  (r) => r,
  (error) => {
    if (error.response?.status !== 403) {
      console.error("API error:", error.response?.data || error.message);
    }
    return Promise.reject(error);
  }
);

export const farmApi = axios.create({
  baseURL: "/farm/api/v1",
  withCredentials: true,
  headers: { "Content-Type": "application/json" },
});