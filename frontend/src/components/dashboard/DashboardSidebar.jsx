import "./DashboardSidebar.css";
import {
  LayoutDashboard,
  FolderKanban,
  Video,
  Film,
  Settings,
} from "lucide-react";

const menu = [
  {
    id: "home",
    label: "Dashboard",
    icon: LayoutDashboard,
  },
  {
    id: "projects",
    label: "Projects",
    icon: FolderKanban,
  },
  {
    id: "resources",
    label: "Resources",
    icon: Video,
  },
  {
    id: "clips",
    label: "Generated Clips",
    icon: Film,
  },
  {
    id: "settings",
    label: "Settings",
    icon: Settings,
  },
];

export default function DashboardSidebar({
  currentPage,
  setCurrentPage,
}) {
  return (
    <aside className="dashboardSidebar">
      <div className="dashboardSidebar__logo">
        <h2>Scriptloom</h2>
        <span>Content OS</span>
      </div>

      <nav className="dashboardSidebar__nav">
        {menu.map((item) => {
          const Icon = item.icon;

          return (
            <button
              key={item.id}
              className={`dashboardSidebar__item ${
                currentPage === item.id
                  ? "dashboardSidebar__item--active"
                  : ""
              }`}
              onClick={() => setCurrentPage(item.id)}
            >
              <Icon size={18} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>
    </aside>
  );
}