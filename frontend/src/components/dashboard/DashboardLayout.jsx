import "./DashboardLayout.css";
import DashboardSidebar from "./DashboardSidebar";
import DashboardTopbar from "./DashboardTopbar";

export default function DashboardLayout({
  currentPage,
  setCurrentPage,
  user,
  children,
}) {
  return (
    <div className="dashboardLayout">
      <DashboardSidebar
        currentPage={currentPage}
        setCurrentPage={setCurrentPage}
      />

      <div className="dashboardLayout__content">
        <DashboardTopbar user={user} />

        <main className="dashboardLayout__page">
          {children}
        </main>
      </div>
    </div>
  );
}