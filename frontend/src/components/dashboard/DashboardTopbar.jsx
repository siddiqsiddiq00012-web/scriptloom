import "./DashboardTopbar.css";
import { Bell, Search, Plus } from "lucide-react";

export default function DashboardTopbar({ user }) {
  return (
    <header className="dashboardTopbar">

      <div className="dashboardTopbar__left">
        <h1>Scriptloom</h1>
        <p>Repurpose long-form content into viral short-form assets.</p>
      </div>

      <div className="dashboardTopbar__center">

        <div className="dashboardTopbar__search">
          <Search size={18} />
          <input
            placeholder="Search projects..."
          />
        </div>

      </div>

      <div className="dashboardTopbar__right">

        <button className="dashboardTopbar__newProject">
          <Plus size={18}/>
          New Project
        </button>

        <button className="dashboardTopbar__notification">
          <Bell size={18}/>
        </button>

        <div className="dashboardTopbar__user">

          <div className="dashboardTopbar__avatar">
            {user?.name?.charAt(0)?.toUpperCase() || "U"}
          </div>

          <div>
            <strong>{user?.name || "User"}</strong>

            <span>
              {user?.email || ""}
            </span>
          </div>

        </div>

      </div>

    </header>
  );
}