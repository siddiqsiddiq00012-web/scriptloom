import { apiRequest } from "./client";

export async function getVoiceDNA() {
  return await apiRequest("/voice-dna/me", "GET");
}

export async function updateVoiceDNA(payload) {
  return await apiRequest("/voice-dna/me", "PUT", payload);
}

export async function searchMemory(query, category = null, topK = 5) {
  return await apiRequest("/creator-memory/search", "POST", {
    query,
    category,
    top_k: topK,
  });
}
