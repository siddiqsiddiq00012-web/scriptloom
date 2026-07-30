import React, { useState } from "react";
import "./Dashboard.css";
import UploadModal from "../../components/modals/UploadModal";
import DemoModal from "../../components/modals/DemoModal";
import UpgradeModal from "../../components/modals/UpgradeModal";
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
} from "lucide-react";

function Dashboard() {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [searchQuery, setSearchQuery] = useState("");
  const [filterType, setFilterType] = useState("all");

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

  const assets = [
    {
      id: 1,
      title: "Q3 B2B SaaS Growth & Positioning Masterclass",
      speaker: "Sarah Jenkins (Founder & CEO)",
      type: "Webinar",
      duration: "45 mins",
      date: "Today, 2:15 PM",
      assets: ["Video Script", "LinkedIn Carousel", "Substack Essay", "X Thread"],
      status: "Campaign Pack Ready",
      packContent: {
        hook: "Why generic AI prose is killing B2B authority in 2026...",
        carouselSlides: 5,
        newsletterTitle: "The End of Commodity Marketing",
      },
    },
    {
      id: 2,
      title: "Customer Discovery & Enterprise Authority Keynote",
      speaker: "Marcus Chen (VP of Product)",
      type: "Podcast",
      duration: "32 mins",
      date: "Yesterday",
      assets: ["Video Script", "LinkedIn Carousel", "Substack Essay"],
      status: "Campaign Pack Ready",
      packContent: {
        hook: "Conversations contain 10x more positioning clarity than landing pages...",
        carouselSlides: 4,
        newsletterTitle: "Unlocking Trapped Spoken Knowledge",
      },
    },
    {
      id: 3,
      title: "Why Generic AI Copy Destroys B2B Trust",
      speaker: "Sarah Jenkins (Founder & CEO)",
      type: "Zoom Call",
      duration: "18 mins",
      date: "3 days ago",
      assets: ["Video Script", "LinkedIn Carousel"],
      status: "Campaign Pack Ready",
      packContent: {
        hook: "As marginal text cost approaches zero, authentic conviction value approaches infinity...",
        carouselSlides: 4,
        newsletterTitle: "Authenticity is the Only Defensible Strategy",
      },
    },
  ];

  const filteredAssets = assets.filter((item) => {
    const matchesSearch =
      item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.speaker.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesType = filterType === "all" || item.type.toLowerCase().includes(filterType);
    return matchesSearch && matchesType;
  });

  const handleCopyPack = (item) => {
    const text = `CAMPAIGN PACK: ${item.title}\nSpeaker: ${item.speaker}\n\nHOOK:\n"${item.packContent.hook}"\n\nSUBSTACK ESSAY:\nTitle: ${item.packContent.newsletterTitle}\n\nFORMATTED LINKEDIN CAROUSEL (${item.packContent.carouselSlides} Slides Ready)`;
    navigator.clipboard.writeText(text);
    showToast(`Copied "${item.title}" Campaign Pack to clipboard!`);
  };

  const handleExportPDF = (item) => {
    showToast(`Downloading PDF Carousel & Script Pack for "${item.title}"...`);
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
          <div className="appDashboard__logo">
            <span>S</span>
          </div>
          <div>
            <h1 className="appDashboard__brandTitle">Scriptloom</h1>
            <p className="appDashboard__brandTag">AI Content OS</p>
          </div>

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
            onClick={() => setIsUploadOpen(true)}
          >
            <Plus size={16} /> Import Content
          </button>

          <button
            className="appDashboard__btnUpgrade"
            onClick={() => setIsUpgradeOpen(true)}
          >
            <Crown size={16} /> Pro
          </button>
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
          {/* DASHBOARD VIEW */}
          {activeTab === "dashboard" && (
            <div className="appDashboard__view">
              {/* Executive Metrics */}
              <div className="appDashboard__metricsGrid">
                <div className="appDashboard__metricCard">
                  <div className="appDashboard__metricHeader">
                    <Play size={18} color="#4F46E5" />
                    <span>Spoken Knowledge</span>
                  </div>
                  <span className="appDashboard__metricNum">142.5 hrs</span>
                  <p className="appDashboard__metricSub">From 38 webinars, podcasts & calls</p>
                </div>

                <div className="appDashboard__metricCard">
                  <div className="appDashboard__metricHeader">
                    <Sparkles size={18} color="#8B5CF6" />
                    <span>Voice DNA Match</span>
                  </div>
                  <span className="appDashboard__metricNum">99.4%</span>
                  <p className="appDashboard__metricSub">0% generic AI slop detected</p>
                </div>

                <div className="appDashboard__metricCard">
                  <div className="appDashboard__metricHeader">
                    <FileText size={18} color="#06B6D4" />
                    <span>Campaign Packs</span>
                  </div>
                  <span className="appDashboard__metricNum">38 Packs</span>
                  <p className="appDashboard__metricSub">152 multi-platform assets created</p>
                </div>

                <div className="appDashboard__metricCard">
                  <div className="appDashboard__metricHeader">
                    <Zap size={18} color="#EC4899" />
                    <span>Time Saved</span>
                  </div>
                  <span className="appDashboard__metricNum">184 hrs</span>
                  <p className="appDashboard__metricSub">Manual editing drag eliminated</p>
                </div>
              </div>

              {/* Quick Action Grid */}
              <div className="appDashboard__actionsGrid">
                <button
                  className="appDashboard__actionCard"
                  onClick={() => setIsUploadOpen(true)}
                >
                  <div className="appDashboard__actionIcon">
                    <UploadCloud size={24} />
                  </div>
                  <div className="appDashboard__actionText">
                    <strong>Import Long-Form Content</strong>
                    <span>Upload webinar, podcast, or Zoom recording</span>
                  </div>
                  <ChevronRight size={18} />
                </button>

                <button
                  className="appDashboard__actionCard"
                  onClick={() => setActiveTab("studio")}
                >
                  <div className="appDashboard__actionIcon" style={{ background: "#F3E8FF", color: "#8B5CF6" }}>
                    <PenTool size={24} />
                  </div>
                  <div className="appDashboard__actionText">
                    <strong>Content Studio</strong>
                    <span>Generate & refine multi-platform packs</span>
                  </div>
                  <ChevronRight size={18} />
                </button>

                <button
                  className="appDashboard__actionCard"
                  onClick={() => setActiveTab("ai")}
                >
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

                <div className="appDashboard__table">
                  {filteredAssets.map((item) => (
                    <div key={item.id} className="appDashboard__tableRow">
                      <div className="appDashboard__colTitle">
                        <div className="appDashboard__playIcon">
                          <Play size={14} />
                        </div>
                        <div>
                          <strong>{item.title}</strong>
                          <p>{item.speaker} • {item.date}</p>
                        </div>
                      </div>

                      <div className="appDashboard__colType">
                        <span className="appDashboard__typeBadge">{item.type}</span>
                        <span className="appDashboard__dur">{item.duration}</span>
                      </div>

                      <div className="appDashboard__colPacks">
                        {item.assets.map((assetName, idx) => (
                          <span key={idx} className="appDashboard__assetTag">
                            {assetName}
                          </span>
                        ))}
                      </div>

                      <div className="appDashboard__colActions">
                        <button
                          className="appDashboard__btnIconBtn"
                          title="View Campaign Pack"
                          onClick={() => {
                            setSelectedPack(item);
                            setIsUploadOpen(true);
                          }}
                        >
                          <Eye size={16} /> View Pack
                        </button>

                        <button
                          className="appDashboard__btnIconBtn"
                          title="Copy Assets"
                          onClick={() => handleCopyPack(item)}
                        >
                          <Copy size={16} /> Copy
                        </button>

                        <button
                          className="appDashboard__btnIconBtn"
                          title="Export PDF"
                          onClick={() => handleExportPDF(item)}
                        >
                          <Download size={16} /> PDF
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* OTHER TABS */}
          {activeTab !== "dashboard" && (
            <div className="appDashboard__view">
              <div className="appDashboard__moduleHeader">
                <h2 style={{ textTransform: "capitalize" }}>{activeTab} Workspace</h2>
                <p>Preserving creator voice with zero translation drag</p>
              </div>

              <div className="appDashboard__moduleCard">
                <Sparkles size={36} color="#4F46E5" />
                <h3>{activeTab.toUpperCase()} Operating Module Active</h3>
                <p>Connected to central Voice DNA & Brand Memory RAG store.</p>
                <button
                  className="appDashboard__btnPrimary"
                  onClick={() => setIsUploadOpen(true)}
                >
                  Import New Long-Form Content
                </button>
              </div>
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