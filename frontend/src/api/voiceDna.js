import { api } from "./client";

export async function getVoiceDNA() {
  return await api.get("/voice-dna/me");
}

export async function updateVoiceDNA(payload) {
  return await api.put("/voice-dna/me", payload);
}

export async function searchMemory(query, category = null, topK = 5) {
  return await api.post("/creator-memory/search", {
    query,
    category,
    top_k: topK,
  });
}
