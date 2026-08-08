import { useCallback, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import {
  AlertCircle,
  ArrowLeft,
  Check,
  CheckCircle2,
  Clock,
  Download,
  FileText,
  Film,
  Loader2,
  Pencil,
  PlayCircle,
  Sparkles,
  X,
} from "lucide-react";
import { api } from "../../api/client";
import { config } from "../../config";
import { getMediaDetails, getMediaTranscript, transcribeMedia } from "../../api/media";
import { getProcessingJob, getLatestJobForMedia, startProcessing } from "../../api/processing";
import { getProjectClips, getClipStreamUrl } from "../../api/clips";
import { generateCampaignPack, getCampaignPack, updateGeneratedContent } from "../../api/generation";
import { exportContentAsset, exportCampaignPack } from "../../api/exports";
import { progressStream } from "../../services/progressStream";
import "./ResourceWorkspace.css";

const VIDEO_EXT_RE = /\.(mp4|mov|m4v|avi|mkv|webm|ogv|wmv|flv)$/i;

function formatFileSize(bytes) {
  if (bytes === null || bytes === undefined) return "—";
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function formatDuration(seconds) {
  if (seconds === null || seconds === undefined) return "—";
  const total = Math.max(0, Math.floor(Number(seconds)));
  const h = Math.floor(total / 3600);
  const m = Math.floor((total % 3600) / 60);
  const s = total % 60;
  const pad = (n) => String(n).padStart(2, "0");
  return h > 0 ? `${h}:${pad(m)}:${pad(s)}` : `${m}:${pad(s)}`;
}

function parseBodyJson(bodyJson) {
  if (bodyJson === null || bodyJson === undefined) return "No content.";
  if (typeof bodyJson !== "string") {
    if (bodyJson.markdown) return bodyJson.markdown;
    if (Array.isArray(bodyJson)) {
      return bodyJson
        .map((item) => (typeof item === "string" ? item : JSON.stringify(item, null, 2)))
        .join("\n\n");
    }
    return JSON.stringify(bodyJson, null, 2);
  }
  try {
    const parsed = JSON.parse(bodyJson);
    if (typeof parsed === "string") return parsed;
    if (parsed.markdown) return parsed.markdown;
    if (Array.isArray(parsed)) {
      return parsed
        .map((item) => (typeof item === "string" ? item : JSON.stringify(item, null, 2)))
        .join("\n\n");
    }
    return JSON.stringify(parsed, null, 2);
  } catch {
    return bodyJson;
  }
}

export default function ResourceWorkspace() {
  const { projectId, mediaId } = useParams();
  const navigate = useNavigate();

  const [activeTab, setActiveTab] = useState("overview");
  const [media, setMedia] = useState(null);
  const [job, setJob] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [isStarting, setIsStarting] = useState(false);
  const [progressInfo, setProgressInfo] = useState(null);
  const [clipsVersion, setClipsVersion] = useState(0);

  const jobStatus = job?.status;
  const jobId = job?.job_id;
  const hasActiveJob = jobStatus === "pending" || jobStatus === "processing";

  const fetchMedia = useCallback(async () => {
    const data = await getMediaDetails(mediaId);
    setMedia(data);
  }, [mediaId]);

  useEffect(() => {
    let active = true;
    const load = async () => {
      try {
        const [mediaData, jobData] = await Promise.all([
          getMediaDetails(mediaId),
          getLatestJobForMedia(mediaId).catch(() => null),
        ]);
        if (!active) return;
        setMedia(mediaData);
        setJob(jobData);
        setError("");
        setLoading(false);
      } catch {
        if (!active) return;
        setError("Failed to load resource.");
        setLoading(false);
      }
    };
    load();
    return () => {
      active = false;
    };
  }, [mediaId]);

  // Poll job status while a processing job is active.
  useEffect(() => {
    if (jobStatus !== "pending" && jobStatus !== "processing") return undefined;
    const interval = setInterval(async () => {
      try {
        const j = await getProcessingJob(jobId);
        setJob(j);
        if (j.status === "completed" || j.status === "failed") {
          progressStream.disconnect();
          fetchMedia().catch(() => {});
          setClipsVersion((v) => v + 1);
          setActiveTab("clips");
        }
      } catch {
        // Transient polling failure; keep waiting for the next tick.
      }
    }, 3000);
    return () => clearInterval(interval);
  }, [jobStatus, jobId, fetchMedia]);

  // Subscribe to the live progress stream while a job is active.
  useEffect(() => {
    if (jobStatus !== "pending" && jobStatus !== "processing") return undefined;
    const listener = (msg) => {
      if (msg && msg.type === "event" && msg.data && msg.data.event === "progress" && msg.data.payload) {
        setProgressInfo(msg.data.payload);
      }
    };
    progressStream.subscribe(listener);
    progressStream.connect(mediaId);
    return () => {
      progressStream.unsubscribe(listener);
    };
  }, [jobStatus, mediaId]);

  // Clean up the SSE connection on unmount.
  useEffect(() => {
    return () => {
      progressStream.disconnect();
    };
  }, []);

  const handleStartProcessing = useCallback(async () => {
    setIsStarting(true);
    setError("");
    setProgressInfo(null);
    try {
      const res = await startProcessing(mediaId);
      setJob(res);
      setClipsVersion((v) => v + 1);
    } catch (err) {
      setError("Failed to start processing: " + (err.message || "Unknown error"));
    } finally {
      setIsStarting(false);
    }
  }, [mediaId]);

  const tabs = [
    { id: "overview", label: "Overview", icon: PlayCircle },
    { id: "transcript", label: "Transcript", icon: FileText },
    { id: "clips", label: "Clips", icon: Film },
    { id: "content", label: "AI Content", icon: Sparkles },
  ];

  const canProcess = !hasActiveJob && media && (media.status === "processed" || media.status === "uploaded" || media.status === "error");

  return (
    <div className="resourceWorkspace">
      <header className="resourceWorkspace__header">
        <button className="resourceWorkspace__back" onClick={() => navigate(`/projects/${projectId}`)}>
          <ArrowLeft size={16} /> Back
        </button>
        <div className="resourceWorkspace__titleWrap">
          <h1 className="resourceWorkspace__title">{media?.filename || "Resource Workspace"}</h1>
          {media?.status && (
            <span className={`statusBadge statusBadge--${String(media.status).toLowerCase()}`}>{media.status}</span>
          )}
        </div>
      </header>

      {loading ? (
        <div className="stateBox">
          <Loader2 className="lucide-spin" size={18} /> Loading resource…
        </div>
      ) : error ? (
        <div className="stateBox stateBox--error">
          <AlertCircle size={18} /> {error}
        </div>
      ) : (
        <>
          <nav className="resourceWorkspace__tabs">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  className={`resourceWorkspace__tab${activeTab === tab.id ? " resourceWorkspace__tab--active" : ""}`}
                  onClick={() => setActiveTab(tab.id)}
                >
                  <Icon size={16} /> {tab.label}
                </button>
              );
            })}
          </nav>

          <section className="resourceWorkspace__content">
            {activeTab === "overview" && (
              <div className="overview">
                <div className="overview__grid">
                  <div className="card">
                    <div className="card__header">
                      <h3 className="card__title">Media Info</h3>
                    </div>
                    <dl className="mediaInfo">
                      <div className="mediaInfo__row">
                        <dt>Status</dt>
                        <dd>
                          <span
                            className={`statusBadge statusBadge--${String(media?.status || "unknown").toLowerCase()}`}
                          >
                            {media?.status || "—"}
                          </span>
                        </dd>
                      </div>
                      <div className="mediaInfo__row">
                        <dt>File Size</dt>
                        <dd>{formatFileSize(media?.file_size)}</dd>
                      </div>
                      <div className="mediaInfo__row">
                        <dt>Duration</dt>
                        <dd>{formatDuration(media?.duration)}</dd>
                      </div>
                      <div className="mediaInfo__row">
                        <dt>Codec</dt>
                        <dd>{media?.codec || "—"}</dd>
                      </div>
                      <div className="mediaInfo__row">
                        <dt>Resolution</dt>
                        <dd>{media?.width && media?.height ? `${media.width} × ${media.height}` : "—"}</dd>
                      </div>
                      <div className="mediaInfo__row">
                        <dt>Bitrate</dt>
                        <dd>{media?.bitrate ? `${Math.round(media.bitrate / 1000)} kbps` : "—"}</dd>
                      </div>
                      <div className="mediaInfo__row">
                        <dt>Frame Rate</dt>
                        <dd>{media?.fps ? `${media.fps} fps` : "—"}</dd>
                      </div>
                    </dl>
                  </div>

                  <div className="card">
                    <div className="card__header">
                      <h3 className="card__title">Preview</h3>
                    </div>
                    <MediaPreview media={media} />
                  </div>
                </div>

                <div className="card">
                  <div className="card__header">
                    <h3 className="card__title">Processing</h3>
                  </div>
                  <div className="processing">
                    {hasActiveJob && (
                      <div className="processing__active">
                        <div className="processing__statusRow">
                          <Loader2 className="lucide-spin" size={18} />
                          <span>Processing resource…</span>
                          {jobStatus && <span className="statusBadge statusBadge--processing">{jobStatus}</span>}
                        </div>
                        {typeof progressInfo?.progress === "number" && (
                          <div className="processing__progress">
                            <progress
                              className="progressBar"
                              max={100}
                              value={Math.min(100, Math.max(0, progressInfo.progress))}
                            >
                              {Math.round(progressInfo.progress)}%
                            </progress>
                            <span className="processing__percent">{Math.round(progressInfo.progress)}%</span>
                          </div>
                        )}
                        {progressInfo?.stage && <p className="processing__stage">Stage: {progressInfo.stage}</p>}
                        {progressInfo?.message && <p className="processing__message">{progressInfo.message}</p>}
                      </div>
                    )}

                    {jobStatus === "failed" && (
                      <div className="processing__failed">
                        <AlertCircle size={18} />
                        <p className="processing__error">
                          Processing failed: {job?.error_message || "Unknown error"}
                        </p>
                      </div>
                    )}

                    {jobStatus === "completed" && (
                      <div className="processing__done">
                        <CheckCircle2 size={18} />
                        <span>Processing completed successfully.</span>
                        <button className="btn btn--primary btn--sm" onClick={() => setActiveTab("clips")}>
                          <Film size={14} /> View Clips
                        </button>
                      </div>
                    )}

                    {canProcess && (
                      <div className="processing__actions">
                        <button className="btn btn--primary" onClick={handleStartProcessing} disabled={isStarting}>
                          {isStarting ? (
                            <>
                              <Loader2 className="lucide-spin" size={16} /> Starting…
                            </>
                          ) : (
                            <>
                              <PlayCircle size={16} /> Start Processing
                            </>
                          )}
                        </button>
                        <p className="processing__hint">
                          Run the processing pipeline to prepare this resource for transcription, clip selection, and
                          content generation.
                        </p>
                      </div>
                    )}

                    {!hasActiveJob &&
                      jobStatus !== "failed" &&
                      jobStatus !== "completed" &&
                      !canProcess && (
                        <p className="processing__idle">No active processing job for this resource.</p>
                      )}
                  </div>
                </div>
              </div>
            )}

            {activeTab === "transcript" && <TranscriptView mediaId={mediaId} />}
            {activeTab === "clips" && <ClipsView key={clipsVersion} projectId={projectId} mediaId={mediaId} />}
            {activeTab === "content" && <ContentView mediaId={mediaId} />}
          </section>
        </>
      )}
    </div>
  );
}

function MediaPreview({ media }) {
  const [url, setUrl] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const isVideo = VIDEO_EXT_RE.test(media?.filename || "");

  useEffect(() => {
    let active = true;
    let objectUrl = null;

    const token = localStorage.getItem("token");
    fetch(`${config.apiUrl}/projects/media/${media.id}/stream`, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    })
      .then((res) => {
        if (!res.ok) throw new Error("Stream unavailable");
        return res.blob();
      })
      .then((blob) => {
        if (!active) return;
        objectUrl = URL.createObjectURL(blob);
        setUrl(objectUrl);
        setLoading(false);
        setError("");
      })
      .catch(() => {
        if (!active) return;
        setError("Unable to load media preview.");
        setLoading(false);
      });

    return () => {
      active = false;
      if (objectUrl) URL.revokeObjectURL(objectUrl);
    };
  }, [media.id, media.filename]);

  if (loading) {
    return (
      <div className="mediaPreview mediaPreview--video">
        <div className="mediaPreview__loading">
          <Loader2 className="lucide-spin" size={18} /> Loading preview…
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="mediaPreview mediaPreview--video">
        <div className="mediaPreview__error">{error}</div>
      </div>
    );
  }

  if (!url) return null;

  return isVideo ? (
    <div className="mediaPreview mediaPreview--video">
      <video className="mediaPreview__video" src={url} controls playsInline />
    </div>
  ) : (
    <div className="mediaPreview mediaPreview--audio">
      <audio className="mediaPreview__audio" src={url} controls />
    </div>
  );
}

function TranscriptView({ mediaId }) {
  const [transcript, setTranscript] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [editingSegmentId, setEditingSegmentId] = useState(null);
  const [segmentDraft, setSegmentDraft] = useState("");
  const [savingSegmentId, setSavingSegmentId] = useState(null);

  const loadTranscript = useCallback(async () => {
    try {
      const data = await getMediaTranscript(mediaId);
      setTranscript(data);
      setError("");
    } catch (err) {
      if (err.status === 404) {
        setTranscript(null);
        setError("");
      } else {
        setError("Failed to load transcript.");
      }
    }
  }, [mediaId]);

  useEffect(() => {
    let active = true;
    Promise.resolve()
      .then(() => loadTranscript())
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [loadTranscript]);

  const handleTranscribe = async () => {
    setIsTranscribing(true);
    setError("");
    try {
      await transcribeMedia(mediaId);
      await loadTranscript();
    } catch (err) {
      setError("Transcription failed: " + (err.message || "Unknown error"));
    } finally {
      setIsTranscribing(false);
    }
  };

  const startEditingSegment = (seg) => {
    setEditingSegmentId(seg.id);
    setSegmentDraft(seg.text || "");
  };

  const cancelEditingSegment = () => {
    setEditingSegmentId(null);
    setSegmentDraft("");
  };

  const saveSegment = async (seg) => {
    setSavingSegmentId(seg.id);
    setError("");
    try {
      await api.put(`/transcripts/segments/${seg.id}`, { text: segmentDraft });
      setTranscript((prev) => {
        if (!prev) return prev;
        return {
          ...prev,
          segments: (prev.segments || []).map((s) => (s.id === seg.id ? { ...s, text: segmentDraft } : s)),
        };
      });
      setEditingSegmentId(null);
      setSegmentDraft("");
    } catch (err) {
      setError("Failed to save segment: " + (err.message || "Unknown error"));
    } finally {
      setSavingSegmentId(null);
    }
  };

  if (loading) {
    return (
      <div className="stateBox">
        <Loader2 className="lucide-spin" size={18} /> Loading transcript…
      </div>
    );
  }

  if (error && !transcript) {
    return (
      <div className="stateBox stateBox--error">
        <AlertCircle size={18} /> {error}
      </div>
    );
  }

  if (!transcript) {
    return (
      <div className="emptyState">
        <div className="emptyState__icon">
          <FileText size={36} color="#4F46E5" />
        </div>
        <h3 className="emptyState__title">No transcript yet</h3>
        <p className="emptyState__text">
          Generate a transcript to unlock the full text, a summary, and editable segments.
        </p>
        <button className="btn btn--primary" onClick={handleTranscribe} disabled={isTranscribing}>
          {isTranscribing ? (
            <>
              <Loader2 className="lucide-spin" size={16} /> Transcribing…
            </>
          ) : (
            <>
              <Sparkles size={16} /> Generate Transcript
            </>
          )}
        </button>
      </div>
    );
  }

  const segments = Array.isArray(transcript.segments) ? transcript.segments : [];

  return (
    <div className="transcript">
      {error && (
        <div className="inlineError">
          <AlertCircle size={15} /> {error}
        </div>
      )}

      {(transcript.summary || transcript.language) && (
        <div className="transcript__summary">
          {transcript.language && <p className="transcript__language">Language: {transcript.language}</p>}
          <h3 className="transcript__summaryTitle">Summary</h3>
          <p className="transcript__summaryText">{transcript.summary || "No summary available."}</p>
        </div>
      )}

      {segments.length === 0 ? (
        <div className="stateBox">No transcript segments available.</div>
      ) : (
        <div className="transcript__list">
          {segments.map((seg) => (
            <div key={seg.id} className={`segment${editingSegmentId === seg.id ? " segment--editing" : ""}`}>
              <div className="segment__header">
                <div className="segment__meta">
                  <span className="segment__time">
                    <Clock size={12} /> {formatDuration(seg.start_time)} – {formatDuration(seg.end_time)}
                  </span>
                  {seg.speaker_label && <span className="segment__speaker">{seg.speaker_label}</span>}
                  {seg.chapter_title && <span className="segment__chapter">{seg.chapter_title}</span>}
                </div>
                {editingSegmentId === seg.id ? (
                  <button className="btn btn--ghost btn--sm" onClick={cancelEditingSegment}>
                    <X size={13} /> Cancel
                  </button>
                ) : (
                  <button
                    className="btn btn--ghost btn--sm"
                    onClick={() => startEditingSegment(seg)}
                    aria-label="Edit segment"
                  >
                    <Pencil size={13} /> Edit
                  </button>
                )}
              </div>

              {editingSegmentId === seg.id ? (
                <div className="segment__editor">
                  <textarea
                    className="segment__textarea"
                    value={segmentDraft}
                    onChange={(e) => setSegmentDraft(e.target.value)}
                    rows={Math.max(3, Math.min(12, Math.ceil((segmentDraft.length || 1) / 90)))}
                    autoFocus
                  />
                  <div className="segment__editorActions">
                    <button
                      className="btn btn--primary btn--sm"
                      onClick={() => saveSegment(seg)}
                      disabled={savingSegmentId === seg.id}
                    >
                      {savingSegmentId === seg.id ? (
                        <>
                          <Loader2 className="lucide-spin" size={13} /> Saving…
                        </>
                      ) : (
                        <>
                          <Check size={13} /> Save
                        </>
                      )}
                    </button>
                    <button className="btn btn--ghost btn--sm" onClick={cancelEditingSegment}>
                      <X size={13} /> Cancel
                    </button>
                  </div>
                </div>
              ) : (
                <p
                  className="segment__text"
                  role="button"
                  tabIndex={0}
                  title="Click to edit"
                  onClick={() => startEditingSegment(seg)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" || e.key === " ") {
                      e.preventDefault();
                      startEditingSegment(seg);
                    }
                  }}
                >
                  {seg.text}
                </p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function ClipVideo({ clip }) {
  const [videoUrl, setVideoUrl] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    let active = true;
    let objectUrl = null;

    getClipStreamUrl(clip.id)
      .then((url) => {
        if (!active) {
          URL.revokeObjectURL(url);
          return;
        }
        objectUrl = url;
        setVideoUrl(url);
      })
      .catch((err) => {
        if (active) setError(err?.message || "Failed to load clip.");
      });

    return () => {
      active = false;
      if (objectUrl) URL.revokeObjectURL(objectUrl);
    };
  }, [clip.id]);

  if (error) return <div className="clipVideo__error"><AlertCircle size={14} /> {error}</div>;
  if (!videoUrl) {
    return (
      <div className="clipVideo__loading">
        <Loader2 className="lucide-spin" size={18} /> Loading…
      </div>
    );
  }
  return <video className="clipVideo__video" src={videoUrl} controls playsInline />;
}

function ClipsView({ projectId, mediaId }) {
  const [clips, setClips] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    getProjectClips(projectId)
      .then((data) => {
        if (!active) return;
        const arr = Array.isArray(data) ? data : [];
        setClips(arr.filter((c) => String(c.media_id) === String(mediaId)));
        setLoading(false);
      })
      .catch(() => {
        if (!active) return;
        setError("Failed to load clips.");
        setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [projectId, mediaId]);

  if (loading) {
    return (
      <div className="stateBox">
        <Loader2 className="lucide-spin" size={18} /> Loading clips…
      </div>
    );
  }

  if (error) {
    return (
      <div className="stateBox stateBox--error">
        <AlertCircle size={18} /> {error}
      </div>
    );
  }

  if (clips.length === 0) {
    return (
      <div className="emptyState">
        <div className="emptyState__icon">
          <Film size={36} color="#4F46E5" />
        </div>
        <h3 className="emptyState__title">No clips yet</h3>
        <p className="emptyState__text">Clips generated from this resource will appear here.</p>
      </div>
    );
  }

  return (
    <div className="clips">
      {clips.map((clip) => (
        <div key={clip.id} className="clip">
          <div className="clip__video">
            <ClipVideo clip={clip} />
          </div>
          <div className="clip__body">
            <h4 className="clip__title">{clip.title}</h4>
            <div className="clip__meta">
              <span className="clip__time">
                <Clock size={12} /> {formatDuration(clip.start_time)} – {formatDuration(clip.end_time)}
              </span>
            </div>
            {clip.reason && <p className="clip__reason">{clip.reason}</p>}
          </div>
        </div>
      ))}
    </div>
  );
}

function ContentView({ mediaId }) {
  const [pack, setPack] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [editingContent, setEditingContent] = useState(null);
  const [editBody, setEditBody] = useState("");
  const [savingContent, setSavingContent] = useState(false);

  const loadPack = useCallback(async () => {
    try {
      const data = await getCampaignPack(mediaId);
      setPack(data);
      setError("");
    } catch (err) {
      if (err.status === 404) {
        setPack(null);
        setError("");
      } else {
        setError("Failed to load content.");
      }
    }
  }, [mediaId]);

  useEffect(() => {
    let active = true;
    Promise.resolve()
      .then(() => loadPack())
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [loadPack]);

  const handleGenerate = async () => {
    setIsGenerating(true);
    setError("");
    try {
      const data = await generateCampaignPack(mediaId);
      if (data && Array.isArray(data.assets)) {
        setPack(data);
      } else {
        await loadPack();
      }
    } catch (err) {
      setError("Content generation failed: " + (err.message || "Unknown error"));
    } finally {
      setIsGenerating(false);
    }
  };

  const startEdit = (asset) => {
    setEditingContent(asset);
    setEditBody(typeof asset.body_json === "string" ? asset.body_json : JSON.stringify(asset.body_json, null, 2));
  };

  const cancelEdit = () => {
    setEditingContent(null);
    setEditBody("");
  };

  const handleSaveEdit = async (asset) => {
    setSavingContent(true);
    setError("");
    try {
      await updateGeneratedContent(asset.id, { body_json: editBody });
      await loadPack();
      setEditingContent(null);
      setEditBody("");
    } catch (err) {
      setError("Failed to save content: " + (err.message || "Unknown error"));
    } finally {
      setSavingContent(false);
    }
  };

  const handleExportSingle = async (contentId) => {
    try {
      await exportContentAsset(contentId, "markdown");
    } catch (err) {
      setError("Failed to export asset: " + (err.message || "Unknown error"));
    }
  };

  const handleExportAll = async () => {
    try {
      await exportCampaignPack(mediaId);
    } catch (err) {
      setError("Failed to export campaign pack: " + (err.message || "Unknown error"));
    }
  };

  if (loading) {
    return (
      <div className="stateBox">
        <Loader2 className="lucide-spin" size={18} /> Loading AI content…
      </div>
    );
  }

  if (error && !pack) {
    return (
      <div className="stateBox stateBox--error">
        <AlertCircle size={18} /> {error}
      </div>
    );
  }

  if (!pack) {
    return (
      <div className="emptyState">
        <div className="emptyState__icon">
          <Sparkles size={36} color="#4F46E5" />
        </div>
        <h3 className="emptyState__title">No AI content yet</h3>
        <p className="emptyState__text">
          Generate a campaign pack to turn this resource into ready-to-publish social content.
        </p>
        <button className="btn btn--primary" onClick={handleGenerate} disabled={isGenerating}>
          {isGenerating ? (
            <>
              <Loader2 className="lucide-spin" size={16} /> Generating…
            </>
          ) : (
            <>
              <Sparkles size={16} /> Generate Content
            </>
          )}
        </button>
      </div>
    );
  }

  const assets = Array.isArray(pack.assets) ? pack.assets : [];

  return (
    <div className="contentView">
      {error && (
        <div className="inlineError">
          <AlertCircle size={15} /> {error}
        </div>
      )}

      <div className="contentHeader">
        <h3 className="contentHeader__title">
          Campaign Pack
          <span className="contentHeader__count">{pack.count || assets.length} Assets</span>
        </h3>
        <button className="btn btn--success" onClick={handleExportAll}>
          <Download size={16} /> Export All (ZIP)
        </button>
      </div>

      {assets.length === 0 ? (
        <div className="stateBox">No assets in this pack yet.</div>
      ) : (
        <div className="contentList">
          {assets.map((asset) => (
            <div key={asset.id} className="contentAsset">
              <div className="contentAsset__header">
                <div className="contentAsset__heading">
                  <h4 className="contentAsset__title">{asset.title}</h4>
                  {asset.content_type && <span className="contentTypeBadge">{asset.content_type}</span>}
                </div>
                <div className="contentAsset__actions">
                  <button className="btn btn--outline btn--sm" onClick={() => handleExportSingle(asset.id)}>
                    <Download size={13} /> Download
                  </button>
                  {editingContent?.id === asset.id ? (
                    <button className="btn btn--ghost btn--sm" onClick={cancelEdit}>
                      <X size={13} /> Cancel
                    </button>
                  ) : (
                    <button className="btn btn--outline btn--sm" onClick={() => startEdit(asset)}>
                      <Pencil size={13} /> Edit
                    </button>
                  )}
                </div>
              </div>

              {editingContent?.id === asset.id ? (
                <div className="contentAsset__editor">
                  <textarea
                    className="contentAsset__textarea"
                    value={editBody}
                    onChange={(e) => setEditBody(e.target.value)}
                    rows={12}
                  />
                  <div className="contentAsset__editorActions">
                    <button
                      className="btn btn--primary btn--sm"
                      onClick={() => handleSaveEdit(asset)}
                      disabled={savingContent}
                    >
                      {savingContent ? (
                        <>
                          <Loader2 className="lucide-spin" size={13} /> Saving…
                        </>
                      ) : (
                        <>
                          <Check size={13} /> Save Changes
                        </>
                      )}
                    </button>
                    <button className="btn btn--ghost btn--sm" onClick={cancelEdit}>
                      <X size={13} /> Cancel
                    </button>
                  </div>
                </div>
              ) : (
                <div className="contentAsset__body">{parseBodyJson(asset.body_json)}</div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
