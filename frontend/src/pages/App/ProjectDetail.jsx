import React, { useState, useEffect, useRef } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { getProject } from "../../api/projects";
import { getProjectMedia, uploadMediaFile, deleteMediaFile } from "../../api/media";
import { startProcessing } from "../../api/processing";
import { Upload, Trash2, Video, FileAudio, PlayCircle, Loader2 } from "lucide-react";

export default function ProjectDetail() {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const fileInputRef = useRef(null);

  const [project, setProject] = useState(null);
  const [mediaList, setMediaList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");

  const loadData = async () => {
    try {
      setLoading(true);
      const [projData, mediaData] = await Promise.all([
        getProject(projectId),
        getProjectMedia(projectId),
      ]);
      setProject(projData);
      setMediaList(mediaData);
    } catch (err) {
      setError("Failed to load project details.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [projectId]);

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setError("");
    try {
      await uploadMediaFile(projectId, file);
      await loadData();
    } catch (err) {
      setError("Upload failed: " + (err.message || "Unknown error"));
    } finally {
      setUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  };

  const handleDeleteMedia = async (mediaId) => {
    if (!window.confirm("Delete this media?")) return;
    try {
      await deleteMediaFile(mediaId);
      setMediaList(mediaList.filter(m => m.id !== mediaId));
    } catch (err) {
      setError("Failed to delete media.");
    }
  };

  if (loading) return <div style={{ padding: "20px" }}><Loader2 className="lucide-spin" /> Loading project...</div>;
  if (error) return <div style={{ padding: "20px", color: "red" }}>{error}</div>;

  return (
    <div style={{ padding: "20px", maxWidth: "1200px", margin: "0 auto", width: "100%" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "30px" }}>
        <div>
          <button onClick={() => navigate("/dashboard")} style={{ background: "none", border: "none", cursor: "pointer", color: "#4F46E5", marginBottom: "10px" }}>
            &larr; Back to Dashboard
          </button>
          <h1 style={{ fontSize: "24px", margin: 0 }}>{project?.name || project?.title || "Project Workspace"}</h1>
        </div>
        
        <div>
          <input 
            type="file" 
            ref={fileInputRef} 
            style={{ display: "none" }} 
            onChange={handleFileUpload} 
            accept="video/*,audio/*" 
          />
          <button 
            disabled={uploading}
            onClick={() => fileInputRef.current?.click()} 
            style={{ display: "flex", alignItems: "center", gap: "8px", background: "#4F46E5", color: "white", padding: "10px 16px", borderRadius: "8px", border: "none", cursor: uploading ? "not-allowed" : "pointer" }}
          >
            {uploading ? <Loader2 size={16} className="lucide-spin" /> : <Upload size={16} />}
            {uploading ? "Uploading..." : "Upload Media"}
          </button>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))", gap: "20px" }}>
        {mediaList.length === 0 ? (
          <div style={{ gridColumn: "1 / -1", padding: "40px", textAlign: "center", background: "#f8fafc", borderRadius: "8px", border: "2px dashed #cbd5e1" }}>
            <Video size={48} color="#94a3b8" style={{ margin: "0 auto 10px" }} />
            <h3 style={{ margin: "0 0 10px" }}>No media uploaded yet</h3>
            <p style={{ margin: 0, color: "#64748b" }}>Upload a video or audio file to start generating content.</p>
          </div>
        ) : (
          mediaList.map(media => (
            <div key={media.id} style={{ background: "white", border: "1px solid #e2e8f0", borderRadius: "8px", overflow: "hidden" }}>
              <div style={{ padding: "16px", borderBottom: "1px solid #e2e8f0", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "8px", overflow: "hidden" }}>
                  {media.filename?.match(/\.(mp4|mov|avi|mkv|webm)$/i) ? <Video size={20} color="#4F46E5" /> : <FileAudio size={20} color="#4F46E5" />}
                  <span style={{ fontWeight: 500, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }} title={media.filename}>
                    {media.filename}
                  </span>
                </div>
              </div>
              <div style={{ padding: "16px" }}>
                <p style={{ margin: "0 0 8px", fontSize: "14px", color: "#64748b" }}>Status: <strong style={{ color: "#1e293b" }}>{media.status}</strong></p>
                <p style={{ margin: "0 0 16px", fontSize: "14px", color: "#64748b" }}>Size: {(media.file_size / (1024 * 1024)).toFixed(2)} MB</p>
                
                <div style={{ display: "flex", gap: "10px" }}>
                  <button 
                    onClick={() => navigate(`/projects/${projectId}/media/${media.id}`)}
                    style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", gap: "6px", background: "#f1f5f9", border: "1px solid #cbd5e1", padding: "8px", borderRadius: "6px", cursor: "pointer", color: "#334155" }}
                  >
                    <PlayCircle size={16} /> Open Workspace
                  </button>
                  <button 
                    onClick={() => handleDeleteMedia(media.id)}
                    style={{ background: "#fef2f2", border: "1px solid #fecaca", color: "#ef4444", padding: "8px", borderRadius: "6px", cursor: "pointer" }}
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
