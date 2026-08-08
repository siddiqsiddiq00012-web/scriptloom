import { useState, useEffect, useCallback, useRef } from "react";
import { Link, useNavigate } from "react-router-dom";
import "./Dashboard.css";
import {
  Home,
  Folder,
  Image,
  Settings,
  Plus,
  ChevronRight,
  User,
  LogOut,
  Zap,
  FileText,
  Film,
  FolderPlus,
  ArrowUpRight,
  Clock,
  BarChart3,
  CreditCard,
} from "lucide-react";

import { getCurrentUser, getUserProfile, logoutUser, isAuthenticated } from "../../api/auth";
import { getProjects } from "../../api/projects";
import { api } from "../../api/client";

import ProjectsWorkspace from "../../components/projects/ProjectsWorkspace";
import MediaLibrary from "../../components/media/MediaLibrary";
import SettingsWorkspace from "../../components/settings/SettingsWorkspace";
import { SkeletonMetricGrid, SkeletonRow } from "../../components/ui";
import EmptyState from "../../components/ui/EmptyState";

function Dashboard() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState("dashboard");

  const [userProfile, setUserProfile] = useState(getUserProfile());
  const [isProfileMenuOpen, setIsProfileMenuOpen] = useState(false);

  const [usage, setUsage] = useState(null);
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);

  const [toastMessage, setToastMessage] = useState("");
  const toastTimerRef = useRef(null);

  const showToast = useCallback((msg) => {
    if (toastTimerRef.current) clearTimeout(toastTimerRef.current);
    setToastMessage(msg);
    toastTimerRef.current = setTimeout(() => {
      setToastMessage("");
      toastTimerRef.current = null;
    }, 3000);
  }, []);

  useEffect(() => {
    return () => {
      if (toastTimerRef.current) clearTimeout(toastTimerRef.current);
    };
  }, []);

  useEffect(() => {
    if (!isAuthenticated()) {
      navigate("/login");
      return;
    }

    getCurrentUser()
      .then((user) => {
        if (user?.email) {
          setUserProfile({
            email: user.email,
            name: user.name || user.email.split("@")[0],
            avatarUrl: user.avatar_url || "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=120&q=80",
          });
        }
      })
      .catch(() => {});

    api.get("/billing/usage")
      .then((data) => setUsage(data))
      .catch(() => {});

    getProjects()
      .then((data) => setProjects(Array.isArray(data) ? data : []))
      .catch(() => setProjects([]))
      .finally(() => setLoading(false));
  }, [navigate]);

  const menuItems = [
    { id: "dashboard", label: "Dashboard", icon: Home },
    { id: "projects", label: "Projects", icon: Folder },
    { id: "media", label: "Media Library", icon: Image },
    { id: "billing", label: "Billing", icon: CreditCard, href: "/billing" },
    { id: "content-library", label: "Content Library", icon: FileText, href: "/content" },
    { id: "settings", label: "Settings", icon: Settings, href: "/settings" },
  ];

  const usagePercent = usage?.processing_minutes?.limit
    ? Math.min(100, (usage.processing_minutes.used / usage.processing_minutes.limit) * 100)
    : 0;
  const aiPercent = usage?.ai_generations?.limit
    ? Math.min(100, (usage.ai_generations.used / usage.ai_generations.limit) * 100)
    : 0;

  return (
    <div className="appDashboard">
      {toastMessage && <div className="toast">{toastMessage}</div>}

      {/* Header */}
      <header className="appDashboard__header">
        <div className="appDashboard__headerLeft">
          <Link to="/" className="appDashboard__brand">
            <div className="appDashboard__logo"><span>S</span></div>
            <div>
              <h1 className="appDashboard__brandTitle">Scriptloom</h1>
              <p className="appDashboard__brandTag">Content Studio</p>
            </div>
          </Link>
        </div>

        <div className="appDashboard__headerRight">
          {userProfile && (
            <div className="appDashboard__profileWrapper">
              <button className="appDashboard__profileBtn" onClick={() => setIsProfileMenuOpen(!isProfileMenuOpen)}>
                <img src={userProfile.avatarUrl} alt="" className="appDashboard__avatarImg" />
                <span className="appDashboard__profileName">{userProfile.name}</span>
                <ChevronRight size={14} style={{ transform: isProfileMenuOpen ? "rotate(90deg)" : "rotate(0)", transition: "transform 0.2s" }} />
              </button>

              {isProfileMenuOpen && (
                <div className="appDashboard__dropdown">
                  <div className="appDropdown__header">
                    <strong>{userProfile.name}</strong>
                    <p>{userProfile.email}</p>
                    {usage?.plan_display_name && <span className="badge badge-success">{usage.plan_display_name}</span>}
                  </div>
                  <div className="appDropdown__divider" />
                  <button className="appDropdown__item" onClick={() => { navigate("/settings"); setIsProfileMenuOpen(false); }}>
                    <User size={15} /> Account
                  </button>
                  <button className="appDropdown__item" onClick={() => { navigate("/settings"); setIsProfileMenuOpen(false); }}>
                    <Settings size={15} /> Settings
                  </button>
                  <div className="appDropdown__divider" />
                  <button className="appDropdown__item appDropdown__item--danger" onClick={() => { logoutUser(); navigate("/"); }}>
                    <LogOut size={15} /> Sign Out
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </header>

      {/* Layout */}
      <div className="appDashboard__layout">
        <aside className="appDashboard__sidebar">
          <nav className="appDashboard__nav">
            {menuItems.map((item) => {
              const Icon = item.icon;
              return (
                <button
                  key={item.id}
                  className={`appDashboard__navItem ${activeTab === item.id ? "appDashboard__navItem--active" : ""}`}
                  onClick={() => item.href ? navigate(item.href) : setActiveTab(item.id)}
                >
                  <Icon size={18} />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>
        </aside>

        <main className="appDashboard__main">
          {activeTab === "dashboard" && (
            <div className="animate-fadeIn">
              {/* Welcome */}
              <div className="dash__welcome">
                <div>
                  <h2 className="dash__welcomeTitle">Welcome back{userProfile?.name ? `, ${userProfile.name}` : ""}</h2>
                  <p className="dash__welcomeSub">Here's what's happening with your content projects.</p>
                </div>
                <button className="btn btn-primary" onClick={() => setActiveTab("projects")}>
                  <Plus size={16} /> New Project
                </button>
              </div>

              {/* Metrics */}
              {loading ? (
                <SkeletonMetricGrid />
              ) : (
                <div className="dash__metrics">
                  <div className="dash__metric card card-padding animate-fadeInUp stagger-1">
                    <div className="dash__metricIcon dash__metricIcon--blue"><Zap size={20} /></div>
                    <div>
                      <span className="dash__metricLabel">Processing</span>
                      <h3 className="dash__metricValue">{usage?.processing_minutes?.used ?? 0}</h3>
                      <p className="dash__metricSub">of {usage?.processing_minutes?.limit === -1 ? "unlimited" : (usage?.processing_minutes?.limit ?? "—")} min monthly</p>
                    </div>
                    <div className="dash__metricProgress">
                      <div className="progress-track"><div className="progress-fill" style={{ width: `${usagePercent}%` }} /></div>
                    </div>
                  </div>

                  <div className="dash__metric card card-padding animate-fadeInUp stagger-2">
                    <div className="dash__metricIcon dash__metricIcon--purple"><FileText size={20} /></div>
                    <div>
                      <span className="dash__metricLabel">AI Generations</span>
                      <h3 className="dash__metricValue">{usage?.ai_generations?.used ?? 0}</h3>
                      <p className="dash__metricSub">of {usage?.ai_generations?.limit === -1 ? "unlimited" : (usage?.ai_generations?.limit ?? "—")} monthly</p>
                    </div>
                    <div className="dash__metricProgress">
                      <div className="progress-track"><div className="progress-fill" style={{ width: `${aiPercent}%`, background: "var(--accent-purple)" }} /></div>
                    </div>
                  </div>

                  <div className="dash__metric card card-padding animate-fadeInUp stagger-3">
                    <div className="dash__metricIcon dash__metricIcon--cyan"><Film size={20} /></div>
                    <div>
                      <span className="dash__metricLabel">Projects</span>
                      <h3 className="dash__metricValue">{projects.length}</h3>
                      <p className="dash__metricSub">active projects</p>
                    </div>
                  </div>

                  <div className="dash__metric card card-padding animate-fadeInUp stagger-4">
                    <div className="dash__metricIcon dash__metricIcon--green"><BarChart3 size={20} /></div>
                    <div>
                      <span className="dash__metricLabel">Media Uploads</span>
                      <h3 className="dash__metricValue">{usage?.media_uploads?.used ?? 0}</h3>
                      <p className="dash__metricSub">of {usage?.media_uploads?.limit === -1 ? "unlimited" : (usage?.media_uploads?.limit ?? "—")} this cycle</p>
                    </div>
                  </div>
                </div>
              )}

              {/* Recent Projects */}
              <div className="dash__section card animate-fadeInUp stagger-5">
                <div className="dash__sectionHeader">
                  <h3>Recent Projects</h3>
                  <button className="btn btn-ghost btn-sm" onClick={() => setActiveTab("projects")}>
                    View All <ArrowUpRight size={14} />
                  </button>
                </div>

                {loading ? (
                  <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
                    <SkeletonRow /><SkeletonRow /><SkeletonRow />
                  </div>
                ) : projects.length === 0 ? (
                  <EmptyState
                    icon={FolderPlus}
                    title="No Projects Yet"
                    description="Create your first project to start uploading media and generating content."
                    action={<button className="btn btn-primary" onClick={() => setActiveTab("projects")}><Plus size={16} /> Create Project</button>}
                  />
                ) : (
                  <div className="dash__projectList">
                    {projects.slice(0, 5).map((proj, i) => (
                      <div key={proj.id} className={`dash__projectRow card-hover animate-fadeInUp stagger-${i + 1}`} onClick={() => navigate(`/projects/${proj.id}`)}>
                        <div className="dash__projectIcon"><Folder size={18} color="var(--primary)" /></div>
                        <div className="dash__projectInfo">
                          <strong>{proj.name}</strong>
                          <span><Clock size={12} /> Project</span>
                        </div>
                        <ArrowUpRight size={16} className="dash__projectArrow" />
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === "projects" && <ProjectsWorkspace />}
          {activeTab === "media" && <MediaLibrary onShowToast={showToast} />}
          {activeTab === "settings" && <SettingsWorkspace onShowToast={showToast} />}
        </main>
      </div>
    </div>
  );
}

export default Dashboard;
