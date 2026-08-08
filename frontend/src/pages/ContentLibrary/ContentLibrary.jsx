import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { Link } from "react-router-dom";
import "./ContentLibrary.css";
import {
  FileText,
  Search,
  ArrowLeft,
  ExternalLink,
  Trash2,
  Loader2,
  Filter,
  RefreshCw,
} from "lucide-react";
import { api } from "../../api/client";

const CONTENT_TYPES = [
  { key: "", label: "All Types" },
  { key: "linkedin_post", label: "LinkedIn Post" },
  { key: "x_thread", label: "X Thread" },
  { key: "instagram_caption", label: "Instagram Caption" },
  { key: "newsletter", label: "Newsletter" },
  { key: "article", label: "Blog Article" },
  { key: "video_script", label: "Video Script" },
  { key: "hook", label: "Content Hooks" },
  { key: "title", label: "Titles" },
  { key: "content_idea", label: "Content Ideas" },
];

export default function ContentLibrary() {
  const navigate = useNavigate();
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [selectedType, setSelectedType] = useState("");
  const [selectedProject, setSelectedProject] = useState("");
  const [projects, setProjects] = useState([]);
  const [expandedId, setExpandedId] = useState(null);

  const loadContent = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (selectedType) params.set("content_type", selectedType);
      if (selectedProject) params.set("project_id", selectedProject);
      params.set("limit", "100");

      const data = await api.get(`/generation/library?${params.toString()}`);
      setItems(data.items || []);
      setTotal(data.total || 0);
    } catch {
      setItems([]);
    } finally {
      setLoading(false);
    }
  }, [selectedType, selectedProject]);

  useEffect(() => {
    loadContent();
  }, [loadContent]);

  useEffect(() => {
    api.get("/projects")
      .then((data) => setProjects(Array.isArray(data) ? data : []))
      .catch(() => {});
  }, []);

  const handleDelete = async (item) => {
    try {
      await api.delete(`/generation/content/${item.id}`);
      setItems((prev) => prev.filter((i) => i.id !== item.id));
      setTotal((prev) => prev - 1);
    } catch {
    }
  };

  const parseBody = (bodyJson) => {
    try {
      return JSON.parse(bodyJson || "{}");
    } catch {
      return { body: bodyJson };
    }
  };

  return (
    <div className="clPage">
      <div className="clPage__header">
        <div>
          <h2 className="clPage__title">Content Library</h2>
          <p className="clPage__subtitle">
            All AI-generated content across your projects. Filter by type or project.
          </p>
        </div>
        <button className="btn btn-ghost" onClick={() => navigate("/dashboard")}>
          <ArrowLeft size={15} /> Back to Dashboard
        </button>
      </div>

      <div className="clPage__filters">
        <div className="clPage__filterGroup">
          <Filter size={15} />
          <select
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value)}
            className="clPage__select"
          >
            {CONTENT_TYPES.map((ct) => (
              <option key={ct.key} value={ct.key}>
                {ct.label}
              </option>
            ))}
          </select>
          <select
            value={selectedProject}
            onChange={(e) => setSelectedProject(e.target.value)}
            className="clPage__select"
          >
            <option value="">All Projects</option>
            {projects.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name}
              </option>
            ))}
          </select>
        </div>
        <div className="clPage__filterMeta">
          {total > 0 && (
            <span className="clPage__count">
              {total} asset{total !== 1 ? "s" : ""}
            </span>
          )}
          <button className="btn btn-ghost btn-sm" onClick={loadContent}>
            <RefreshCw size={14} />
          </button>
        </div>
      </div>

      {loading ? (
        <div className="clPage__loading">
          <Loader2 className="lucide-spin" size={20} />
          Loading content...
        </div>
      ) : items.length === 0 ? (
        <div className="clPage__empty">
          <FileText size={32} />
          <p>No generated content yet.</p>
          <p className="clPage__emptyHint">
            Go to a media resource and use the AI Generation tab to create content.
          </p>
        </div>
      ) : (
        <div className="clPage__grid">
          {items.map((item) => {
            const body = parseBody(item.body_json);
            const preview =
              body.body ||
              body.markdown ||
              body.caption ||
              (Array.isArray(body.tweets)
                ? body.tweets.join("\n")
                : bodyJson_to_preview(item.body_json));
            const isExpanded = expandedId === item.id;

            return (
              <div
                key={item.id}
                className={`clPage__card card card-padding ${isExpanded ? "clPage__card--expanded" : ""}`}
                onClick={() => setExpandedId(isExpanded ? null : item.id)}
              >
                <div className="clPage__cardHeader">
                  <span className="clPage__badge">
                    {item.content_type.replace(/_/g, " ")}
                  </span>
                  <span className="clPage__date">
                    {item.created_at
                      ? new Date(item.created_at).toLocaleDateString()
                      : ""}
                  </span>
                </div>
                <h3 className="clPage__cardTitle">{item.title || "Untitled"}</h3>
                <div className="clPage__cardMeta">
                  {item.media_filename && (
                    <span>{item.media_filename}</span>
                  )}
                </div>
                <div className={`clPage__cardBody ${isExpanded ? "" : "clPage__cardBody--collapsed"}`}>
                  <pre className="clPage__cardText">
                    {isExpanded
                      ? typeof preview === "string"
                        ? preview
                        : JSON.stringify(preview, null, 2)
                      : truncatePreview(preview)}
                  </pre>
                </div>
                {isExpanded && (
                  <div className="clPage__cardActions">
                    {item.project_id && item.media_id && (
                      <button
                        className="btn btn-ghost btn-sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          navigate(`/projects/${item.project_id}/media/${item.media_id}`);
                        }}
                      >
                        <ExternalLink size={13} /> View Source
                      </button>
                    )}
                    <button
                      className="btn btn-ghost btn-sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        navigator.clipboard.writeText(
                          typeof preview === "string"
                            ? preview
                            : JSON.stringify(preview, null, 2)
                        );
                      }}
                    >
                      Copy
                    </button>
                    <button
                      className="btn btn-ghost btn-sm btn--danger"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDelete(item);
                      }}
                    >
                      <Trash2 size={13} />
                    </button>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

function truncatePreview(text) {
  if (!text || typeof text !== "string") return "No preview";
  const lines = text.split("\n").slice(0, 3).join("\n");
  return lines.length > 150 ? lines.slice(0, 150) + "..." : lines;
}

function bodyJson_to_preview(bodyJson) {
  if (!bodyJson) return "No content";
  try {
    const obj = JSON.parse(bodyJson);
    return Object.values(obj).find((v) => typeof v === "string") || JSON.stringify(obj);
  } catch {
    return bodyJson.slice(0, 150);
  }
}
