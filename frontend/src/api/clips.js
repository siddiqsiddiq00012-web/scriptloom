import { config } from "../config";
import { api } from "./client";

export async function getProjectClips(projectId) {
  return await api.get(`/clips/project/${projectId}`);
}

export async function getClipStreamUrl(clipId) {
  const token = localStorage.getItem("token");
  
  const response = await fetch(`${config.apiUrl}/clips/${clipId}/stream`, {
    headers: {
      "Authorization": `Bearer ${token}`
    }
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch clip stream: ${response.status}`);
  }

  const blob = await response.blob();
  return URL.createObjectURL(blob);
}