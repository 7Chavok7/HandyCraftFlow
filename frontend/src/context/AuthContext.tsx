import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { fetchMe, type Me } from "../api/auth";
import { api } from "../api/client";

interface AuthContextValue {
  me: Me | null;
  loading: boolean;
  refresh: () => Promise<void>;
  setMe: (me: Me | null) => void;
}

api.get("/auth/csrf/").catch(() => {});
const AuthContext = createContext<AuthContextValue>({
  me: null,
  loading: true,
  refresh: async () => {},
  setMe: () => {},
});

export function AuthProvider({ children }: { children: ReactNode }) {
  const [me, setMe] = useState<Me | null>(null);
  const [loading, setLoading] = useState(true);

  const refresh = async () => {
    try {
      await api.get("/auth/csrf/");   // ← получить csrftoken в cookie
      const m = await fetchMe();
      setMe(m);
    } catch {
      setMe(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refresh();
  }, []);

  return (
    <AuthContext.Provider value={{ me, loading, refresh, setMe }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}