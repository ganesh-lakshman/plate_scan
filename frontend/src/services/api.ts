import axios from "axios";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE,
});

api.interceptors.request.use((config) => {
  try {
    const raw = localStorage.getItem("plate_scan_auth");
    if (raw) {
      const { token } = JSON.parse(raw);
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
  } catch {}
  return config;
});

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user_id: string;
  username: string;
  tenant_id: string;
  tenant_name: string;
  role: string;
}

export interface CaseItem {
  id: string;
  vin: string;
  plate: string | null;
  status: string;
  tenant_id: string;
  assigned_agent_id: string | null;
  originated_by_tenant_id: string;
  created_at: string;
  claimed_at: string | null;
  closed_at: string | null;
  tenant_name: string | null;
  agent_name: string | null;
}

export interface ScanItem {
  id: string;
  camera_id: string;
  plate: string;
  vin: string;
  latitude: number;
  longitude: number;
  scanned_at: string;
  image_url: string | null;
  tenant_id: string;
  case_id: string | null;
  created_at: string;
}

export interface ClaimResponse {
  id: string;
  status: string;
  tenant_id: string;
  assigned_agent_id: string;
  claimed_at: string;
  message: string;
}

export const authApi = {
  login: (username: string, password: string) =>
    api.post<LoginResponse>("/api/v1/auth/login", { username, password }),
};

export const casesApi = {
  list: (status?: string) =>
    api.get<CaseItem[]>("/api/v1/cases", { params: status ? { status } : {} }),
  claim: (caseId: string) =>
    api.post<ClaimResponse>(`/api/v1/cases/${caseId}/claim`),
  scans: (caseId: string) =>
    api.get<ScanItem[]>(`/api/v1/cases/${caseId}/scans`),
};

export default api;
