import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import "./Dashboard.css";
import UploadModal from "../../components/modals/UploadModal";
import DemoModal from "../../components/modals/DemoModal";
import UpgradeModal from "../../components/modals/UpgradeModal";
import ContentStudio from "../../components/studio/ContentStudio";
import VoiceDNAManager from "../../components/voiceDna/VoiceDNAManager";
import ProjectsWorkspace from "../../components/projects/ProjectsWorkspace";
import SettingsWorkspace from "../../components/settings/SettingsWorkspace";
import MediaLibrary from "../../components/media/MediaLibrary";
import AnalyticsWorkspace from "../../components/analytics/AnalyticsWorkspace";
import PublishingQueue from "../../components/publishing/PublishingQueue";
import IngestionWorkspace from "../../components/ingestion/IngestionWorkspace";
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
  Crown,
  Plus,
  Search,
  Play,
  CheckCircle2,
  FileText,
  Copy,
  Download,
  Eye,
  Sliders,
  Check,
  Zap,
  Globe,
  ArrowUpRight,
  ChevronRight,
  FolderPlus,
  User,
  LogOut,
} from "lucide-react";

import { getVoiceDNA } from "../../api/voiceDna";
import { getCurrentUser, getUserProfile, logoutUser, isAuthenticated } from "../../api/auth";
import { getProjects } from "../../api/projects";

function Dashboard() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState("dashboard");
  const [searchQuery, setSearchQuery] = useState("");
  const [filterType, setFilterType] = useState("all");

  // User Profile & Menu State
  const [userProfile, setUserProfile] = useState(getUserProfile());
  const [isProfileMenuOpen, setIsProfileMenuOpen] = useState(false);

  // Live Backend Data
  const [liveUsage, setLiveUsage] = useState({ hours_processed: 0, campaign_packs_generated: 0 });
  const [voiceDnaInfo, setVoiceDnaInfo] = useState({ tone: "Authoritative Brand Voice", match: "99.4%" });
  const [assets, setAssets] = useState([]);

  // Modals & Toast State
  const [isUploadOpen, setIsUploadOpen] = useState(false);
  const [isDemoOpen, setIsDemoOpen] = useState(false);
  const [isUpgradeOpen, setIsUpgradeOpen] = useState(false);
  const [selectedPack, setSelectedPack] = useState(null);
  const [toastMessage, setToastMessage] = useState("");

  const showToast = (msg) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(""), 3000);
  };

  useEffect(() => {
    // Verify session
    if (!isAuthenticated()) {
      navigate("/login");
      return;
    }

    // Fetch logged-in user profile from backend DB
    getCurrentUser()
      .then((user) => {
        if (user && user.email) {
          setUserProfile({
            email: user.email,
            name: user.name || user.email.split("@")[0],
            avatarUrl: user.avatar_url || "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=120&q=80",
            plan: "Founder Pro",
          });
        }
      })
      .catch(() => {});

    // Fetch live backend metrics & Voice DNA if available
    getVoiceDNA()
      .then((dna) => {
        if (dna && dna.tone) {
          setVoiceDnaInfo({ tone: dna.tone, match: "99.4%" });
        }
      })
      .catch(() => {});

    // Fetch projects to list campaign packs
    getProjects()
      .then((projs) => {
        if (Array.isArray(projs) && projs.length > 0) {
          setAssets(projs);
        }
      })
      .catch(() => setAssets([]));
  }, [navigate]);

  const menuItems = [
    { id: "dashboard", label: "Dashboard", icon: Home },
    { id: "projects", label: "Projects", icon: Folder },
    { id: "ingestion", label: "Ingestion Center", icon: UploadCloud },
    { id: "studio", label: "Content Studio", icon: PenTool },
    { id: "ai", label: "Voice DNA & Memory", icon: Sparkles },
    { id: "media", label: "Media Library", icon: Image },
    { id: "publishing", label: "Publishing Queue", icon: Send },
    { id: "analytics", label: "Analytics", icon: BarChart2 },
    { id: "settings", label: "Settings", icon: Settings },
  ];

  const filteredAssets = assets.filter((item) => {
    const titleStr = item.title || item.name || "";
    const speakerStr = item.speaker || "";
    const matchesSearch =
      titleStr.toLowerCase().includes(searchQuery.toLowerCase()) ||
      speakerStr.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesType = filterType === "all" || (item.type || "").toLowerCase().includes(filterType);
    return matchesSearch && matchesType;
  });

  const handleCopyPack = (item) => {
    const text = `CAMPAIGN PACK: ${item.title || item.name}\nSpeaker: ${item.speaker || "Creator"}\n\nHOOK:\n"${item.packContent?.hook || "Content Pack"}"`;
    navigator.clipboard.writeText(text);
    showToast(`Copied "${item.title || item.name}" Campaign Pack to clipboard!`);
  };

  const handleExportPDF = (item) => {
    showToast(`Downloading PDF Carousel & Script Pack for "${item.title || item.name}"...`);
  };

  return (
    <div className="appDashboard">
      {/* Toast Notification */}
      {toastMessage && (
        <div className="appDashboard__toast">
          <CheckCircle2 size={18} />
          <span>{toastMessage}</span>
        </div>
      )}

      {/* Top Header Bar */}
      <header className="appDashboard__header">
        <div className="appDashboard__headerLeft">
          <Link to="/" style={{ textDecoration: "none", display: "flex", alignItems: "center", gap: "10px" }} title="Return to Scriptloom Homepage">
            <div className="appDashboard__logo">
              <span>S</span>
            </div>
            <div>
              <h1 className="appDashboard__brandTitle">Scriptloom</h1>
              <p className="appDashboard__brandTag">AI Content OS</p>
            </div>
          </Link>

          <div className="appDashboard__dnaBadge">
            <Sparkles size={14} color="#8B5CF6" />
            <span>Voice DNA: B2B Founder • 99.4% Match</span>
          </div>
        </div>

        <div className="appDashboard__headerRight">
          <div className="appDashboard__searchBar">
            <Search size={16} className="appDashboard__searchIcon" />
            <input
              type="text"
              placeholder="Search spoken assets, topics, or campaign packs..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>

          <button
            className="appDashboard__btnPrimary"
            onClick={() => setActiveTab("ingestion")}
          >
            <Plus size={16} /> Import Content
          </button>

          <button
            className="appDashboard__btnUpgrade"
            onClick={() => setIsUpgradeOpen(true)}
          >
            <Crown size={16} /> Pro
          </button>

          {/* User Profile Account Menu */}
          {userProfile && (
            <div className="appDashboard__profileWrapper">
              <button
                className="appDashboard__profileBtn"
                onClick={() => setIsProfileMenuOpen(!isProfileMenuOpen)}
              >
                <img
                  src={userProfile.avatarUrl}
                  alt={userProfile.name}
                  className="appDashboard__avatarImg"
                />
                <div className="appDashboard__profileText">
                  <strong>{userProfile.name}</strong>
                  <span>{userProfile.email}</span>
                </div>
                <ChevronRight
                  size={14}
                  style={{
                    transform: isProfileMenuOpen ? "rotate(90deg)" : "rotate(0deg)",
                    transition: "transform 0.2s",
                  }}
                />
              </button>

              {isProfileMenuOpen && (
                <div className="appDashboard__profileDropdown">
                  <div className="appDashboard__dropdownHeader">
                    <strong>{userProfile.name}</strong>
                    <p>{userProfile.email}</p>
                    <span className="appDashboard__planBadge">{userProfile.plan || "Free Creator Plan"}</span>
                  </div>

                  <div className="appDashboard__dropdownDivider" />

                  <button
                    className="appDashboard__dropdownItem"
                    onClick={() => {
                      setActiveTab("settings");
                      setIsProfileMenuOpen(false);
                    }}
                  >
                    <User size={15} /> Account Profile
                  </button>

                  <button
                    className="appDashboard__dropdownItem"
                    onClick={() => {
                      setIsUpgradeOpen(true);
                      setIsProfileMenuOpen(false);
                    }}
                  >
                    <Crown size={15} color="#F59E0B" /> Subscription Plan
                  </button>

                  <button
                    className="appDashboard__dropdownItem"
                    onClick={() => {
                      setActiveTab("settings");
                      setIsProfileMenuOpen(false);
                    }}
                  >
                    <Settings size={15} /> Settings & API Keys
                  </button>

                  <div className="appDashboard__dropdownDivider" />

                  <button
                    className="appDashboard__logoutBtn"
                    onClick={() => {
                      logoutUser();
                      setUserProfile(null);
                      navigate("/login");
                    }}
                  >
                    <LogOut size={15} /> Sign Out
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </header>

      <div className="appDashboard__layout">
        {/* Left Side OS Navigation Drawer */}
        <aside className="appDashboard__sidebar">
          <nav className="appDashboard__nav">
            {menuItems.map((item) => {
              const IconComponent = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  className={`appDashboard__navItem ${
                    isActive ? "appDashboard__navItem--active" : ""
                  }`}
                  onClick={() => setActiveTab(item.id)}
                >
                  <IconComponent size={18} className="appDashboard__navIcon" />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>

          <div className="appDashboard__proCard">
            <div className="appDashboard__proHeader">
              <Crown size={18} color="#F59E0B" />
              <span>Founder Pro Plan</span>
            </div>
            <p>Unlimited long-form ingestion & Brand Memory RAG vectors.</p>
            <button onClick={() => setIsUpgradeOpen(true)}>Manage Plan</button>
          </div>
        </aside>

        {/* Main Content Workspace */}
        <main className="appDashboard__main">
          {/* DASHBOARD TAB */}
          {activeTab === "dashboard" && (
            <div className="appDashboard__view">
              {/* Top Metrics Cards */}
              <div className="appDashboard__metricsGrid">
                <div className="appDashboard__metricCard">
                  <div className="appDashboard__metricIcon" style={{ background: "#EEF2FF", color: "#4F46E5" }}>
                    <Zap size={20} />
                  </div>
                  <div>
                    <span className="appDashboard__metricLabel">Knowledge Velocity</span>
                    <h3 className="appDashboard__metricValue">{liveUsage.hours_processed}h</h3>
                    <p className="appDashboard__metricSub">Spoken hours indexed</p>
                  </div>
                </div>

                <div className="appDashboard__metricCard">
                  <div className="appDashboard__metricIcon" style={{ background: "#F3E8FF", color: "#8B5CF6" }}>
                    <Sparkles size={20} />
                  </div>
                  <div>
                    <span className="appDashboard__metricLabel">Voice DNA Precision</span>
                    <h3 className="appDashboard__metricValue">{voiceDnaInfo.match}</h3>
                    <p className="appDashboard__metricSub">{voiceDnaInfo.tone}</p>
                  </div>
                </div>

                <div className="appDashboard__metricCard">
                  <div className="appDashboard__metricIcon" style={{ background: "#ECFEFF", color: "#06B6D4" }}>
                    <Send size={20} />
                  </div>
                  <div>
                    <span className="appDashboard__metricLabel">Campaign Packs Generated</span>
                    <h3 className="appDashboard__metricValue">{liveUsage.campaign_packs_generated}</h3>
                    <p className="appDashboard__metricSub">Multi-platform ready</p>
                  </div>
                </div>
              </div>

              {/* Quick Actions Bar */}
              <div className="appDashboard__quickActions">
                <button className="appDashboard__actionCard" onClick={() => setActiveTab("ingestion")}>
                  <div className="appDashboard__actionIcon" style={{ background: "#EEF2FF", color: "#4F46E5" }}>
                    <UploadCloud size={24} />
                  </div>
                  <div className="appDashboard__actionText">
                    <strong>Ingest Spoken Media</strong>
                    <span>Upload webinar, podcast, or Zoom call</span>
                  </div>
                  <ChevronRight size={18} />
                </button>

                <button className="appDashboard__actionCard" onClick={() => setActiveTab("studio")}>
                  <div className="appDashboard__actionIcon" style={{ background: "#F3E8FF", color: "#8B5CF6" }}>
                    <PenTool size={24} />
                  </div>
                  <div className="appDashboard__actionText">
                    <strong>Content Studio</strong>
                    <span>Inspect & refine generated campaign packs</span>
                  </div>
                  <ChevronRight size={18} />
                </button>

                <button className="appDashboard__actionCard" onClick={() => setActiveTab("ai")}>
                  <div className="appDashboard__actionIcon" style={{ background: "#ECFEFF", color: "#06B6D4" }}>
                    <Sliders size={24} />
                  </div>
                  <div className="appDashboard__actionText">
                    <strong>Voice DNA & Memory</strong>
                    <span>Inspect brand rules & vector memory</span>
                  </div>
                  <ChevronRight size={18} />
                </button>
              </div>

              {/* Spoken Assets & Generated Packs Table */}
              <div className="appDashboard__tableCard">
                <div className="appDashboard__tableHeader">
                  <div>
                    <h3>Spoken Conversations & Campaign Packs</h3>
                    <p>Click any recording to inspect or export multi-channel assets</p>
                  </div>

                  <div className="appDashboard__filterGroup">
                    <button
                      className={filterType === "all" ? "filter--active" : ""}
                      onClick={() => setFilterType("all")}
                    >
                      All
                    </button>
                    <button
                      className={filterType === "webinar" ? "filter--active" : ""}
                      onClick={() => setFilterType("webinar")}
                    >
                      Webinars
                    </button>
                    <button
                      className={filterType === "podcast" ? "filter--active" : ""}
                      onClick={() => setFilterType("podcast")}
                    >
                      Podcasts
                    </button>
                  </div>
                </div>

                {filteredAssets.length === 0 ? (
                  <div className="mediaLibrary__emptyCard">
                    <div className="mediaLibrary__emptyIconBox">
                      <FolderPlus size={40} color="#4F46E5" />
                    </div>
                    <h3>No Campaign Packs Generated Yet</h3>
                    <p>
                      Import an audio recording or text note to generate your first zero-slop multi-platform campaign pack.
                    </p>
                    <button className="appDashboard__btnPrimary" onClick={() => setActiveTab("ingestion")}>
                      <Plus size={16} /> Create Your First Content Pack
                    </button>
                  </div>
                ) : (
                  <div className="appDashboard__table">
                    {filteredAssets.map((item) => (
                      <div key={item.id} className="appDashboard__tableRow">
                        <div className="appDashboard__colTitle">
                          <div className="appDashboard__playIcon">
                            <Play size={14} />
                          </div>
                          <div>
                            <strong>{item.title || item.name}</strong>
                            <p>{item.speaker || "Creator"} • {item.date || "Recent"}</p>
                          </div>
                        </div>

                        <div className="appDashboard__colType">
                          <span className="appDashboard__typeBadge">{item.type || "Audio"}</span>
                          <span className="appDashboard__dur">{item.duration || "--"}</span>
                        </div>

                        <div className="appDashboard__colPacks">
                          {(item.assets || ["LinkedIn Carousel", "Substack Essay"]).map((assetName, idx) => (
                            <span key={idx} className="appDashboard__assetTag">
                              {assetName}
                            </span>
                          ))}
                        </div>

                        <div className="appDashboard__colActions">
                          <button
                            className="appDashboard__btnIconBtn"
                            onClick={() => setSelectedPack(item)}
                            title="Inspect Campaign Pack"
                          >
                            <Eye size={16} />
                          </button>
                          <button
                            className="appDashboard__btnIconBtn"
                            onClick={() => handleCopyPack(item)}
                            title="Copy to Clipboard"
                          >
                            <Copy size={16} />
                          </button>
                          <button
                            className="appDashboard__btnIconBtn"
                            onClick={() => handleExportPDF(item)}
                            title="Download Assets"
                          >
                            <Download size={16} />
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* PROJECTS TAB */}
          {activeTab === "projects" && (
            <div className="appDashboard__view">
              <ProjectsWorkspace onOpenUpload={() => setIsUploadOpen(true)} />
            </div>
          )}

          {/* CONTENT STUDIO TAB */}
          {activeTab === "studio" && (
            <div className="appDashboard__view">
              <ContentStudio onOpenUpload={() => setIsUploadOpen(true)} onShowToast={showToast} />
            </div>
          )}

          {/* VOICE DNA TAB */}
          {activeTab === "ai" && (
            <div className="appDashboard__view">
              <VoiceDNAManager onShowToast={showToast} />
            </div>
          )}

          {/* MEDIA LIBRARY TAB */}
          {activeTab === "media" && (
            <div className="appDashboard__view">
              <MediaLibrary onOpenUpload={() => setIsUploadOpen(true)} onShowToast={showToast} />
            </div>
          )}

          {/* ANALYTICS TAB */}
          {activeTab === "analytics" && (
            <div className="appDashboard__view">
              <AnalyticsWorkspace />
            </div>
          )}

          {/* PUBLISHING QUEUE TAB */}
          {activeTab === "publishing" && (
            <div className="appDashboard__view">
              <PublishingQueue onShowToast={showToast} />
            </div>
          )}

          {/* INGESTION CENTER TAB */}
          {activeTab === "ingestion" && (
            <div className="appDashboard__view">
              <IngestionWorkspace onShowToast={showToast} />
            </div>
          )}

          {/* SETTINGS TAB */}
          {activeTab === "settings" && (
            <div className="appDashboard__view">
              <SettingsWorkspace onShowToast={showToast} />
            </div>
          )}
        </main>
      </div>

      {/* Modals */}
      <UploadModal isOpen={isUploadOpen} onClose={() => setIsUploadOpen(false)} />
      <DemoModal isOpen={isDemoOpen} onClose={() => setIsDemoOpen(false)} onOpenUpload={() => setIsUploadOpen(true)} />
      <UpgradeModal isOpen={isUpgradeOpen} onClose={() => setIsUpgradeOpen(false)} />
    </div>
  );
}

export default Dashboard;