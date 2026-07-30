import React, { useState } from "react";
import "./WorkspaceView.css";
import {
  Home,
  Folder,
  UploadCloud,
  PenTool,
  Sparkles,
  Image,
  Send,
  BarChart2,
  Settings,
  ArrowUpRight,
  Clock,
  CheckCircle2,
  Sliders,
  Copy,
  Plus,
  Play,
  FileText,
} from "lucide-react";

function WorkspaceView({ activeTab, onOpenUpload, onOpenUpgrade }) {
  const [toneMode, setToneMode] = useState("founder");

  const recentUploads = [
    {
      id: 1,
      title: "Q3 Strategy & B2B Positioning Masterclass",
      speaker: "Founder / CEO",
      duration: "45 mins",
      date: "2 hours ago",
      status: "Campaign Pack Ready",
    },
    {
      id: 2,
      title: "Customer Discovery & Product Roadmap Keynote",
      speaker: "VP of Product",
      duration: "32 mins",
      date: "Yesterday",
      status: "Campaign Pack Ready",
    },
    {
      id: 3,
      title: "Why Generic AI Copy Destroys Enterprise Authority",
      speaker: "Founder / CEO",
      duration: "18 mins",
      date: "3 days ago",
      status: "Campaign Pack Ready",
    },
  ];

  return (
    <div className="workspaceView">
      {/* DASHBOARD TAB */}
      {activeTab === "dashboard" && (
        <div className="workspaceView__container">
          <div className="workspaceView__header">
            <div>
              <h2>Executive Operations Dashboard</h2>
              <p>Persistent Brand Memory & Campaign Pack Overview</p>
            </div>
            <button className="workspaceView__primaryBtn" onClick={onOpenUpload}>
              <Plus size={16} /> New Recording
            </button>
          </div>

          {/* Stats Bar */}
          <div className="workspaceView__statsGrid">
            <div className="workspaceView__statCard">
              <span className="workspaceView__statNum">142 hrs</span>
              <span className="workspaceView__statLabel">Spoken Knowledge Indexed</span>
            </div>
            <div className="workspaceView__statCard">
              <span className="workspaceView__statNum">99.4%</span>
              <span className="workspaceView__statLabel">Voice DNA Match Rate</span>
            </div>
            <div className="workspaceView__statCard">
              <span className="workspaceView__statNum">38 Packs</span>
              <span className="workspaceView__statLabel">Zero-Edit Campaigns Exported</span>
            </div>
          </div>

          {/* Recent Uploads */}
          <div className="workspaceView__section">
            <div className="workspaceView__sectionHeader">
              <h3>Recent Conversations</h3>
              <span>Auto-Generated Campaign Packs</span>
            </div>

            <div className="workspaceView__list">
              {recentUploads.map((item) => (
                <div key={item.id} className="workspaceView__listItem">
                  <div className="workspaceView__listInfo">
                    <div className="workspaceView__itemIcon">
                      <Play size={16} />
                    </div>
                    <div>
                      <h4>{item.title}</h4>
                      <p>
                        {item.speaker} • {item.duration} • {item.date}
                      </p>
                    </div>
                  </div>
                  <div className="workspaceView__listActions">
                    <span className="workspaceView__statusBadge">
                      <CheckCircle2 size={12} /> {item.status}
                    </span>
                    <button
                      className="workspaceView__actionBtn"
                      onClick={onOpenUpload}
                    >
                      View Assets <ArrowUpRight size={14} />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* CONTENT STUDIO TAB */}
      {activeTab === "studio" && (
        <div className="workspaceView__container">
          <div className="workspaceView__header">
            <div>
              <h2>Content Studio & Tone Adjuster</h2>
              <p>Refine campaign packs with active Voice DNA parameters</p>
            </div>
            <div className="workspaceView__toneSelector">
              <Sliders size={16} />
              <button
                className={toneMode === "founder" ? "tone--active" : ""}
                onClick={() => setToneMode("founder")}
              >
                Authoritative Founder
              </button>
              <button
                className={toneMode === "tech" ? "tone--active" : ""}
                onClick={() => setToneMode("tech")}
              >
                Technical Conviction
              </button>
            </div>
          </div>

          <div className="workspaceView__editorCard">
            <div className="workspaceView__editorHeader">
              <FileText size={18} color="#4F46E5" />
              <span>Camera-Ready Script (Hook A)</span>
              <button className="workspaceView__copySmBtn">
                <Copy size={14} /> Copy Script
              </button>
            </div>
            <div className="workspaceView__editorBody">
              <p>
                "As the marginal cost of generic LLM text generation approaches zero, the market
                value of authentic, proprietary human insight approaches infinity. B2B software
                buyers convert through founder-led authority..."
              </p>
            </div>
          </div>
        </div>
      )}

      {/* AI WORKSPACE TAB */}
      {activeTab === "ai" && (
        <div className="workspaceView__container">
          <div className="workspaceView__header">
            <div>
              <h2>Brand Memory & Voice DNA Inspector</h2>
              <p>Semantic vector index & vocabulary rules</p>
            </div>
            <button className="workspaceView__primaryBtn" onClick={onOpenUpgrade}>
              <Sparkles size={16} /> Fine-Tune Voice Model
            </button>
          </div>

          <div className="workspaceView__dnaGrid">
            <div className="workspaceView__dnaBox">
              <h4>Active Tone Persona</h4>
              <p>Direct B2B Founder • Zero Jargon • High Conviction</p>
            </div>
            <div className="workspaceView__dnaBox">
              <h4>Banned Vocabulary</h4>
              <p>"game-changer", "synergy", "paradigm shift", "revolutionary"</p>
            </div>
            <div className="workspaceView__dnaBox">
              <h4>Historical Vectors</h4>
              <p>1,480 assertions indexed across 38 recordings</p>
            </div>
          </div>
        </div>
      )}

      {/* GENERIC TAB FALLBACK (Projects, Upload, Media, Publishing, Analytics, Settings) */}
      {!["dashboard", "studio", "ai"].includes(activeTab) && (
        <div className="workspaceView__container">
          <div className="workspaceView__header">
            <div>
              <h2 style={{ textTransform: "capitalize" }}>{activeTab} Workspace</h2>
              <p>Scriptloom Content Operations Engine</p>
            </div>
            <button className="workspaceView__primaryBtn" onClick={onOpenUpload}>
              Quick Action
            </button>
          </div>

          <div className="workspaceView__placeholderCard">
            <Sparkles size={32} color="#4F46E5" />
            <h3>{activeTab.toUpperCase()} Module Active</h3>
            <p>Integrated with your central Voice DNA & Brand Memory store.</p>
            <button className="workspaceView__actionBtn" onClick={onOpenUpload}>
              Launch Workflow
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default WorkspaceView;
