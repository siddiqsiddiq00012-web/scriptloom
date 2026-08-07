import { useState, useEffect, useCallback } from "react";
import "./SettingsWorkspace.css";
import {
  User,
  CreditCard,
  Webhook,
  Save,
  Check,
  Crown,
  Plus,
  Trash2,
  RefreshCw,
  ExternalLink,
  CheckCircle2,
  AlertCircle,
  Loader2,
} from "lucide-react";
import { getCurrentUser } from "../../api/auth";
import { updateProfile } from "../../api/users";
import { api } from "../../api/client";

const PLANS = [
  { key: "starter", label: "Starter (Free)", price: "$0/mo" },
  { key: "founder_pro", label: "Founder Pro", price: "$49/mo" },
  { key: "enterprise", label: "Enterprise", price: "Custom" },
];

function SettingsWorkspace({ onShowToast }) {
  const [activeSubTab, setActiveSubTab] = useState("profile");

  return (
    <div className="animate-fadeIn">
      <div className="settings__header">
        <div>
          <h2 className="settings__title">Settings</h2>
          <p className="settings__subtitle">Manage your profile, billing, and webhooks.</p>
        </div>
      </div>

      <div className="settings__tabs">
        <button className={`settings__tab ${activeSubTab === "profile" ? "settings__tab--active" : ""}`} onClick={() => setActiveSubTab("profile")}>
          <User size={16} /> Profile
        </button>
        <button className={`settings__tab ${activeSubTab === "billing" ? "settings__tab--active" : ""}`} onClick={() => setActiveSubTab("billing")}>
          <CreditCard size={16} /> Billing
        </button>
        <button className={`settings__tab ${activeSubTab === "webhooks" ? "settings__tab--active" : ""}`} onClick={() => setActiveSubTab("webhooks")}>
          <Webhook size={16} /> Webhooks
        </button>
      </div>

      <div className="card card-padding" style={{ marginTop: 0 }}>
        {activeSubTab === "profile" && <ProfilePane onShowToast={onShowToast} />}
        {activeSubTab === "billing" && <BillingPane onShowToast={onShowToast} />}
        {activeSubTab === "webhooks" && <WebhooksPane onShowToast={onShowToast} />}
      </div>
    </div>
  );
}

/* ── Profile ─────────────────────────────────────────────────────────── */

function ProfilePane({ onShowToast }) {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [avatarUrl, setAvatarUrl] = useState("");
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getCurrentUser()
      .then((user) => {
        if (user) {
          setName(user.name || "");
          setEmail(user.email || "");
          setAvatarUrl(user.avatar_url || "");
        }
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const handleSave = async () => {
    setSaving(true);
    try {
      const updated = await updateProfile({ name });
      if (updated) {
        if (updated.name) localStorage.setItem("user_name", updated.name);
        if (updated.avatar_url) localStorage.setItem("user_avatar", updated.avatar_url);
      }
      if (onShowToast) onShowToast("Profile updated.");
    } catch (err) {
      if (onShowToast) onShowToast(err.message || "Failed to update profile.");
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div style={{ padding: "20px", color: "#64748B" }}><Loader2 className="lucide-spin" size={18} /> Loading profile...</div>;

  return (
    <div className="settings__pane">
      <h3>Profile</h3>
      <div className="settingsWorkspace__field">
        <label>Name</label>
        <input type="text" value={name} onChange={(e) => setName(e.target.value)} />
      </div>
      <div className="settingsWorkspace__field">
        <label>Email</label>
        <input type="email" value={email} disabled style={{ background: "#F1F5F9", color: "#94a3b8" }} />
      </div>
      {avatarUrl && (
        <div className="settingsWorkspace__field">
          <label>Avatar</label>
          <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
            <img src={avatarUrl} alt="Avatar" style={{ width: 48, height: 48, borderRadius: "50%", objectFit: "cover" }} />
            <span style={{ fontSize: "13px", color: "#64748B" }}>Loaded from your account.</span>
          </div>
        </div>
      )}
      <button className="btn btn-primary" onClick={handleSave} disabled={saving}>
        {saving ? <Check size={16} /> : <Save size={16} />}
        {saving ? "Saving..." : "Save Changes"}
      </button>
    </div>
  );
}

/* ── Billing ─────────────────────────────────────────────────────────── */

function BillingPane({ onShowToast }) {
  const [subscription, setSubscription] = useState(null);
  const [usage, setUsage] = useState(null);
  const [upgrading, setUpgrading] = useState(false);
  const [loading, setLoading] = useState(true);

  const loadData = useCallback(() => {
    Promise.all([
      api.get("/billing/subscription"),
      api.get("/billing/usage"),
    ])
      .then(([sub, useg]) => {
        setSubscription(sub);
        setUsage(useg);
      })
      .catch(() => {
        if (onShowToast) onShowToast("Failed to load billing information.");
      })
      .finally(() => setLoading(false));
  }, [onShowToast]);

  useEffect(() => { loadData(); }, [loadData]);

  const handleUpgrade = async (planKey) => {
    setUpgrading(true);
    try {
      await api.post("/billing/upgrade", { plan_name: planKey });
      if (onShowToast) onShowToast("Plan updated.");
      await loadData();
    } catch (err) {
      if (onShowToast) onShowToast(err.message || "Failed to upgrade plan.");
    } finally {
      setUpgrading(false);
    }
  };

  if (loading) return <div style={{ padding: "20px", color: "#64748B" }}><Loader2 className="lucide-spin" size={18} /> Loading billing...</div>;

  return (
    <div className="settingsWorkspace__pane" style={{ maxWidth: "700px" }}>
      <h3>Current Plan</h3>
      {subscription && (
        <div className="settingsWorkspace__planCard">
          <Crown size={24} color="#F59E0B" />
          <div>
            <h4>{subscription.plan_display_name || subscription.plan_name}</h4>
            <p>Status: {subscription.status}</p>
          </div>
        </div>
      )}

      {usage && (
        <>
          <h3 style={{ marginTop: "12px" }}>Usage This Period</h3>
          <div className="settingsWorkspace__usageBar">
            <div className="settingsWorkspace__usageInfo">
              <span>Processing</span>
              <strong>{usage.hours_processed ?? 0} / {usage.hours_limit ?? 0} hours</strong>
            </div>
            <div className="settingsWorkspace__track">
              <div className="settingsWorkspace__fill" style={{
                width: `${usage.hours_limit ? Math.min(100, (usage.hours_processed / usage.hours_limit) * 100) : 0}%`
              }} />
            </div>
          </div>
          <div className="settingsWorkspace__usageBar">
            <div className="settingsWorkspace__usageInfo">
              <span>Content Packs</span>
              <strong>{usage.campaign_packs_generated ?? 0} / {usage.campaign_packs_limit ?? 0}</strong>
            </div>
            <div className="settingsWorkspace__track">
              <div className="settingsWorkspace__fill" style={{
                width: `${usage.campaign_packs_limit ? Math.min(100, (usage.campaign_packs_generated / usage.campaign_packs_limit) * 100) : 0}%`,
                background: "#8B5CF6",
              }} />
            </div>
          </div>
          {usage.period_month && (
            <p style={{ fontSize: "12px", color: "#94a3b8" }}>Billing period: {usage.period_month}</p>
          )}
        </>
      )}

      <h3 style={{ marginTop: "12px" }}>Change Plan</h3>
      <div style={{ display: "flex", gap: "10px", flexWrap: "wrap" }}>
        {PLANS.map((p) => (
          <button
            key={p.key}
            onClick={() => handleUpgrade(p.key)}
            disabled={upgrading || subscription?.plan_name === p.key}
            style={{
              padding: "10px 16px",
              border: `1px solid ${subscription?.plan_name === p.key ? "#4F46E5" : "#E2E8F0"}`,
              borderRadius: "10px",
              background: subscription?.plan_name === p.key ? "#EEF2FF" : "#FFFFFF",
              fontSize: "13px",
              fontWeight: 600,
              cursor: subscription?.plan_name === p.key ? "default" : "pointer",
              color: subscription?.plan_name === p.key ? "#4F46E5" : "#334155",
            }}
          >
            {p.label} · {p.price}
            {subscription?.plan_name === p.key && " (current)"}
          </button>
        ))}
      </div>
    </div>
  );
}

/* ── Webhooks ─────────────────────────────────────────────────────────── */

function WebhooksPane({ onShowToast }) {
  const [endpoints, setEndpoints] = useState([]);
  const [deliveries, setDeliveries] = useState({});
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [newUrl, setNewUrl] = useState("");
  const [newSecret, setNewSecret] = useState("");
  const [selectedForLog, setSelectedForLog] = useState(null);
  const [testingId, setTestingId] = useState(null);

  const loadEndpoints = useCallback(() => {
    api.get("/webhooks/endpoints")
      .then((data) => setEndpoints(Array.isArray(data) ? data : []))
      .catch(() => {
        if (onShowToast) onShowToast("Failed to load webhook endpoints.");
      })
      .finally(() => setLoading(false));
  }, [onShowToast]);

  useEffect(() => { loadEndpoints(); }, [loadEndpoints]);

  const handleCreate = async () => {
    if (!newUrl.trim()) return;
    try {
      await api.post("/webhooks/endpoints", { url: newUrl.trim(), secret: newSecret || undefined, subscribed_events: ["*"] });
      if (onShowToast) onShowToast("Endpoint created.");
      setNewUrl(""); setNewSecret(""); setShowCreate(false);
      await loadEndpoints();
    } catch (err) {
      if (onShowToast) onShowToast(err.message || "Failed to create endpoint.");
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Delete this webhook endpoint?")) return;
    try {
      await api.delete(`/webhooks/endpoints/${id}`);
      setEndpoints((prev) => prev.filter((ep) => ep.id !== id));
      if (onShowToast) onShowToast("Endpoint deleted.");
    } catch (err) {
      if (onShowToast) onShowToast(err.message || "Failed to delete endpoint.");
    }
  };

  const handleToggleActive = async (ep) => {
    try {
      await api.put(`/webhooks/endpoints/${ep.id}`, { is_active: !ep.is_active });
      setEndpoints((prev) => prev.map((e) => e.id === ep.id ? { ...e, is_active: !e.is_active } : e));
    } catch (err) {
      if (onShowToast) onShowToast(err.message || "Failed to update endpoint.");
    }
  };

  const handleTestPing = async (epId) => {
    setTestingId(epId);
    try {
      const res = await api.post(`/webhooks/endpoints/${epId}/test`);
      if (onShowToast) onShowToast(res.message || "Test ping queued.");
    } catch (err) {
      if (onShowToast) onShowToast(err.message || "Test ping failed.");
    } finally {
      setTestingId(null);
    }
  };

  const handleShowDeliveries = async (epId) => {
    if (selectedForLog === epId) {
      setSelectedForLog(null);
      return;
    }
    try {
      const data = await api.get(`/webhooks/endpoints/${epId}/deliveries`);
      setDeliveries((prev) => ({ ...prev, [epId]: Array.isArray(data) ? data : [] }));
      setSelectedForLog(epId);
    } catch (err) {
      if (onShowToast) onShowToast(err.message || "Failed to load deliveries.");
    }
  };

  if (loading) return <div style={{ padding: "20px", color: "#64748B" }}><Loader2 className="lucide-spin" size={18} /> Loading webhooks...</div>;

  return (
    <div className="settingsWorkspace__pane" style={{ maxWidth: "800px" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h3>Webhook Endpoints</h3>
        <button
          className="settingsWorkspace__saveBtn"
          onClick={() => setShowCreate(!showCreate)}
        >
          <Plus size={16} /> Add Endpoint
        </button>
      </div>

      {showCreate && (
        <div style={{ background: "#f8fafc", border: "1px solid #e2e8f0", borderRadius: "12px", padding: "16px", display: "flex", flexDirection: "column", gap: "12px" }}>
          <div className="settingsWorkspace__field">
            <label>Endpoint URL</label>
            <input type="url" placeholder="https://your-server.com/webhooks" value={newUrl} onChange={(e) => setNewUrl(e.target.value)} />
          </div>
          <div className="settingsWorkspace__field">
            <label>Secret (optional, min 16 chars)</label>
            <input type="text" placeholder="your-webhook-secret" value={newSecret} onChange={(e) => setNewSecret(e.target.value)} />
          </div>
          <div style={{ display: "flex", gap: "8px" }}>
            <button className="settingsWorkspace__saveBtn" onClick={handleCreate}>Create</button>
            <button
              onClick={() => { setShowCreate(false); setNewUrl(""); setNewSecret(""); }}
              style={{ padding: "10px 16px", border: "1px solid #E2E8F0", borderRadius: "10px", fontSize: "13px", fontWeight: 600, background: "#fff", cursor: "pointer" }}
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {endpoints.length === 0 ? (
        <div style={{ padding: "30px", textAlign: "center", color: "#64748B" }}>
          No webhook endpoints configured. Add one to receive event notifications.
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
          {endpoints.map((ep) => (
            <div key={ep.id} style={{ background: "#f8fafc", border: "1px solid #e2e8f0", borderRadius: "12px", padding: "16px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "8px" }}>
                <div>
                  <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "4px" }}>
                    <ExternalLink size={14} color="#4F46E5" />
                    <code style={{ fontSize: "13px", fontWeight: 600 }}>{ep.url}</code>
                  </div>
                  <span style={{ fontSize: "12px", color: "#64748B" }}>
                    Events: {(ep.subscribed_events || ["*"]).join(", ")}
                    {" · "}
                    <span style={{ color: ep.is_active ? "#10B981" : "#EF4444", fontWeight: 600 }}>
                      {ep.is_active ? "Active" : "Paused"}
                    </span>
                  </span>
                </div>
                <div style={{ display: "flex", gap: "6px" }}>
                  <button onClick={() => handleToggleActive(ep)} style={{ padding: "6px 10px", border: "1px solid #E2E8F0", borderRadius: "8px", fontSize: "12px", fontWeight: 600, cursor: "pointer", background: "#fff" }}>
                    {ep.is_active ? "Pause" : "Enable"}
                  </button>
                  <button onClick={() => handleTestPing(ep.id)} disabled={testingId === ep.id} style={{ padding: "6px 10px", border: "1px solid #E2E8F0", borderRadius: "8px", fontSize: "12px", fontWeight: 600, cursor: "pointer", background: "#EEF2FF", color: "#4F46E5" }}>
                    {testingId === ep.id ? "Sending..." : "Test"}
                  </button>
                  <button onClick={() => handleShowDeliveries(ep.id)} style={{ padding: "6px 10px", border: "1px solid #E2E8F0", borderRadius: "8px", fontSize: "12px", fontWeight: 600, cursor: "pointer", background: "#fff" }}>
                    <RefreshCw size={12} /> Log
                  </button>
                  <button onClick={() => handleDelete(ep.id)} style={{ padding: "6px", border: "1px solid #FCA5A5", borderRadius: "8px", background: "#FEF2F2", color: "#EF4444", cursor: "pointer" }}>
                    <Trash2 size={14} />
                  </button>
                </div>
              </div>

              {selectedForLog === ep.id && deliveries[ep.id] && (
                <div style={{ marginTop: "12px", borderTop: "1px solid #E2E8F0", paddingTop: "12px" }}>
                  <p style={{ fontSize: "12px", fontWeight: 600, color: "#475569", marginBottom: "8px" }}>
                    Delivery Log ({deliveries[ep.id].length} entries)
                  </p>
                  {deliveries[ep.id].length === 0 ? (
                    <p style={{ fontSize: "12px", color: "#94a3b8" }}>No deliveries yet.</p>
                  ) : (
                    <div style={{ display: "flex", flexDirection: "column", gap: "6px", maxHeight: 200, overflowY: "auto" }}>
                      {deliveries[ep.id].map((d) => (
                        <div key={d.delivery_id || d.id} style={{ display: "flex", alignItems: "center", gap: "8px", fontSize: "12px", padding: "6px 10px", background: "#fff", borderRadius: "8px", border: "1px solid #e2e8f0" }}>
                          {d.status === "delivered" || d.status === "SUCCESS" ? (
                            <CheckCircle2 size={14} color="#10B981" />
                          ) : (
                            <AlertCircle size={14} color="#EF4444" />
                          )}
                          <span style={{ fontWeight: 600, minWidth: 100 }}>{d.event_type}</span>
                          <span style={{ color: "#64748B" }}>{d.response_status || "—"}</span>
                          {d.failure_reason && <span style={{ color: "#EF4444" }}>{d.failure_reason}</span>}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default SettingsWorkspace;
