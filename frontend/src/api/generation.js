import { api } from "./client";

export async function generateCampaignPack(mediaId) {
  return await api.post(`/generation/campaign-pack/${mediaId}`);
}

export async function getCampaignPack(mediaId) {
  return await api.get(`/generation/campaign-pack/${mediaId}`);
}

export async function updateGeneratedContent(contentId, data) {
  return await api.put(`/generation/content/${contentId}`, data);
}
