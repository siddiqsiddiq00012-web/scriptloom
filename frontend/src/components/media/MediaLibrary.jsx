import { useState, useEffect, useRef, useCallback } from "react";
import { useNavigate } from "react-router-dom";
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
import { deleteMediaFile, uploadMediaFile } from "../../api/media";
import { getProjects } from "../../api/projects";
import { api } from "../../api/client";
import { ConfirmDialog, SkeletonGrid, EmptyState } from "../ui";

function samplePeaks(peaks, count) {
  if (peaks.length <= count) return peaks;
  const step = peaks.length / count;
  return Array.from({ length: count }, (_, i) => {
    const idx = Math.min(Math.floor(i * step), peaks.length - 1);
    return peaks[idx];
  });
}

function MediaLibrary({ onShowToast }) {
  const navigate = useNavigate();
  const [search, setSearch] = useState("");
  const [mediaItems, setMediaItems] = useState([]);
  const [projectsMap, setProjectsMap] = useState({});
  const [waveformData, setWaveformData] = useState({});
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [selectedProjectId, setSelectedProjectId] = useState("");
  const [deleteTarget, setDeleteTarget] = useState(null);
  const fileInputRef = useRef(null);

  const fetchMediaData = useCallback(async () => {
    const projects = await getProjects();
    const projectsArr = Array.isArray(projects) ? projects : [];
    const pMap = {};
    projectsArr.forEach((p) => { pMap[p.id] = p.name; });

    const allMedia = [];
    await Promise.all(
      projectsArr.map(async (p) => {
        try {
          const list = await api.get(`/projects/${p.id}/media`);
          if (Array.isArray(list)) {
            list.forEach((m) => allMedia.push({ ...m, _projectName: p.name, _projectId: p.id }));
          }
        } catch { /* skip */ }
      })
    );

    const waves = {};
    await Promise.all(
      allMedia.map(async (m) => {
        try {
          const waveData = await api.get(`/projects/media/${m.id}/waveform`);
          if (waveData?.peaks?.length > 0) waves[m.id] = samplePeaks(waveData.peaks, 28);
        } catch { waves[m.id] = null; }
      })
    );

    return { projectsMap: pMap, mediaItems: allMedia, waveformData: waves };
  }, []);

  const loadData = useCallback(() => {
    return fetchMediaData()
      .then(({ projectsMap: pMap, mediaItems: items, waveformData: waves }) => {
        setProjectsMap(pMap);
        setMediaItems(items);
        setWaveformData(waves);
        const ids = Object.keys(pMap);
        if (ids.length > 0) {
          setSelectedProjectId((prev) => (prev && ids.includes(prev) ? prev : ids[0]));
        }
      })
      .catch(() => setMediaItems([]))
      .finally(() => setLoading(false));
  }, [fetchMediaData]);

  useEffect(() => { loadData(); }, [loadData]);

  const handleUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const targetId = selectedProjectId;
    if (!targetId) {
      if (onShowToast) onShowToast("Please create a project first before uploading media.");
      return;
    }
    setUploading(true);
    try {
      await uploadMediaFile(Number(targetId), file);
      if (onShowToast) onShowToast(`Uploaded "${file.name}" successfully.`);
      await loadData();
    } catch (err) {
      if (onShowToast) onShowToast(err.message || "Upload failed.");
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  const handleDelete = async () => {
    if (!deleteTarget) return;
    try {
      await deleteMediaFile(deleteTarget.id);
      setMediaItems((prev) => prev.filter((item) => item.id !== deleteTarget.id));
      if (onShowToast) onShowToast(`Deleted "${deleteTarget.filename}".`);
    } catch (err) {
      if (onShowToast) onShowToast(err.message || "Failed to delete media.");
    } finally {
      setDeleteTarget(null);
    }
  };

  const filtered = mediaItems.filter((item) =>
    (item.filename || "").toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="animate-fadeIn">
      <div className="media__header">
        <div>
          <h2 className="media__title">Media Library</h2>
          <p className="media__subtitle">All media across your projects with waveform previews.</p>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          {Object.keys(projectsMap).length > 1 && (
            <select className="input" style={{ width: "auto", padding: "8px 12px", fontSize: "13px" }} value={selectedProjectId} onChange={(e) => setSelectedProjectId(e.target.value)} aria-label="Target project">
              {Object.entries(projectsMap).map(([id, name]) => (
                <option key={id} value={id}>{name}</option>
              ))}
            </select>
          )}
          <button className="btn btn-primary" onClick={() => fileInputRef.current?.click()} disabled={uploading}>
            <input ref={fileInputRef} type="file" accept="audio/*,video/*,.mp4,.mov,.mp3,.wav,.m4a" onChange={handleUpload} style={{ display: "none" }} />
            {uploading ? <><UploadCloud size={16} /> Uploading...</> : <><Plus size={16} /> Upload</>}
          </button>
        </div>
      </div>

      <div className="media__toolbar">
        <div className="media__search">
          <Search size={16} />
          <input type="text" placeholder="Search by filename..." value={search} onChange={(e) => setSearch(e.target.value)} />
        </div>
      </div>

      {loading ? (
        <SkeletonGrid count={3} />
      ) : filtered.length === 0 && mediaItems.length === 0 ? (
        <EmptyState
          icon={UploadCloud}
          title="No Media Yet"
          description="Upload a video or audio file to start generating clips, transcripts, and repurposed content."
          action={<button className="btn btn-primary" onClick={() => fileInputRef.current?.click()}><Plus size={16} /> Upload First Media</button>}
        />
      ) : filtered.length === 0 ? (
        <EmptyState icon={Search} title="No Matching Media" description={`No media matches "${search}".`} />
      ) : (
        <div className="media__grid">
          {filtered.map((item, i) => (
            <div key={item.id} className={`media__card card animate-fadeInUp stagger-${Math.min(i + 1, 6)}`}>
              <div className="media__cardTop">
                <div className="media__iconBox">
                  {/\.(mp4|mov|avi|mkv|webm)$/i.test(item.filename) ? <FileVideo size={22} color="var(--primary)" /> : <FileAudio size={22} color="var(--accent-purple)" />}
                </div>
                <span className={`badge ${item.status === "ready" || item.status === "processed" ? "badge-success" : item.status === "error" ? "badge-error" : "badge-neutral"}`}>
                  <CheckCircle2 size={11} /> {item.status || "Ready"}
                </span>
              </div>

              <h3 className="media__filename">{item.filename}</h3>
              <div className="media__meta">
                <span>{((item.file_size || 0) / (1024 * 1024)).toFixed(1)} MB</span>
                {item.duration && <><span>·</span><span>{Math.floor(item.duration / 60)} min</span></>}
                {item._projectName && <><span>·</span><span>{item._projectName}</span></>}
              </div>

              <div className="media__waveform">
                <Activity size={14} color="var(--primary)" />
                <div className="media__peaks">
                  {waveformData[item.id] ? (
                    waveformData[item.id].map((peak, idx) => (
                      <div key={idx} className="media__peakBar" style={{ height: `${Math.max(12, (peak || 0.1) * 100)}%` }} />
                    ))
                  ) : (
                    <span className="media__waveformFallback">No waveform</span>
                  )}
                </div>
              </div>

              <div className="media__actions">
                <button className="btn btn-secondary btn-sm" onClick={() => navigate(`/projects/${item._projectId}/media/${item.id}`)}>
                  <Eye size={14} /> Open
                </button>
                <button className="btn btn-danger btn-sm" onClick={() => setDeleteTarget(item)} aria-label="Delete media">
                  <Trash2 size={14} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      <ConfirmDialog
        isOpen={!!deleteTarget}
        onClose={() => setDeleteTarget(null)}
        onConfirm={handleDelete}
        title="Delete Media"
        message={`Delete "${deleteTarget?.filename}"? This action cannot be undone.`}
        confirmLabel="Delete"
        danger
      />
    </div>
  );
}

export default MediaLibrary;
