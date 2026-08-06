import { config } from "../config";

const BASE_URL = config.apiUrl;

export async function apiRequest(endpoint, options = {}) {
  const token = localStorage.getItem("token");
  const headers = {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  };

  // If formData, let browser handle Content-Type boundary
  if (options.body instanceof FormData) {
    delete headers["Content-Type"];
  }

  const response = await fetch(`${BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    if (response.status === 401) {
      localStorage.removeItem("token");
      localStorage.removeItem("user_email");
      localStorage.removeItem("user_name");
      localStorage.removeItem("user_avatar");
      if (window.location.pathname !== "/login") {
        window.location.href = "/login";
      }
    }

    let errorDetail = "API Request Failed";
    try {
      const errJson = await response.json();
      errorDetail = errJson.detail || errorDetail;
    } catch (e) {
      // fallback
    }
    throw new Error(errorDetail);
  }

  // Handle binary blob responses (e.g. ZIP export)
  const contentType = response.headers.get("content-type");
  if (contentType && (contentType.includes("application/zip") || contentType.includes("octet-stream"))) {
    return await response.blob();
  }

  return await response.json();
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
