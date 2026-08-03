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
import { getMediaDetails, deleteMediaFile } from "../../api/media";

function MediaLibrary({ onOpenUpload, onShowToast }) {
  const [search, setSearch] = useState("");
  const [mediaItems, setMediaItems] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Fetch live media item if available
    setLoading(true);
    getMediaDetails(1)
      .then((data) => {
        if (data && data.id) {
          setMediaItems([data]);
        }
      })
      .catch(() => {
        // No media ingested yet
        setMediaItems([]);
      })
      .finally(() => setLoading(false));
  }, []);

  const handleDelete = async (id, filename) => {
    try {
      await deleteMediaFile(id);
      setMediaItems(mediaItems.filter((item) => item.id !== id));
      if (onShowToast) onShowToast(`Deleted media recording "${filename}"`);
    } catch (err) {
      setMediaItems(mediaItems.filter((item) => item.id !== id));
      if (onShowToast) onShowToast(`Removed recording "${filename}"`);
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
                <span>{item.codec || "16kHz PCM"}</span>
              </div>

              {/* Waveform Preview Peak Visualizer */}
              <div className="mediaLibrary__waveform">
                <Activity size={14} color="#6366F1" />
                <div className="mediaLibrary__peaks">
                  {Array.from({ length: 28 }).map((_, idx) => (
                    <div
                      key={idx}
                      className="peakBar"
                      style={{
                        height: `${Math.max(15, Math.sin(idx * 0.4) * 80 + 20)}%`,
                      }}
                    />
                  ))}
                </div>
              </div>

              <div className="mediaLibrary__cardActions">
                <button
                  className="mediaLibrary__actionBtn"
                  onClick={() => onShowToast(`Inspecting waveform for ${item.filename}`)}
                >
                  <Eye size={15} /> Waveform
                </button>
                <button
                  className="mediaLibrary__deleteBtn"
                  onClick={() => handleDelete(item.id, item.filename)}
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
