const RAW_API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8001";
const API_URL = RAW_API_URL.replace(/\/+$/, "");
const TOKEN_KEY = "planetpulse.access_token";

async function request(path, options) {
  const headers = new Headers(options?.headers || {});
  const token = localStorage.getItem(TOKEN_KEY);
  if (token) headers.set("Authorization", `Bearer ${token}`);
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), 30000);

  let response;
  try {
    response = await fetch(`${API_URL}${path}`, { ...options, headers, signal: controller.signal });
  } catch (error) {
    if (error.name === "AbortError") {
      console.error(`[PlanetPulse Timeout] ${path} request timed out`);
      throw new Error("The request timed out. Please try again.");
    }
    console.error(`[PlanetPulse Network Error] ${path}`, error);
    throw new Error("Unable to reach PlanetPulse. Check your connection and try again.");
  } finally {
    window.clearTimeout(timeout);
  }
  const result = await response.json().catch(() => ({}));
  if (!response.ok) {
    if (response.status === 401 && !path.startsWith("/auth/")) window.dispatchEvent(new Event("planetpulse:unauthorized"));
    console.error(`[PlanetPulse API ${response.status}] ${path}:`, result);
    const detail = result.detail ?? result.message;
    const message = typeof detail === "string" && detail.trim()
      ? detail
      : Array.isArray(detail)
        ? detail.map((item) => item.msg).filter(Boolean).join(" ")
        : response.status >= 500
          ? "PlanetPulse service is temporarily unavailable. Please try again."
          : `Request failed (${response.status})`;
    throw new Error(message);
  }
  return result;

}

export const api = {
  TOKEN_KEY,
  register: (credentials) => request("/auth/register", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(credentials) }),
  login: (credentials) => request("/auth/login", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(credentials) }),
  getMe: () => request("/auth/me"),
  getDashboard: () => request("/dashboard"),
  getActivities: () => request("/activities"),
  getTrend: (period) => request(`/trend?period=${encodeURIComponent(period)}`),
  getGoal: () => request("/goals/monthly"),
  updateGoal: (target) => request("/goals/monthly", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ target }),
  }),
  getInsights: () => request("/insights"),
  addActivity: (activity) => request("/activities", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(activity),
  }),
  simulateWhatIf: (scenario) => request("/what-if", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(scenario),
  }),
};
