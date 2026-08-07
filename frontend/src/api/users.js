import { api } from "./client";

export async function updateProfile(data) {
  return await api.put("/users/me", data);
}
