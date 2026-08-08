import { config } from "../config";

const BASE_URL = config.apiUrl;
const CSRF_HEADER = "X-CSRF-Token";

export async function apiRequest(endpoint, options = {}) {
  const headers = {
    "Content-Type": "application/json",
    ...options.headers,
  };

  // If formData, let browser handle Content-Type boundary
  if (options.body instanceof FormData) {
    delete headers["Content-Type"];
  }

  // Attach CSRF token for state-changing requests so the httpOnly
  // cookie auth stays protected against cross-site request forgery.
  const method = (options.method || "GET").toUpperCase();
  if (method !== "GET" && method !== "HEAD" && method !== "OPTIONS") {
    const csrfToken = getCsrfToken();
    if (csrfToken) headers[CSRF_HEADER] = csrfToken;
  }

  const response = await fetch(`${BASE_URL}${endpoint}`, {
    ...options,
    headers,
    credentials: "include",
  });

  if (!response.ok) {
    if (response.status === 401 && !endpoint.startsWith("/auth/")) {
      clearAuthState();
      if (window.location.pathname !== "/login") {
        window.location.href = "/login";
      }
    }

    let errorDetail = "API Request Failed";
    try {
      const errJson = await response.json();
      errorDetail = errJson.detail || errorDetail;
    } catch {
      // fallback
    }
    const error = new Error(errorDetail);
    error.status = response.status;
    throw error;
  }

  // Handle 204 No Content (e.g. DELETE)
  if (response.status === 204) {
    return null;
  }

  // Handle binary blob responses (e.g. ZIP export)
  const contentType = response.headers.get("content-type");
  if (contentType && (contentType.includes("application/zip") || contentType.includes("octet-stream"))) {
    return await response.blob();
  }

  return await response.json();
}

function getCsrfToken() {
  const match = document.cookie.match(/(?:^|;\s*)csrf_token=([^;]*)/);
  return match ? decodeURIComponent(match[1]) : null;
}

export function clearAuthState() {
  localStorage.removeItem("token");
  localStorage.removeItem("user_email");
  localStorage.removeItem("user_name");
  localStorage.removeItem("user_avatar");
}

export const api = {
  get: (endpoint) => apiRequest(endpoint, { method: "GET" }),
  post: (endpoint, body) =>
    apiRequest(endpoint, {
      method: "POST",
      body: body instanceof FormData ? body : JSON.stringify(body),
    }),
  put: (endpoint, body) =>
    apiRequest(endpoint, {
      method: "PUT",
      body: JSON.stringify(body),
    }),
  patch: (endpoint, body) =>
    apiRequest(endpoint, {
      method: "PATCH",
      body: JSON.stringify(body),
    }),
  delete: (endpoint) => apiRequest(endpoint, { method: "DELETE" }),
};
