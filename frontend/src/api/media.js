import { api } from "./client";

export async function uploadMediaFile(projectId, file) {
  const formData = new FormData();
  formData.append("file", file);

  return await api.post(`/projects/${projectId}/media`, formData);
}

export async function getMediaDetails(mediaId) {
  return await api.get(`/projects/media/${mediaId}`);
}

export async function getMediaWaveform(mediaId) {
  return await api.get(`/projects/media/${mediaId}/waveform`);
}

export async function deleteMediaFile(mediaId) {
  return await api.delete(`/projects/media/${mediaId}`);
}

export async function transcribeMedia(mediaId) {
  return await api.post(`/media/${mediaId}/transcribe`);
}

export async function getMediaTranscript(mediaId) {
  return await api.get(`/media/${mediaId}/transcript`);
}
