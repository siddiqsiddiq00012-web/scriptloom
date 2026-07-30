import "./DashboardLayout.css";

import Sidebar from "./Sidebar";
import Topbar from "./Topbar";

function DashboardLayout({ children }) {
  return (
    <div className="dashboard-layout">
      <Sidebar />

      <div className="dashboard-content">
        <Topbar />
        {children}
      </div>
    </div>
  );
}

export default DashboardLayout;