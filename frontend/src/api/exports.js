import { config } from "../config";

export async function exportContentAsset(contentId, format = "markdown") {
  const response = await fetch(`${config.apiUrl}/export/content/${contentId}?format=${format}`, {
    credentials: "include",
  });

  if (!response.ok) {
    throw new Error(`Failed to export content: ${response.status}`);
  }

  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);

  // Extract filename from Content-Disposition header if available
  const contentDisposition = response.headers.get("Content-Disposition");
  let filename = `asset_${contentId}.${format}`;
  if (contentDisposition) {
    const filenameMatch = contentDisposition.match(/filename="?([^"]+)"?/);
    if (filenameMatch && filenameMatch.length === 2) {
      filename = filenameMatch[1];
    }
  }

  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  window.URL.revokeObjectURL(url);
}

export async function exportCampaignPack(mediaId) {
  const response = await fetch(`${config.apiUrl}/export/campaign-pack/${mediaId}`, {
    credentials: "include",
  });

  if (!response.ok) {
    throw new Error(`Failed to export campaign pack: ${response.status}`);
  }

  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);

  // Extract filename from Content-Disposition header if available
  const contentDisposition = response.headers.get("Content-Disposition");
  let filename = `campaign_${mediaId}.zip`;
  if (contentDisposition) {
    const filenameMatch = contentDisposition.match(/filename="?([^"]+)"?/);
    if (filenameMatch && filenameMatch.length === 2) {
      filename = filenameMatch[1];
    }
  }

  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  window.URL.revokeObjectURL(url);
}
