import { api } from "./client";

export async function registerUser(name, email, password) {
  if (!email || !password) {
    throw new Error("Email and password are required for registration.");
  }
  const data = await api.post("/auth/register", { name: name || email.split("@")[0], email, password });
  if (data.access_token) {
    localStorage.setItem("token", data.access_token);
    localStorage.setItem("user_email", data.user?.email || email);
    localStorage.setItem("user_name", data.user?.name || name || email.split("@")[0]);
  }
  return data;
}

export async function loginUser(email, password) {
  if (!email || !password) {
    throw new Error("Email and password are required.");
  }
  const data = await api.post("/auth/login", { email, password });
  if (data.access_token) {
    localStorage.setItem("token", data.access_token);
    if (data.user) {
      localStorage.setItem("user_email", data.user.email || email);
      localStorage.setItem("user_name", data.user.name || email.split("@")[0]);
      if (data.user.avatar_url) localStorage.setItem("user_avatar", data.user.avatar_url);
    }
  }
  return data;
}

export async function loginWithGoogle(credential) {
  if (!credential) {
    throw new Error("Google credential is required.");
  }

  const data = await api.post("/auth/google", {
    credential: credential
  });

  if (data.access_token) {
    localStorage.setItem("token", data.access_token);
    if (data.user) {
      localStorage.setItem("user_email", data.user.email);
      localStorage.setItem("user_name", data.user.name);
      if (data.user.avatar_url) localStorage.setItem("user_avatar", data.user.avatar_url);
    }
  }
  return data;
}

export function isAuthenticated() {
  return !!localStorage.getItem("token");
}

export function getUserProfile() {
  const email = localStorage.getItem("user_email");
  const name = localStorage.getItem("user_name");
  const avatarUrl = localStorage.getItem("user_avatar");

  if (!email && !name) {
    return null;
  }

  const plan = localStorage.getItem("user_plan") || "Free Creator";

  return {
    email: email || "Unsaved User",
    name: name || (email ? email.split("@")[0] : "Creator"),
    avatarUrl: avatarUrl || "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=120&q=80",
    plan,
  };
}

export function logoutUser() {
  localStorage.removeItem("token");
  localStorage.removeItem("user_email");
  localStorage.removeItem("user_name");
  localStorage.removeItem("user_avatar");
}

export async function getCurrentUser() {
  try {
    const user = await api.get("/auth/me");
    if (user) {
      localStorage.setItem("user_email", user.email);
      localStorage.setItem("user_name", user.name);
      if (user.avatar_url) localStorage.setItem("user_avatar", user.avatar_url);
    }
    return user;
  } catch {
    return null;
  }
}
