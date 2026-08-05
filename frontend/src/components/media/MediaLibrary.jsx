import React, { useState, useEffect } from "react";
import "./MediaLibrary.css";
import {
  FileVideo,
  FileAudio,
  Search,
  Trash2,
  Eye,
  Plus,
  Activity,
  CheckCircle2,
  UploadCloud,
} from "lucide-react";
import { getMediaDetails, getMediaWaveform, deleteMediaFile } from "../../api/media";
import { getProjects } from "../../api/projects";
import { api } from "../../api/client";

function MediaLibrary({ onOpenUpload, onShowToast }) {
  const [search, setSearch] = useState("");
  const [mediaItems, setMediaItems] = useState([]);
  const [waveformData, setWaveformData] = useState({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);

    // Fetch user's projects, then list media from the first project
    getProjects()
      .then(async (projects) => {
        if (!Array.isArray(projects) || projects.length === 0) {
          setMediaItems([]);
          return;
        }
        const projectId = projects[0].id;

        // Use the new backend list-media endpoint
        const mediaList = await api.get(`/projects/${projectId}/media`);
        if (Array.isArray(mediaList)) {
          setMediaItems(mediaList);

          // Pre-fetch waveform peaks for each media item
          for (const item of mediaList) {
            try {
              const waveData = await getMediaWaveform(item.id);
              if (waveData && Array.isArray(waveData.peaks)) {
                // Sample to 28 peaks for visualization
                const sampledPeaks = samplePeaks(waveData.peaks, 28);
                setWaveformData((prev) => ({ ...prev, [item.id]: sampledPeaks }));
              }
            } catch {
              // No waveform available — use placeholder
              setWaveformData((prev) => ({
                ...prev,
                [item.id]: Array.from({ length: 28 }, () => 0.1),
              }));
            }
          }
        }
      })
      .catch(() => {
        setMediaItems([]);
      })
      .finally(() => setLoading(false));
  }, []);

  // Sample a peak array down to `count` evenly-spaced values
  const samplePeaks = (peaks, count) => {
    if (peaks.length <= count) return peaks;
    const step = peaks.length / count;
    return Array.from({ length: count }, (_, i) => {
      const idx = Math.min(Math.floor(i * step), peaks.length - 1);
      return peaks[idx];
    });
  };

  const handleDelete = async (id, filename) => {
    try {
      await deleteMediaFile(id);
      setMediaItems(mediaItems.filter((item) => item.id !== id));
      if (onShowToast) onShowToast(`Deleted media recording "${filename}"`);
    } catch (err) {
      if (onShowToast) onShowToast(err.message || `Failed to delete "${filename}"`);
    }
  };

  const filtered = mediaItems.filter((item) =>
    (item.filename || "").toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="mediaLibrary">
      <div className="mediaLibrary__header">
        <div>
          <h2>Media Library & Spoken Assets</h2>
          <p>Inspect raw webinars, podcast audio, and 100-point peak waveforms</p>
        </div>

        <button className="mediaLibrary__btnPrimary" onClick={onOpenUpload}>
          <Plus size={16} /> Import Media File
        </button>
      </div>

      <div className="mediaLibrary__toolbar">
        <div className="mediaLibrary__search">
          <Search size={16} />
          <input
            type="text"
            placeholder="Search media files by filename..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
      </div>

      {filtered.length === 0 ? (
        <div className="mediaLibrary__emptyCard">
          <div className="mediaLibrary__emptyIconBox">
            <UploadCloud size={40} color="#4F46E5" />
          </div>
          <h3>No Spoken Media Ingested Yet</h3>
          <p>
            Upload your first podcast recording, webinar, or executive keynote to extract authentic Voice DNA campaign packs.
          </p>
          <button className="mediaLibrary__btnPrimary" onClick={onOpenUpload}>
            <Plus size={16} /> Import Your First Recording
          </button>
        </div>
      ) : (
        <div className="mediaLibrary__grid">
          {filtered.map((item) => (
            <div key={item.id} className="mediaLibrary__card">
              <div className="mediaLibrary__cardTop">
                <div className="mediaLibrary__iconBox">
                  {(item.filename || "").endsWith(".mp4") ? (
                    <FileVideo size={24} color="#4F46E5" />
                  ) : (
                    <FileAudio size={24} color="#8B5CF6" />
                  )}
                </div>
                <span className="mediaLibrary__badge">
                  <CheckCircle2 size={12} /> {item.status || "Ready"}
                </span>
              </div>

              <h3 className="mediaLibrary__filename">{item.filename}</h3>

              <div className="mediaLibrary__meta">
                <span>{((item.file_size || 0) / (1024 * 1024)).toFixed(1)} MB</span>
                <span>•</span>
                <span>{Math.floor((item.duration || 0) / 60)} mins</span>
                <span>•</span>
                <span>{item.codec || "unknown"}</span>
              </div>

              {/* Waveform Preview Peak Visualizer */}
              <div className="mediaLibrary__waveform">
                <Activity size={14} color="#6366F1" />
                <div className="mediaLibrary__peaks">
                  {(waveformData[item.id] || Array.from({ length: 28 }, () => 0.1)).map((peak, idx) => (
                    <div
                      key={idx}
                      className="peakBar"
                      style={{
                        height: `${Math.max(15, (peak || 0.1) * 100)}%`,
                      }}
                    />
                  ))}
                </div>
              </div>

              <div className="mediaLibrary__cardActions">
                <button
                  className="mediaLibrary__actionBtn"
                  onClick={() => {
                    if (onShowToast) onShowToast(`Waveform peaks: ${item.id}`);
                  }}
                  title="View waveform"
                >
                  <Eye size={15} /> Waveform
                </button>
                <button
                  className="mediaLibrary__deleteBtn"
                  onClick={() => handleDelete(item.id, item.filename)}
                  title="Delete media"
                >
                  <Trash2 size={15} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default MediaLibrary;
