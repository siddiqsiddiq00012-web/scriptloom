import React from "react";
import "./AppDrawer.css";
import {
  X,
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
} from "lucide-react";

function AppDrawer({ isOpen, onClose, activeTab, setActiveTab, onOpenUpgrade }) {
  const menuItems = [
    { id: "dashboard", label: "Dashboard", icon: Home },
    { id: "projects", label: "Projects", icon: Folder },
    { id: "upload", label: "Upload Center", icon: UploadCloud },
    { id: "studio", label: "Content Studio", icon: PenTool },
    { id: "ai", label: "AI Workspace", icon: Sparkles },
    { id: "media", label: "Media Library", icon: Image },
    { id: "publishing", label: "Publishing", icon: Send },
    { id: "analytics", label: "Analytics", icon: BarChart2 },
    { id: "settings", label: "Settings", icon: Settings },
  ];

  return (
    <aside className={`appDrawer ${isOpen ? "appDrawer--open" : ""}`}>
      <div className="appDrawer__content">
        {/* Header */}
        <div className="appDrawer__header">
          <div className="appDrawer__brand">
            <div className="appDrawer__avatar">S</div>
            <div className="appDrawer__brandInfo">
              <h4 className="appDrawer__title">Scriptloom</h4>
              <p className="appDrawer__subtitle">AI Content OS</p>
            </div>
          </div>

          <button
            className="appDrawer__closeBtn"
            onClick={onClose}
            aria-label="Close navigation"
          >
            <X size={18} />
          </button>
        </div>

        {/* Menu Items */}
        <nav className="appDrawer__nav">
          {menuItems.map((item) => {
            const IconComponent = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                className={`appDrawer__navItem ${
                  isActive ? "appDrawer__navItem--active" : ""
                }`}
                onClick={() => {
                  if (setActiveTab) setActiveTab(item.id);
                }}
              >
                <IconComponent size={18} className="appDrawer__navIcon" />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>

        {/* Upgrade Box */}
        <div className="appDrawer__upgradeCard">
          <div className="appDrawer__upgradeHeader">
            <Crown size={18} className="appDrawer__crownIcon" />
            <span>Upgrade to Pro</span>
          </div>
          <p className="appDrawer__upgradeText">
            Unlock all features and boost your content workflow.
          </p>
          <button className="appDrawer__upgradeBtn" onClick={onOpenUpgrade}>
            Upgrade Now
          </button>
        </div>
      </div>
    </aside>
  );
}

export default AppDrawer;
