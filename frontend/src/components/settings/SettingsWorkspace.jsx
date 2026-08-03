import React, { useState } from "react";
import "./SettingsWorkspace.css";
import {
  User,
  Shield,
  CreditCard,
  Key,
  Save,
  Check,
  Crown,
  Bell,
  Sliders,
  Database,
} from "lucide-react";

function SettingsWorkspace({ onShowToast }) {
  const [activeSubTab, setActiveSubTab] = useState("profile"); // 'profile' | 'voice_dna' | 'billing' | 'api'
  const [saving, setSaving] = useState(false);

  // Form states
  const [name, setName] = useState("Sarah Jenkins");
  const [email, setEmail] = useState("founder@scriptloom.ai");
  const [tone, setTone] = useState("Authoritative & Conviction-driven");
  const [bannedWords, setBannedWords] = useState("game-changer, synergy, paradigm shift, revolutionary, unleash, delve");
  const [exportFormat, setExportFormat] = useState("markdown");
  const [webhookUrl, setWebhookUrl] = useState("https://api.scriptloom.ai/v1/webhooks/content-ready");

  const handleSaveSettings = () => {
    setSaving(true);
    setTimeout(() => {
      setSaving(false);
      if (onShowToast) onShowToast("Settings updated successfully!");
    }, 500);
  };

  return (
    <div className="settingsWorkspace">
      <div className="settingsWorkspace__header">
        <div>
          <h2>Account & OS Workspace Settings</h2>
          <p>Manage profile, Voice DNA rules, billing subscription, and API keys</p>
        </div>

        <button className="settingsWorkspace__saveBtn" onClick={handleSaveSettings} disabled={saving}>
          {saving ? <Check size={16} /> : <Save size={16} />}
          <span>{saving ? "Saving..." : "Save Settings"}</span>
        </button>
      </div>

      {/* Sub Tabs */}
      <div className="settingsWorkspace__tabs">
        <button
          className={`settingsWorkspace__tab ${activeSubTab === "profile" ? "tab--active" : ""}`}
          onClick={() => setActiveSubTab("profile")}
        >
          <User size={16} /> Profile & Account
        </button>
        <button
          className={`settingsWorkspace__tab ${activeSubTab === "voice_dna" ? "tab--active" : ""}`}
          onClick={() => setActiveSubTab("voice_dna")}
        >
          <Sliders size={16} /> Voice DNA Rules
        </button>
        <button
          className={`settingsWorkspace__tab ${activeSubTab === "billing" ? "tab--active" : ""}`}
          onClick={() => setActiveSubTab("billing")}
        >
          <CreditCard size={16} /> Billing & Quotas
        </button>
        <button
          className={`settingsWorkspace__tab ${activeSubTab === "api" ? "tab--active" : ""}`}
          onClick={() => setActiveSubTab("api")}
        >
          <Key size={16} /> API & Export Defaults
        </button>
      </div>

      {/* Workspace Body */}
      <div className="settingsWorkspace__card">
        {activeSubTab === "profile" && (
          <div className="settingsWorkspace__pane">
            <h3>Creator Profile Details</h3>
            <div className="settingsWorkspace__field">
              <label>Full Name</label>
              <input type="text" value={name} onChange={(e) => setName(e.target.value)} />
            </div>

            <div className="settingsWorkspace__field">
              <label>Work Email Address</label>
              <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
            </div>
          </div>
        )}

        {activeSubTab === "voice_dna" && (
          <div className="settingsWorkspace__pane">
            <h3>Voice DNA & Jargon Filters</h3>
            <div className="settingsWorkspace__field">
              <label>Default Tone of Voice</label>
              <select value={tone} onChange={(e) => setTone(e.target.value)}>
                <option value="Authoritative & Conviction-driven">Authoritative & Conviction-driven</option>
                <option value="Direct & Tactical Founder">Direct & Tactical Founder</option>
                <option value="Executive Thought Leadership">Executive Thought Leadership</option>
              </select>
            </div>

            <div className="settingsWorkspace__field">
              <label>Banned Jargon Words (Zero-Slop Enforcement)</label>
              <textarea
                rows={4}
                value={bannedWords}
                onChange={(e) => setBannedWords(e.target.value)}
              />
            </div>
          </div>
        )}

        {activeSubTab === "billing" && (
          <div className="settingsWorkspace__pane">
            <div className="settingsWorkspace__planCard">
              <Crown size={24} color="#F59E0B" />
              <div>
                <h4>Active Plan: Founder Pro ($49/month)</h4>
                <p>50 hours processing limit • Unlimited Campaign Packs • RAG Vector Store</p>
              </div>
            </div>

            <div className="settingsWorkspace__usageBar">
              <div className="settingsWorkspace__usageInfo">
                <span>Monthly Audio Processing Used</span>
                <strong>14.2 / 50.0 hours</strong>
              </div>
              <div className="settingsWorkspace__track">
                <div className="settingsWorkspace__fill" style={{ width: "28.4%" }} />
              </div>
            </div>
          </div>
        )}

        {activeSubTab === "api" && (
          <div className="settingsWorkspace__pane">
            <h3>API Keys & Export Preferences</h3>
            <div className="settingsWorkspace__field">
              <label>Default File Export Format</label>
              <select value={exportFormat} onChange={(e) => setExportFormat(e.target.value)}>
                <option value="markdown">Markdown (.md)</option>
                <option value="txt">Plain Text (.txt)</option>
                <option value="json">Structured JSON (.json)</option>
              </select>
            </div>

            <div className="settingsWorkspace__field">
              <label>Webhook URL (Content Generation Complete Signal)</label>
              <input
                type="text"
                value={webhookUrl}
                onChange={(e) => setWebhookUrl(e.target.value)}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default SettingsWorkspace;
