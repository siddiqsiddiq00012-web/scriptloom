import { api, clearAuthState } from "./client";

export async function registerUser(name, email, password) {
  if (!email || !password) {
    throw new Error("Email and password are required for registration.");
  }
  const data = await api.post("/auth/register", { name: name || email.split("@")[0], email, password });
  storeUserProfile(data.user, email, name);
  return data;
}

export async function loginUser(email, password) {
  if (!email || !password) {
    throw new Error("Email and password are required.");
  }
  const data = await api.post("/auth/login", { email, password });
  storeUserProfile(data.user, email);
  return data;
}

export async function loginWithGoogle(credential) {
  if (!credential) {
    throw new Error("Google credential is required.");
  }

  const data = await api.post("/auth/google", {
    credential: credential
  });

  storeUserProfile(data.user);
  return data;
}

function storeUserProfile(user, fallbackEmail, fallbackName) {
  // The JWT now lives in an httpOnly cookie; only non-sensitive profile
  // metadata is mirrored to localStorage for quick display.
  if (user) {
    localStorage.setItem("user_email", user.email || fallbackEmail || "");
    localStorage.setItem("user_name", user.name || fallbackName || (user.email ? user.email.split("@")[0] : ""));
    if (user.avatar_url) localStorage.setItem("user_avatar", user.avatar_url);
  } else {
    if (fallbackEmail) localStorage.setItem("user_email", fallbackEmail);
    if (fallbackName) localStorage.setItem("user_name", fallbackName);
  }
}

export function isAuthenticated() {
  // The access token is in an httpOnly cookie, invisible to JS. Detect
  // the non-httpOnly session flag cookie set alongside it.
  return document.cookie.split(";").some((c) => c.trim().startsWith("session_active="));
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

export async function logoutUser() {
  try {
    await api.post("/auth/logout");
  } catch {
    // Cookie is cleared client-side regardless.
  }
  clearAuthState();
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
