import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { getMediaDetails, getMediaWaveform } from "../../api/media";
import { getProcessingJob, startProcessing } from "../../api/processing";
import { getProjectClips, getClipStreamUrl } from "../../api/clips";
import { generateCampaignPack, getCampaignPack, updateGeneratedContent } from "../../api/generation";
import { exportContentAsset, exportCampaignPack } from "../../api/exports";
import { Loader2, ArrowLeft, PlayCircle, FileText, Film, Sparkles, AlertCircle, Download } from "lucide-react";
import "./ResourceWorkspace.css";

export default function ResourceWorkspace() {
  const { projectId, mediaId } = useParams();
  const navigate = useNavigate();

  const [activeTab, setActiveTab] = useState("overview");
  const [media, setMedia] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [job, setJob] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);

  const fetchMedia = async () => {
    try {
      const data = await getMediaDetails(mediaId);
      setMedia(data);
      try {
        const { getLatestJobForMedia } = await import("../../api/processing");
        const latestJob = await getLatestJobForMedia(mediaId);
        setJob(latestJob);
        if (latestJob.status === "PENDING" || latestJob.status === "PROCESSING") {
          setIsProcessing(true);
          pollJobStatus(latestJob.job_id);
        }
      } catch (e) {
        // No jobs or error fetching jobs
      }
    } catch (err) {
      setError("Failed to load resource.");
    }
  };

  useEffect(() => {
    fetchMedia().finally(() => setLoading(false));
  }, [mediaId]);

  const handleStartProcessing = async () => {
    try {
      setIsProcessing(true);
      const res = await startProcessing(mediaId);
      setJob(res);
      pollJobStatus(res.job_id);
    } catch (err) {
      setError("Failed to start processing: " + (err.message || err));
      setIsProcessing(false);
    }
  };

  const pollJobStatus = async (jobId) => {
    const interval = setInterval(async () => {
      try {
        const j = await getProcessingJob(jobId);
        setJob(j);
        if (j.status === "COMPLETED" || j.status === "FAILED") {
          clearInterval(interval);
          setIsProcessing(false);
          fetchMedia(); // Refresh media status
        }
      } catch (err) {
        clearInterval(interval);
        setIsProcessing(false);
      }
    }, 2000);
  };

  if (loading) return <div style={{ padding: "40px", textAlign: "center" }}><Loader2 className="lucide-spin" /> Loading resource...</div>;
  if (error) return <div style={{ padding: "40px", color: "red" }}><AlertCircle /> {error}</div>;

  return (
    <div className="resource-workspace" style={{ padding: "20px", maxWidth: "1200px", margin: "0 auto", width: "100%" }}>
      <header style={{ marginBottom: "20px", display: "flex", alignItems: "center", gap: "16px" }}>
        <button onClick={() => navigate(`/projects/${projectId}`)} style={{ background: "none", border: "none", cursor: "pointer", color: "#4F46E5" }}>
          <ArrowLeft />
        </button>
        <h1 style={{ fontSize: "24px", margin: 0 }}>{media?.filename || "Resource"}</h1>
      </header>

      <div style={{ display: "flex", gap: "10px", marginBottom: "20px", borderBottom: "1px solid #e2e8f0", paddingBottom: "10px" }}>
        <button 
          onClick={() => setActiveTab("overview")} 
          style={{ padding: "8px 16px", background: activeTab === "overview" ? "#e0e7ff" : "none", border: "none", borderRadius: "6px", cursor: "pointer", display: "flex", alignItems: "center", gap: "8px", fontWeight: activeTab === "overview" ? 600 : 400, color: activeTab === "overview" ? "#4F46E5" : "#64748b" }}
        >
          <PlayCircle size={16} /> Overview
        </button>
        <button 
          onClick={() => setActiveTab("transcript")} 
          style={{ padding: "8px 16px", background: activeTab === "transcript" ? "#e0e7ff" : "none", border: "none", borderRadius: "6px", cursor: "pointer", display: "flex", alignItems: "center", gap: "8px", fontWeight: activeTab === "transcript" ? 600 : 400, color: activeTab === "transcript" ? "#4F46E5" : "#64748b" }}
        >
          <FileText size={16} /> Transcript
        </button>
        <button 
          onClick={() => setActiveTab("clips")} 
          style={{ padding: "8px 16px", background: activeTab === "clips" ? "#e0e7ff" : "none", border: "none", borderRadius: "6px", cursor: "pointer", display: "flex", alignItems: "center", gap: "8px", fontWeight: activeTab === "clips" ? 600 : 400, color: activeTab === "clips" ? "#4F46E5" : "#64748b" }}
        >
          <Film size={16} /> Clips
        </button>
        <button 
          onClick={() => setActiveTab("content")} 
          style={{ padding: "8px 16px", background: activeTab === "content" ? "#e0e7ff" : "none", border: "none", borderRadius: "6px", cursor: "pointer", display: "flex", alignItems: "center", gap: "8px", fontWeight: activeTab === "content" ? 600 : 400, color: activeTab === "content" ? "#4F46E5" : "#64748b" }}
        >
          <Sparkles size={16} /> AI Content
        </button>
      </div>

      <section style={{ background: "white", borderRadius: "8px", padding: "20px", border: "1px solid #e2e8f0", minHeight: "500px" }}>
        {activeTab === "overview" && (
          <div>
            <h2>Resource Overview</h2>
            <div style={{ background: "#f8fafc", padding: "16px", borderRadius: "8px", marginBottom: "20px" }}>
              <p><strong>Status:</strong> {media?.status}</p>
              <p><strong>File Size:</strong> {(media?.file_size / (1024 * 1024)).toFixed(2)} MB</p>
              {media?.duration && <p><strong>Duration:</strong> {media.duration}s</p>}
            </div>

            {(media?.status === "PENDING" || media?.status === "FAILED") && !isProcessing && (
              <button 
                onClick={handleStartProcessing} 
                style={{ background: "#4F46E5", color: "white", padding: "10px 20px", border: "none", borderRadius: "8px", cursor: "pointer", fontWeight: "bold" }}
              >
                Start Processing
              </button>
            )}

            {isProcessing && (
              <div style={{ padding: "20px", background: "#f0fdf4", border: "1px solid #bbf7d0", borderRadius: "8px" }}>
                <p style={{ display: "flex", alignItems: "center", gap: "8px", color: "#166534", margin: 0 }}>
                  <Loader2 className="lucide-spin" size={20} /> Processing... {job?.status}
                </p>
              </div>
            )}
            
            {job?.status === "FAILED" && (
              <div style={{ padding: "20px", background: "#fef2f2", border: "1px solid #fecaca", borderRadius: "8px", marginTop: "10px" }}>
                <p style={{ color: "#991b1b", margin: 0 }}>Processing failed: {job.error_message}</p>
              </div>
            )}
          </div>
        )}

        {activeTab === "transcript" && (
          <div>
            <h2>Transcript</h2>
            <TranscriptView mediaId={mediaId} />
          </div>
        )}

        {activeTab === "clips" && (
          <div>
            <h2>Generated Clips</h2>
            <ClipsView projectId={projectId} mediaId={mediaId} />
          </div>
        )}

        {activeTab === "content" && (
          <div>
            <h2>AI Content</h2>
            <p>Content generation integration coming soon...</p>
          </div>
        )}
      </section>
    </div>
  );
}


function ClipVideo({ clip }) {
  const [videoUrl, setVideoUrl] = useState(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    let objectUrl = null;
    let isActive = true;

    getClipStreamUrl(clip.id)
      .then(url => {
        if (isActive) {
          objectUrl = url;
          setVideoUrl(url);
        } else {
          URL.revokeObjectURL(url);
        }
      })
      .catch(err => {
        if (isActive) setError(true);
      });

    return () => {
      isActive = false;
      if (objectUrl) {
        URL.revokeObjectURL(objectUrl);
      }
    };
  }, [clip.id]);

  if (error) return <div style={{ color: "red", padding: "20px" }}>Failed to load video stream.</div>;
  if (!videoUrl) return <div style={{ color: "white", padding: "20px", display: "flex", alignItems: "center", justifyContent: "center", height: "100%" }}><Loader2 className="lucide-spin" /> Loading...</div>;

  return (
    <video 
      controls 
      src={videoUrl} 
      style={{ width: "100%", height: "100%", objectFit: "cover" }}
    />
  );
}

function ClipsView({ projectId, mediaId }) {
  const [clips, setClips] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    getProjectClips(projectId)
      .then((data) => {
        const mediaClips = data.filter(c => String(c.media_id) === String(mediaId));
        setClips(mediaClips);
      })
      .catch(err => setError("Failed to load clips."))
      .finally(() => setLoading(false));
  }, [projectId, mediaId]);

  if (loading) return <div><Loader2 className="lucide-spin" /> Loading clips...</div>;
  if (error) return <div style={{color: "red"}}>{error}</div>;

  if (clips.length === 0) {
    return (
      <div style={{ padding: "40px", textAlign: "center", background: "#f8fafc", borderRadius: "8px", border: "2px dashed #cbd5e1" }}>
        <Film size={48} color="#94a3b8" style={{ margin: "0 auto 10px" }} />
        <h3 style={{ margin: "0 0 10px" }}>No clips available</h3>
        <p style={{ margin: 0, color: "#64748b" }}>Process this resource to generate AI clips.</p>
      </div>
    );
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
      {clips.map(clip => (
        <div key={clip.id} style={{ display: "flex", gap: "20px", background: "#f8fafc", padding: "16px", borderRadius: "8px", border: "1px solid #e2e8f0" }}>
          <div style={{ flex: "0 0 300px", background: "black", borderRadius: "6px", overflow: "hidden", aspectRatio: "16/9" }}>
            <ClipVideo clip={clip} />
          </div>
          <div>
            <h3 style={{ margin: "0 0 10px", fontSize: "18px" }}>{clip.title}</h3>
            <div style={{ display: "flex", gap: "10px", marginBottom: "10px" }}>
              <span style={{ background: "#e0e7ff", color: "#4F46E5", padding: "4px 8px", borderRadius: "4px", fontSize: "12px", fontWeight: "bold" }}>
                {clip.start_time.toFixed(1)}s - {clip.end_time.toFixed(1)}s
              </span>
            </div>
            <p style={{ margin: 0, fontSize: "14px", color: "#334155", lineHeight: "1.5" }}>{clip.reason}</p>
          </div>
        </div>
      ))}
    </div>
  );
}

import { getMediaTranscript, transcribeMedia } from "../../api/media";

function TranscriptView({ mediaId }) {
  const [transcript, setTranscript] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [error, setError] = useState("");

  const fetchTranscript = async () => {
    try {
      const data = await getMediaTranscript(mediaId);
      setTranscript(data);
    } catch (err) {
      if (err.message && err.message.includes("404")) {
        // Not generated yet
      } else {
        setError("Failed to load transcript.");
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTranscript();
  }, [mediaId]);

  const handleTranscribe = async () => {
    setIsTranscribing(true);
    setError("");
    try {
      const data = await transcribeMedia(mediaId);
      setTranscript(data);
    } catch (err) {
      setError("Transcription failed: " + (err.message || "Unknown error"));
    } finally {
      setIsTranscribing(false);
    }
  };

  if (loading) return <div><Loader2 className="lucide-spin" /> Loading transcript...</div>;

  if (error) return <div style={{ color: "red", padding: "10px", background: "#fef2f2", borderRadius: "8px", border: "1px solid #fecaca" }}>{error}</div>;

  if (!transcript) {
    return (
      <div style={{ padding: "40px", textAlign: "center", background: "#f8fafc", borderRadius: "8px", border: "2px dashed #cbd5e1" }}>
        <FileText size={48} color="#94a3b8" style={{ margin: "0 auto 10px" }} />
        <h3 style={{ margin: "0 0 10px" }}>No transcript available</h3>
        <p style={{ margin: "0 0 20px", color: "#64748b" }}>Run transcription to generate the text content.</p>
        <button 
          onClick={handleTranscribe} 
          disabled={isTranscribing}
          style={{ background: "#4F46E5", color: "white", padding: "10px 20px", border: "none", borderRadius: "8px", cursor: isTranscribing ? "not-allowed" : "pointer", fontWeight: "bold", display: "inline-flex", alignItems: "center", gap: "8px" }}
        >
          {isTranscribing ? <Loader2 size={16} className="lucide-spin" /> : <Sparkles size={16} />}
          {isTranscribing ? "Transcribing..." : "Generate Transcript"}
        </button>
      </div>
    );
  }

  return (
    <div style={{ background: "#f8fafc", padding: "20px", borderRadius: "8px", border: "1px solid #e2e8f0" }}>
      <div style={{ marginBottom: "20px", paddingBottom: "20px", borderBottom: "1px solid #cbd5e1" }}>
        <h3 style={{ margin: "0 0 10px" }}>Summary</h3>
        <p style={{ margin: 0, color: "#334155", lineHeight: "1.6" }}>{transcript.summary || "No summary available."}</p>
      </div>
      <div>
        <h3 style={{ margin: "0 0 10px" }}>Full Text</h3>
        <div style={{ display: "flex", flexDirection: "column", gap: "10px", maxHeight: "400px", overflowY: "auto", paddingRight: "10px" }}>
          {(transcript.segments || []).map(seg => (
            <div key={seg.id} style={{ padding: "10px", background: "white", borderRadius: "6px", border: "1px solid #e2e8f0" }}>
              <div style={{ fontSize: "12px", color: "#64748b", marginBottom: "4px", fontWeight: "bold" }}>
                {seg.start_time.toFixed(1)}s - {seg.end_time.toFixed(1)}s
              </div>
              <div style={{ color: "#0f172a", lineHeight: "1.5" }}>{seg.text}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}



function ContentView({ mediaId }) {
  const [pack, setPack] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState("");
  const [editingContent, setEditingContent] = useState(null);
  const [editBody, setEditBody] = useState("");

  const fetchPack = async () => {
    try {
      const data = await getCampaignPack(mediaId);
      setPack(data);
    } catch (err) {
      if (err.message && err.message.includes("404")) {
        // Not generated yet
      } else {
        setError("Failed to load content.");
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPack();
  }, [mediaId]);

  const handleGenerate = async () => {
    setIsGenerating(true);
    setError("");
    try {
      const data = await generateCampaignPack(mediaId);
      setPack(data);
    } catch (err) {
      setError("Content generation failed: " + (err.message || "Unknown error"));
    } finally {
      setIsGenerating(false);
    }
  };

  const handleSaveEdit = async () => {
    if (!editingContent) return;
    try {
      // The backend expects a string for body_json
      await updateGeneratedContent(editingContent.id, { body_json: editBody });
      fetchPack();
      setEditingContent(null);
    } catch (err) {
      alert("Failed to save edits: " + err.message);
    }
  };

  const handleExportSingle = async (contentId) => {
    try {
      await exportContentAsset(contentId, "markdown");
    } catch (err) {
      alert("Failed to export asset: " + err.message);
    }
  };

  const handleExportAll = async () => {
    try {
      await exportCampaignPack(mediaId);
    } catch (err) {
      alert("Failed to export campaign pack: " + err.message);
    }
  };

  if (loading) return <div><Loader2 className="lucide-spin" /> Loading AI content...</div>;

  if (error) return <div style={{ color: "red", padding: "10px", background: "#fef2f2", borderRadius: "8px", border: "1px solid #fecaca" }}>{error}</div>;

  if (!pack) {
    return (
      <div style={{ padding: "40px", textAlign: "center", background: "#f8fafc", borderRadius: "8px", border: "2px dashed #cbd5e1" }}>
        <Sparkles size={48} color="#94a3b8" style={{ margin: "0 auto 10px" }} />
        <h3 style={{ margin: "0 0 10px" }}>No AI Content available</h3>
        <p style={{ margin: "0 0 20px", color: "#64748b" }}>Generate a campaign pack based on your video transcript.</p>
        <button 
          onClick={handleGenerate} 
          disabled={isGenerating}
          style={{ background: "#4F46E5", color: "white", padding: "10px 20px", border: "none", borderRadius: "8px", cursor: isGenerating ? "not-allowed" : "pointer", fontWeight: "bold", display: "inline-flex", alignItems: "center", gap: "8px" }}
        >
          {isGenerating ? <Loader2 size={16} className="lucide-spin" /> : <Sparkles size={16} />}
          {isGenerating ? "Generating Content..." : "Generate Campaign Pack"}
        </button>
      </div>
    );
  }

  if (editingContent) {
    return (
      <div style={{ background: "white", padding: "20px", borderRadius: "8px", border: "1px solid #e2e8f0" }}>
        <h3 style={{ margin: "0 0 16px" }}>Editing: {editingContent.title}</h3>
        <textarea
          value={editBody}
          onChange={(e) => setEditBody(e.target.value)}
          style={{ width: "100%", height: "400px", padding: "12px", border: "1px solid #cbd5e1", borderRadius: "6px", fontFamily: "monospace", fontSize: "14px", resize: "vertical", marginBottom: "16px" }}
        />
        <div style={{ display: "flex", gap: "10px" }}>
          <button onClick={handleSaveEdit} style={{ background: "#4F46E5", color: "white", padding: "8px 16px", border: "none", borderRadius: "6px", cursor: "pointer", fontWeight: "bold" }}>Save Changes</button>
          <button onClick={() => setEditingContent(null)} style={{ background: "#f1f5f9", color: "#334155", padding: "8px 16px", border: "1px solid #cbd5e1", borderRadius: "6px", cursor: "pointer", fontWeight: "bold" }}>Cancel</button>
        </div>
      </div>
    );
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "10px" }}>
        <h3 style={{ margin: 0 }}>Campaign Pack ({pack.count} Assets)</h3>
        <button 
          onClick={handleExportAll}
          style={{ background: "#10b981", color: "white", padding: "8px 16px", border: "none", borderRadius: "6px", cursor: "pointer", fontWeight: "bold", display: "flex", alignItems: "center", gap: "6px" }}
        >
          <Download size={16} /> Export All (ZIP)
        </button>
      </div>
      {pack.assets.map(asset => {
        // Attempt to parse JSON to display a structured preview, fallback to raw string
        let displayContent = asset.body_json || "No content.";
        try {
          const parsed = JSON.parse(asset.body_json);
          // If it's a markdown payload
          if (parsed.markdown) displayContent = parsed.markdown;
          // If it's a list (like tweets)
          else if (Array.isArray(parsed)) displayContent = parsed.map(item => typeof item === "string" ? item : JSON.stringify(item, null, 2)).join("\n\n");
          // If it's an object
          else displayContent = JSON.stringify(parsed, null, 2);
        } catch(e) {}

        return (
          <div key={asset.id} style={{ background: "#f8fafc", padding: "20px", borderRadius: "8px", border: "1px solid #e2e8f0" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "16px", borderBottom: "1px solid #cbd5e1", paddingBottom: "12px" }}>
              <div>
                <h3 style={{ margin: "0 0 4px", fontSize: "18px" }}>{asset.title}</h3>
                <span style={{ background: "#e0e7ff", color: "#4F46E5", padding: "2px 8px", borderRadius: "4px", fontSize: "12px", fontWeight: "bold", display: "inline-block" }}>{asset.content_type}</span>
              </div>
              <div style={{ display: "flex", gap: "8px" }}>
                <button 
                  onClick={() => handleExportSingle(asset.id)}
                  style={{ background: "white", color: "#334155", border: "1px solid #cbd5e1", padding: "6px 12px", borderRadius: "6px", cursor: "pointer", fontSize: "13px", fontWeight: "600", display: "flex", alignItems: "center", gap: "4px" }}
                >
                  <Download size={14} /> Download
                </button>
                <button 
                  onClick={() => {
                    setEditingContent(asset);
                    setEditBody(asset.body_json || "");
                  }}
                  style={{ background: "white", border: "1px solid #cbd5e1", padding: "6px 12px", borderRadius: "6px", cursor: "pointer", fontSize: "13px", fontWeight: "600" }}
                >
                  Edit
                </button>
              </div>
            </div>
            <div style={{ color: "#334155", lineHeight: "1.6", whiteSpace: "pre-wrap", fontFamily: "monospace", fontSize: "13px", background: "white", padding: "12px", borderRadius: "6px", border: "1px solid #e2e8f0" }}>
              {displayContent}
            </div>
          </div>
        );
      })}
    </div>
  );
}