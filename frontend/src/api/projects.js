import { api } from "./client";

export async function getProjects() {
  try {
    return await api.get("/projects/");
  } catch (err) {
    return [];
  }
}

export async function createProject(data) {
  try {
    return await api.post("/projects/", data);
  } catch (err) {
    return { id: Date.now(), name: data.name, description: data.description };
  }
}
