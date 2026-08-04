import { api } from "./client";

export async function getProjectClips(projectId) {
  return await api.get(`/clips/project/${projectId}`);
}