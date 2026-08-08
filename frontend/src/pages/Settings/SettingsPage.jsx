import { useCallback, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ArrowLeft } from "lucide-react";
import SettingsWorkspace from "../../components/settings/SettingsWorkspace";

export default function SettingsPage({ onShowToast }) {
  const navigate = useNavigate();
  const [toastMessage, setToastMessage] = useState("");

  const showToast = useCallback((msg) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(""), 3000);
  }, []);

  const effectiveToast = onShowToast || showToast;

  return (
    <div style={{ minHeight: "100vh", background: "var(--bg-main)" }}>
      {toastMessage && <div className="toast">{toastMessage}</div>}
      <div style={{ padding: "16px 24px", borderBottom: "1px solid var(--border-default)", background: "var(--bg-card)" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "12px", maxWidth: "960px", margin: "0 auto" }}>
          <Link to="/dashboard" style={{ display: "flex", alignItems: "center", gap: "4px", color: "var(--text-muted)", textDecoration: "none", fontSize: "13px", fontWeight: 600 }}>
            <ArrowLeft size={15} /> Dashboard
          </Link>
        </div>
      </div>
      <div style={{ maxWidth: "960px", margin: "0 auto", padding: "24px" }}>
        <SettingsWorkspace onShowToast={effectiveToast} />
      </div>
    </div>
  );
}
