import { useState, useEffect, useCallback, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { getProject } from "../../api/projects";
import { getProjectMedia, uploadMediaFile, deleteMediaFile } from "../../api/media";
import { Upload, Trash2, Video, FileAudio, PlayCircle, Loader2, ArrowLeft } from "lucide-react";
import "./ProjectDetail.css";

const VIDEO_EXTENSIONS = /\.(mp4|mov|avi|mkv|webm|m4v|mpeg|mpg|wmv|flv|3gp|ts|mts)$/i;

const isVideo = (filename) => VIDEO_EXTENSIONS.test(filename || "");

const statusTone = (status) => {
  const value = String(status || "").toLowerCase();
  if (value.includes("error") || value.includes("fail")) return "error";
  if (
    value === "processed" ||
    value.includes("done") ||
    value.includes("ready") ||
    value.includes("complete") ||
    value.includes("transcribed")
  ) {
    return "success";
  }
  if (value.includes("process") || value.includes("pending")) return "processing";
  return "default";
};

const formatFileSize = (bytes) => {
  if (bytes === null || bytes === undefined) return "—";
  const size = Number(bytes);
  if (!Number.isFinite(size) || size < 0) return "—";
  if (size < 1024) return `${size} B`;
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`;
  if (size < 1024 * 1024 * 1024) return `${(size / (1024 * 1024)).toFixed(2)} MB`;
  return `${(size / (1024 * 1024 * 1024)).toFixed(2)} GB`;
};

const formatDuration = (seconds) => {
  if (seconds === null || seconds === undefined) return "—";
  const total = Math.round(Number(seconds));
  if (!Number.isFinite(total) || total < 0) return "—";
  const hours = Math.floor(total / 3600);
  const minutes = Math.floor((total % 3600) / 60);
  const secs = total % 60;
  const mm = String(minutes).padStart(2, "0");
  const ss = String(secs).padStart(2, "0");
  return hours > 0 ? `${hours}:${mm}:${ss}` : `${minutes}:${ss}`;
};

export default function ProjectDetail() {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const fileInputRef = useRef(null);

  const [project, setProject] = useState(null);
  const [mediaList, setMediaList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");
  const [actionError, setActionError] = useState("");

  const fetchProjectData = useCallback(async () => {
    const [projData, mediaData] = await Promise.all([
      getProject(projectId),
      getProjectMedia(projectId),
    ]);
    return { project: projData, media: mediaData };
  }, [projectId]);

  const loadData = useCallback(() => {
    fetchProjectData()
      .then(({ project, media }) => {
        setError("");
        setProject(project);
        setMediaList(Array.isArray(media) ? media : []);
      })
      .catch(() => setError("Failed to load project details."))
      .finally(() => setLoading(false));
  }, [fetchProjectData]);

  const handleRetry = () => {
    setError("");
    setLoading(true);
    loadData();
  };

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setActionError("");
    try {
      await uploadMediaFile(projectId, file);
      await loadData();
    } catch (err) {
      setActionError("Upload failed: " + (err.message || "Unknown error"));
    } finally {
      setUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  };

  const handleDeleteMedia = async (mediaId) => {
    if (!window.confirm("Delete this media?")) return;

    setActionError("");
    try {
      await deleteMediaFile(mediaId);
      setMediaList((prev) => prev.filter((m) => m.id !== mediaId));
    } catch {
      setActionError("Failed to delete media. Please try again.");
    }
  };

  if (loading) {
    return (
      <div className="project-detail__state">
        <Loader2 size={32} className="project-detail__spinner" />
        <p>Loading project...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="project-detail__state">
        <p className="project-detail__state-error">{error}</p>
        <button className="project-detail__retry-btn" onClick={handleRetry}>
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="project-detail">
      <header className="project-detail__header">
        <div className="project-detail__header-left">
          <button className="project-detail__back" onClick={() => navigate("/dashboard")}>
            <ArrowLeft size={16} /> Back to Dashboard
          </button>
          <h1 className="project-detail__title">{project?.name || "Project Workspace"}</h1>
        </div>

        <div className="project-detail__header-right">
          <input
            type="file"
            ref={fileInputRef}
            className="project-detail__file-input"
            onChange={handleFileUpload}
            accept="video/*,audio/*"
          />
          <button
            className="project-detail__upload-btn"
            disabled={uploading}
            onClick={() => fileInputRef.current?.click()}
          >
            {uploading ? <Loader2 size={16} className="project-detail__spinner" /> : <Upload size={16} />}
            {uploading ? "Uploading..." : "Upload Media"}
          </button>
        </div>
      </header>

      {actionError && <div className="project-detail__notice project-detail__notice--error">{actionError}</div>}

      <div className="project-detail__media-grid">
        {mediaList.length === 0 ? (
          <div className="project-detail__empty">
            <div className="project-detail__empty-icon">
              <Video size={44} />
            </div>
            <h3>No media uploaded yet</h3>
            <p>Upload a video or audio file to start generating content.</p>
          </div>
        ) : (
          mediaList.map((media) => (
            <div key={media.id} className="project-detail__card">
              <div className="project-detail__card-header">
                <div className="project-detail__card-title">
                  <span className="project-detail__file-icon">
                    {isVideo(media.filename) ? <Video size={20} /> : <FileAudio size={20} />}
                  </span>
                  <span className="project-detail__filename" title={media.filename}>
                    {media.filename}
                  </span>
                </div>
                <span className={`project-detail__status project-detail__status--${statusTone(media.status)}`}>
                  {media.status}
                </span>
              </div>

              <div className="project-detail__card-body">
                <div className="project-detail__meta">
                  <span className="project-detail__meta-item">{formatFileSize(media.file_size)}</span>
                  <span className="project-detail__meta-item">{formatDuration(media.duration)}</span>
                  {media.codec && <span className="project-detail__meta-item">{media.codec}</span>}
                </div>

                <div className="project-detail__card-actions">
                  <button
                    className="project-detail__open-btn"
                    onClick={() => navigate(`/projects/${projectId}/media/${media.id}`)}
                  >
                    <PlayCircle size={16} /> Open Workspace
                  </button>
                  <button
                    className="project-detail__delete-btn"
                    onClick={() => handleDeleteMedia(media.id)}
                    title="Delete Media"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
