import { api } from "./client";

/**
 * Content Generation API
 * All generation goes through the backend — no mock data, no fake responses.
 */

// Legacy campaign pack endpoints (kept for backward compat)
export async function generateCampaignPack(mediaId) {
  return await api.post(`/generation/campaign-pack/${mediaId}`);
}

export async function getCampaignPack(mediaId) {
  return await api.get(`/generation/campaign-pack/${mediaId}`);
}

export async function updateGeneratedContent(contentId, data) {
  return await api.put(`/generation/content/${contentId}`, data);
}

// New per-type generation endpoints

export async function getContentTypes() {
  return await api.get("/generation/content-types");
}

export async function generateContent(mediaId, options) {
  const { content_type, tone, audience, length, extra_instructions } = options;
  return await api.post(`/generation/media/${mediaId}/generate`, {
    content_type,
    tone,
    audience,
    length,
    extra_instructions,
  });
}

export async function getMediaContent(mediaId) {
  return await api.get(`/generation/media/${mediaId}/content`);
}

export async function deleteGeneratedContent(contentId) {
  return await api.delete(`/generation/content/${contentId}`);
}
