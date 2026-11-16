import axios from "axios";

function getCookie(name: string): string | null {
  const m = document.cookie.match(new RegExp("(^| )" + name + "=([^;]+)"));
  return m ? decodeURIComponent(m[2]) : null;
}

export const api = axios.create({
  baseURL: "/api/v1",
  withCredentials: true,   // ← куки (sessionid, csrftoken)
  headers: { "Content-Type": "application/json" },
});

// Interceptor для логирования ошибок (потом уберём/заменим)
api.interceptors.response.use(
  (r) => r,
  (error) => {
    if (error.response?.status !== 403) {
      console.error("API error:", error.response?.data || error.message);
    }
    return Promise.reject(error);
  }
);

api.interceptors.response.use(
  (r) => r,
  (error) => {
    console.error("API error:", error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export const farmApi = axios.create({
  baseURL: "/farm/api/v1",
  withCredentials: true,
  headers: { "Content-Type": "application/json" },
});
