import { api } from "./client";

export async function getProjects() {
  return await api.get("/projects");
}

export async function getProject(projectId) {
  return await api.get(`/projects/${projectId}`);
}

export async function createProject(data) {
  return await api.post("/projects", data);
}

export async function updateProject(projectId, data) {
  return await api.patch(`/projects/${projectId}`, data);
}

export async function deleteProject(projectId) {
  return await api.delete(`/projects/${projectId}`);
}