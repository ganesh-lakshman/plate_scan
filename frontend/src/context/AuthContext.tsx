import { createContext, useContext, useState, ReactNode } from "react";

interface AuthState {
  token: string | null;
  userId: string | null;
  username: string | null;
  tenantId: string | null;
  tenantName: string | null;
  role: string | null;
}

interface AuthContextType extends AuthState {
  login: (data: LoginData) => void;
  logout: () => void;
}

interface LoginData {
  access_token: string;
  user_id: string;
  username: string;
  tenant_id: string;
  tenant_name: string;
  role: string;
}

const STORAGE_KEY = "plate_scan_auth";

function loadFromStorage(): AuthState {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) return JSON.parse(raw);
  } catch {}
  return { token: null, userId: null, username: null, tenantId: null, tenantName: null, role: null };
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>(loadFromStorage);

  const login = (data: LoginData) => {
    const newState: AuthState = {
      token: data.access_token,
      userId: data.user_id,
      username: data.username,
      tenantId: data.tenant_id,
      tenantName: data.tenant_name,
      role: data.role,
    };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(newState));
    setState(newState);
  };

  const logout = () => {
    localStorage.removeItem(STORAGE_KEY);
    setState({ token: null, userId: null, username: null, tenantId: null, tenantName: null, role: null });
  };

  return (
    <AuthContext.Provider value={{ ...state, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be inside AuthProvider");
  return ctx;
}
