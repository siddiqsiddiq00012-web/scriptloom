import { api } from "./client";

export async function updateProfile(data) {
  return await api.put("/users/me", data);
}

export async function changePassword(data) {
  return await api.post("/users/me/change-password", data);
}

export async function deleteAccount() {
  return await api.delete("/users/me");
}

export async function exportAccountData() {
  return await api.get("/users/me/export");
}
