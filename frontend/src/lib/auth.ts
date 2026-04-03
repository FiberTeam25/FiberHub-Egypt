import api from "./api";

export function getAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("access_token");
}

export function isAuthenticated(): boolean {
  return !!getAccessToken();
}

export async function login(email: string, password: string) {
  const res = await api.post("/auth/login", { email, password });
  localStorage.setItem("access_token", res.data.access_token);
  localStorage.setItem("refresh_token", res.data.refresh_token);
  return res.data;
}

export async function register(data: {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  phone?: string;
  account_type: string;
}) {
  const res = await api.post("/auth/register", data);
  return res.data;
}

export function logout() {
  const refreshToken = localStorage.getItem("refresh_token");
  if (refreshToken) {
    api.post("/auth/logout", { refresh_token: refreshToken }).catch(() => {});
  }
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
  window.location.href = "/login";
}

export async function getCurrentUser() {
  const res = await api.get("/auth/me");
  return res.data;
}
