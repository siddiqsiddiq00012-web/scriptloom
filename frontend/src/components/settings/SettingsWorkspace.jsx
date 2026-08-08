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
  Shield,
  Monitor,
  Download,
  Camera,
  Palette,
  Globe,
} from "lucide-react";
import { getCurrentUser } from "../../api/auth";
import { updateProfile, changePassword, deleteAccount, exportAccountData } from "../../api/users";
import { api } from "../../api/client";

const PLANS = [
  { key: "starter", label: "Starter (Free)", price: "$0/mo" },
  { key: "founder_pro", label: "Founder Pro", price: "$49/mo" },
  { key: "enterprise", label: "Enterprise", price: "Custom" },
];

const TIMEZONES = [
  "UTC",
  "America/New_York",
  "America/Chicago",
  "America/Denver",
  "America/Los_Angeles",
  "America/Sao_Paulo",
  "Europe/London",
  "Europe/Paris",
  "Europe/Berlin",
  "Asia/Dubai",
  "Asia/Kolkata",
  "Asia/Singapore",
  "Asia/Tokyo",
  "Australia/Sydney",
  "Pacific/Auckland",
];

const ROLES = [
  "Founder / CEO",
  "Marketing Manager",
  "Content Creator",
  "Product Manager",
  "Developer",
  "Consultant",
  "Agency Owner",
  "Other",
];

function SettingsWorkspace({ onShowToast }) {
  const [activeSubTab, setActiveSubTab] = useState("profile");

  return (
    <div className="animate-fadeIn">
      <div className="settings__header">
        <div>
          <h2 className="settings__title">Settings</h2>
          <p className="settings__subtitle">Manage your profile, preferences, and account.</p>
        </div>
      </div>

      <div className="settings__tabs">
        <button className={`settings__tab ${activeSubTab === "profile" ? "settings__tab--active" : ""}`} onClick={() => setActiveSubTab("profile")}>
          <User size={16} /> Profile
        </button>
        <button className={`settings__tab ${activeSubTab === "preferences" ? "settings__tab--active" : ""}`} onClick={() => setActiveSubTab("preferences")}>
          <Palette size={16} /> Preferences
        </button>
        <button className={`settings__tab ${activeSubTab === "billing" ? "settings__tab--active" : ""}`} onClick={() => setActiveSubTab("billing")}>
          <CreditCard size={16} /> Billing
        </button>
        <button className={`settings__tab ${activeSubTab === "webhooks" ? "settings__tab--active" : ""}`} onClick={() => setActiveSubTab("webhooks")}>
          <Webhook size={16} /> Webhooks
        </button>
        <button className={`settings__tab ${activeSubTab === "account" ? "settings__tab--active" : ""}`} onClick={() => setActiveSubTab("account")}>
          <Shield size={16} /> Account
        </button>
      </div>

      <div className="card card-padding" style={{ marginTop: 0 }}>
        {activeSubTab === "profile" && <ProfilePane onShowToast={onShowToast} />}
        {activeSubTab === "preferences" && <PreferencesPane onShowToast={onShowToast} />}
        {activeSubTab === "billing" && <BillingPane onShowToast={onShowToast} />}
        {activeSubTab === "webhooks" && <WebhooksPane onShowToast={onShowToast} />}
        {activeSubTab === "account" && <AccountPane onShowToast={onShowToast} />}
      </div>
    </div>
  );
}

/* ── Profile ─────────────────────────────────────────────────────────── */

function ProfilePane({ onShowToast }) {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [avatarUrl, setAvatarUrl] = useState("");
  const [bio, setBio] = useState("");
  const [company, setCompany] = useState("");
  const [role, setRole] = useState("");
  const [timezone, setTimezone] = useState("");
  const [createdAt, setCreatedAt] = useState("");
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getCurrentUser()
      .then((user) => {
        if (user) {
          setName(user.name || "");
          setEmail(user.email || "");
          setAvatarUrl(user.avatar_url || "");
          setBio(user.bio || "");
          setCompany(user.company || "");
          setRole(user.role || "");
          setTimezone(user.timezone || "");
          setCreatedAt(user.created_at || "");
        }
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const handleSave = async () => {
    setSaving(true);
    try {
      const updated = await updateProfile({ name, bio, company, role, timezone });
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

  const profileCompletion = (() => {
    let filled = 0;
    let total = 5;
    if (name.trim()) filled++;
    if (bio.trim()) filled++;
    if (company.trim()) filled++;
    if (role) filled++;
    if (timezone) filled++;
    return Math.round((filled / total) * 100);
  })();

  if (loading) return <div style={{ padding: "20px", color: "#64748B" }}><Loader2 className="lucide-spin" size={18} /> Loading profile...</div>;

  return (
    <div className="settings__pane">
      <div className="profileHeader">
        <div className="profileHeader__avatar">
          {avatarUrl ? (
            <img src={avatarUrl} alt="Avatar" className="profileHeader__img" />
          ) : (
            <div className="profileHeader__placeholder">
              {name ? name.charAt(0).toUpperCase() : <User size={24} />}
            </div>
          )}
          <div className="profileHeader__info">
            <h3 className="profileHeader__name">{name || "Your Name"}</h3>
            <p className="profileHeader__email">{email}</p>
            {createdAt && (
              <p className="profileHeader__since">Member since {new Date(createdAt).toLocaleDateString("en-US", { month: "long", year: "numeric" })}</p>
            )}
          </div>
        </div>
        <div className="profileCompletion">
          <div className="profileCompletion__label">
            <span>Profile Completion</span>
            <strong>{profileCompletion}%</strong>
          </div>
          <div className="profileCompletion__track">
            <div className="profileCompletion__fill" style={{ width: `${profileCompletion}%` }} />
          </div>
        </div>
      </div>

      <h3>Personal Information</h3>

      <div className="settings__field">
        <label>Full Name</label>
        <input type="text" value={name} onChange={(e) => setName(e.target.value)} placeholder="Your full name" />
      </div>

      <div className="settings__field">
        <label>Email</label>
        <input type="email" value={email} disabled className="settings__field--disabled" />
      </div>

      <div className="settings__field">
        <label>Bio</label>
        <textarea
          value={bio}
          onChange={(e) => setBio(e.target.value)}
          placeholder="Tell us about yourself..."
          rows={3}
          maxLength={500}
        />
        <span className="settings__fieldHint">{bio.length}/500 characters</span>
      </div>

      <div className="settings__fieldRow">
        <div className="settings__field">
          <label>Company</label>
          <input type="text" value={company} onChange={(e) => setCompany(e.target.value)} placeholder="Your company" />
        </div>
        <div className="settings__field">
          <label>Role</label>
          <select value={role} onChange={(e) => setRole(e.target.value)}>
            <option value="">Select your role</option>
            {ROLES.map((r) => <option key={r} value={r}>{r}</option>)}
          </select>
        </div>
      </div>

      <div className="settings__field">
        <label>Timezone</label>
        <select value={timezone} onChange={(e) => setTimezone(e.target.value)}>
          <option value="">Select timezone</option>
          {TIMEZONES.map((tz) => <option key={tz} value={tz}>{tz.replace("_", " ")}</option>)}
        </select>
      </div>

      <button className="settings__saveBtn" onClick={handleSave} disabled={saving}>
        {saving ? <><Loader2 className="lucide-spin" size={16} /> Saving...</> : <><Save size={16} /> Save Changes</>}
      </button>
    </div>
  );
}

/* ── Preferences ─────────────────────────────────────────────────────── */

function PreferencesPane({ onShowToast }) {
  const [theme, setTheme] = useState(() => localStorage.getItem("theme") || "light");
  const [notifications, setNotifications] = useState(() => localStorage.getItem("notifications") !== "disabled");

  const handleThemeChange = (newTheme) => {
    setTheme(newTheme);
    localStorage.setItem("theme", newTheme);
    document.documentElement.setAttribute("data-theme", newTheme);
    if (onShowToast) onShowToast(`Theme changed to ${newTheme}.`);
  };

  const handleNotificationsToggle = () => {
    const newVal = !notifications;
    setNotifications(newVal);
    localStorage.setItem("notifications", newVal ? "enabled" : "disabled");
  };

  return (
    <div className="settings__pane">
      <h3>Display</h3>

      <div className="settings__field">
        <label>Theme</label>
        <div className="themeOptions">
          {["light", "dark", "system"].map((t) => (
            <button
              key={t}
              className={`themeOption ${theme === t ? "themeOption--active" : ""}`}
              onClick={() => handleThemeChange(t)}
            >
              {t === "light" && <Monitor size={16} />}
              {t === "dark" && <Palette size={16} />}
              {t === "system" && <Globe size={16} />}
              <span>{t.charAt(0).toUpperCase() + t.slice(1)}</span>
            </button>
          ))}
        </div>
      </div>

      <h3>Notifications</h3>

      <div className="settings__toggleRow">
        <div>
          <span className="settings__toggleLabel">Email Notifications</span>
          <span className="settings__toggleDesc">Receive email updates about your content generation.</span>
        </div>
        <button
          className={`settings__toggle ${notifications ? "settings__toggle--on" : ""}`}
          onClick={handleNotificationsToggle}
        >
          <div className="settings__toggleKnob" />
        </button>
      </div>
    </div>
  );
}

/* ── Account Management ──────────────────────────────────────────────── */

function AccountPane({ onShowToast }) {
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [changingPassword, setChangingPassword] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deleteConfirmText, setDeleteConfirmText] = useState("");
  const [deleting, setDeleting] = useState(false);

  const handleChangePassword = async () => {
    if (newPassword !== confirmPassword) {
      if (onShowToast) onShowToast("New passwords don't match.");
      return;
    }
    if (newPassword.length < 6) {
      if (onShowToast) onShowToast("Password must be at least 6 characters.");
      return;
    }
    setChangingPassword(true);
    try {
      await changePassword({ current_password: currentPassword, new_password: newPassword });
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
      if (onShowToast) onShowToast("Password changed successfully.");
    } catch (err) {
      if (onShowToast) onShowToast(err.message || "Failed to change password.");
    } finally {
      setChangingPassword(false);
    }
  };

  const handleExport = async () => {
    setExporting(true);
    try {
      const data = await exportAccountData();
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `scriptloom-export-${new Date().toISOString().slice(0, 10)}.json`;
      a.click();
      URL.revokeObjectURL(url);
      if (onShowToast) onShowToast("Data exported successfully.");
    } catch (err) {
      if (onShowToast) onShowToast(err.message || "Failed to export data.");
    } finally {
      setExporting(false);
    }
  };

  const handleDelete = async () => {
    setDeleting(true);
    try {
      await deleteAccount();
      localStorage.clear();
      window.location.href = "/login";
    } catch (err) {
      if (onShowToast) onShowToast(err.message || "Failed to delete account.");
      setDeleting(false);
    }
  };

  return (
    <div className="settings__pane">
      <h3>Change Password</h3>
      <div className="settings__field">
        <label>Current Password</label>
        <input type="password" value={currentPassword} onChange={(e) => setCurrentPassword(e.target.value)} placeholder="Enter current password" />
      </div>
      <div className="settings__field">
        <label>New Password</label>
        <input type="password" value={newPassword} onChange={(e) => setNewPassword(e.target.value)} placeholder="Enter new password" />
      </div>
      <div className="settings__field">
        <label>Confirm New Password</label>
        <input type="password" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} placeholder="Confirm new password" />
      </div>
      <button className="settings__saveBtn" onClick={handleChangePassword} disabled={changingPassword || !currentPassword || !newPassword}>
        {changingPassword ? <><Loader2 className="lucide-spin" size={16} /> Changing...</> : <><Shield size={16} /> Change Password</>}
      </button>

      <div className="settings__divider" />

      <h3>Export Data</h3>
      <p className="settings__sectionDesc">Download a copy of all your account data, projects, and generated content.</p>
      <button className="btn btn--outline" onClick={handleExport} disabled={exporting}>
        {exporting ? <><Loader2 className="lucide-spin" size={16} /> Exporting...</> : <><Download size={16} /> Export Account Data</>}
      </button>

      <div className="settings__divider" />

      <h3 className="settings__dangerTitle">Danger Zone</h3>
      <div className="settings__dangerZone">
        <div>
          <span className="settings__dangerLabel">Delete Account</span>
          <span className="settings__dangerDesc">Permanently delete your account and all associated data. This action cannot be undone.</span>
        </div>
        <button className="btn btn--danger" onClick={() => setShowDeleteConfirm(true)}>
          <Trash2 size={16} /> Delete Account
        </button>
      </div>

      {showDeleteConfirm && (
        <div className="settings__deleteConfirm">
          <p>Type <strong>DELETE</strong> to confirm:</p>
          <div className="settings__deleteConfirmRow">
            <input
              type="text"
              value={deleteConfirmText}
              onChange={(e) => setDeleteConfirmText(e.target.value)}
              placeholder="Type DELETE"
              className="settings__deleteInput"
            />
            <button
              className="btn btn--danger"
              onClick={handleDelete}
              disabled={deleteConfirmText !== "DELETE" || deleting}
            >
              {deleting ? <><Loader2 className="lucide-spin" size={16} /> Deleting...</> : "Confirm Delete"}
            </button>
            <button className="btn btn--outline" onClick={() => { setShowDeleteConfirm(false); setDeleteConfirmText(""); }}>
              Cancel
            </button>
          </div>
        </div>
      )}
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
    <div className="settings__pane" style={{ maxWidth: "700px" }}>
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
            className={`planBtn ${subscription?.plan_name === p.key ? "planBtn--current" : ""}`}
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
    <div className="settings__pane" style={{ maxWidth: "800px" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h3>Webhook Endpoints</h3>
        <button className="settings__saveBtn" onClick={() => setShowCreate(!showCreate)}>
          <Plus size={16} /> Add Endpoint
        </button>
      </div>

      {showCreate && (
        <div className="settings__createForm">
          <div className="settings__field">
            <label>Endpoint URL</label>
            <input type="url" placeholder="https://your-server.com/webhooks" value={newUrl} onChange={(e) => setNewUrl(e.target.value)} />
          </div>
          <div className="settings__field">
            <label>Secret (optional, min 16 chars)</label>
            <input type="text" placeholder="your-webhook-secret" value={newSecret} onChange={(e) => setNewSecret(e.target.value)} />
          </div>
          <div className="settings__formRow">
            <button className="settings__saveBtn" onClick={handleCreate}>Create</button>
            <button className="btn btn--outline" onClick={() => { setShowCreate(false); setNewUrl(""); setNewSecret(""); }}>Cancel</button>
          </div>
        </div>
      )}

      {endpoints.length === 0 ? (
        <div className="settings__empty">No webhook endpoints configured. Add one to receive event notifications.</div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
          {endpoints.map((ep) => (
            <div key={ep.id} className="settings__webhookCard">
              <div className="settings__webhookHeader">
                <div>
                  <div className="settings__webhookUrl">
                    <ExternalLink size={14} color="#4F46E5" />
                    <code>{ep.url}</code>
                  </div>
                  <span className="settings__webhookMeta">
                    Events: {(ep.subscribed_events || ["*"]).join(", ")}
                    {" · "}
                    <span style={{ color: ep.is_active ? "#10B981" : "#EF4444", fontWeight: 600 }}>
                      {ep.is_active ? "Active" : "Paused"}
                    </span>
                  </span>
                </div>
                <div className="settings__webhookActions">
                  <button className="btn btn--ghost btn--sm" onClick={() => handleToggleActive(ep)}>
                    {ep.is_active ? "Pause" : "Enable"}
                  </button>
                  <button className="btn btn--primary btn--sm" onClick={() => handleTestPing(ep.id)} disabled={testingId === ep.id}>
                    {testingId === ep.id ? "Sending..." : "Test"}
                  </button>
                  <button className="btn btn--ghost btn--sm" onClick={() => handleShowDeliveries(ep.id)}>
                    <RefreshCw size={12} /> Log
                  </button>
                  <button className="btn btn--ghost btn--sm" style={{ color: "#EF4444" }} onClick={() => handleDelete(ep.id)}>
                    <Trash2 size={14} />
                  </button>
                </div>
              </div>

              {selectedForLog === ep.id && deliveries[ep.id] && (
                <div className="settings__deliveryLog">
                  <p style={{ fontSize: "12px", fontWeight: 600, color: "#475569", marginBottom: "8px" }}>
                    Delivery Log ({deliveries[ep.id].length} entries)
                  </p>
                  {deliveries[ep.id].length === 0 ? (
                    <p style={{ fontSize: "12px", color: "#94a3b8" }}>No deliveries yet.</p>
                  ) : (
                    <div style={{ display: "flex", flexDirection: "column", gap: "6px", maxHeight: 200, overflowY: "auto" }}>
                      {deliveries[ep.id].map((d) => (
                        <div key={d.delivery_id || d.id} className="settings__deliveryItem">
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
