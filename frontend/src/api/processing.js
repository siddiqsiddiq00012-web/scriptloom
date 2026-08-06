import { api } from "./client";

export async function startProcessing(mediaId) {
  return await api.post("/processing/process", {
    media_id: mediaId,
  });
}

export async function getProcessingJob(jobId) {
  return await api.get(`/processing/jobs/${jobId}`);
}

export async function getLatestJobForMedia(mediaId) {
  return await api.get(`/processing/media/${mediaId}/jobs/latest`);
}