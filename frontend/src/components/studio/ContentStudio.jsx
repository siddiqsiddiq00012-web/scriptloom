import React, { useState } from "react";
import "./ContentStudio.css";
import {
  Sparkles,
  BookOpen,
  Send,
  Video,
  Copy,
  Check,
  Download,
  AlertTriangle,
  Save,
  CheckCircle2,
} from "lucide-react";

function ContentStudio({ onShowToast }) {
  const [activeTab, setActiveTab] = useState("carousel");
  const [copied, setCopied] = useState(false);
  const [saving, setSaving] = useState(false);

  // Editable Content States
  const [carouselSlideText, setCarouselSlideText] = useState(
    "Spoken webinars contain 10x more positioning clarity than formal docs."
  );
  const [newsletterText, setNewsletterText] = useState(
    `# The End of Commodity Marketing\n\nDear Reader,\n\nThis week on our strategy call, we unpacked why B2B buyers ignore generic AI copy.\n\nSoftware buyers don't buy features—they buy proof of domain authority.\n\nBest,\nFounder & CEO`
  );
  const [scriptText, setScriptText] = useState(
    `"Stop converting B2B buyers with generic AI slop. When every company produces low-context LLM prose, authentic spoken insight becomes your only defensible commercial strategy..."`
  );

  const bannedJargon = ["game-changer", "synergy", "paradigm shift", "revolutionary", "unleash", "delve"];

  const checkBannedJargon = (text) => {
    const found = [];
    const lower = text.toLowerCase();
    for (const word of bannedJargon) {
      if (lower.includes(word)) {
        found.push(word);
      }
    }
    return found;
  };

  const currentBanned = checkBannedJargon(
    activeTab === "carousel"
      ? carouselSlideText
      : activeTab === "newsletter"
      ? newsletterText
      : scriptText
  );

  const handleCopy = (text) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    if (onShowToast) onShowToast("Copied to clipboard!");
    setTimeout(() => setCopied(false), 2000);
  };

  const handleSave = () => {
    setSaving(true);
    setTimeout(() => {
      setSaving(false);
      if (onShowToast) onShowToast("Saved changes to live campaign pack!");
    }, 600);
  };

  return (
    <div className="contentStudio">
      {/* Top Banner */}
      <div className="contentStudio__header">
        <div>
          <h2>Content Studio & Zero-Slop Refiner</h2>
          <p>Fine-tune multi-platform assets with real-time Voice DNA compliance</p>
        </div>

        <div className="contentStudio__headerActions">
          <button className="contentStudio__saveBtn" onClick={handleSave} disabled={saving}>
            {saving ? <CheckCircle2 size={16} /> : <Save size={16} />}
            <span>{saving ? "Saving..." : "Save Asset"}</span>
          </button>
        </div>
      </div>

      {/* Voice DNA Compliance Banner */}
      {currentBanned.length > 0 ? (
        <div className="contentStudio__warningBanner">
          <AlertTriangle size={18} color="#EF4444" />
          <span>
            <strong>Voice DNA Violation Detected:</strong> Banned jargon word(s) found:{" "}
            {currentBanned.map((w) => `"${w}"`).join(", ")}. Please rephrase to preserve authentic authority.
          </span>
        </div>
      ) : (
        <div className="contentStudio__successBanner">
          <Sparkles size={18} color="#10B981" />
          <span>
            <strong>Voice DNA Compliant:</strong> 100% Zero-Slop verified. No banned jargon detected.
          </span>
        </div>
      )}

      {/* Asset Tabs */}
      <div className="contentStudio__tabs">
        <button
          className={`contentStudio__tab ${activeTab === "carousel" ? "contentStudio__tab--active" : ""}`}
          onClick={() => setActiveTab("carousel")}
        >
          <BookOpen size={16} /> LinkedIn Carousel
        </button>
        <button
          className={`contentStudio__tab ${activeTab === "script" ? "contentStudio__tab--active" : ""}`}
          onClick={() => setActiveTab("script")}
        >
          <Video size={16} /> Camera Script
        </button>
        <button
          className={`contentStudio__tab ${activeTab === "newsletter" ? "contentStudio__tab--active" : ""}`}
          onClick={() => setActiveTab("newsletter")}
        >
          <Send size={16} /> Substack Newsletter
        </button>
      </div>

      {/* Workspace Editor */}
      <div className="contentStudio__editorBox">
        {activeTab === "carousel" && (
          <div className="contentStudio__pane">
            <label className="contentStudio__label">Slide 1 Body Text (Live Editor)</label>
            <textarea
              className="contentStudio__textarea"
              value={carouselSlideText}
              onChange={(e) => setCarouselSlideText(e.target.value)}
              rows={4}
            />
            <div className="contentStudio__previewCard">
              <span className="contentStudio__slideTag">SLIDE 1 • THE TRADITIONAL GAP</span>
              <h3>Conversations Contain More Value Than Documents</h3>
              <p>{carouselSlideText}</p>
            </div>
          </div>
        )}

        {activeTab === "script" && (
          <div className="contentStudio__pane">
            <label className="contentStudio__label">Teleprompter Script & Visual Cues</label>
            <textarea
              className="contentStudio__textarea"
              value={scriptText}
              onChange={(e) => setScriptText(e.target.value)}
              rows={8}
            />
          </div>
        )}

        {activeTab === "newsletter" && (
          <div className="contentStudio__pane">
            <label className="contentStudio__label">Markdown Newsletter Draft</label>
            <textarea
              className="contentStudio__textarea"
              value={newsletterText}
              onChange={(e) => setNewsletterText(e.target.value)}
              rows={10}
            />
          </div>
        )}

        <div className="contentStudio__actions">
          <button
            className="contentStudio__copyBtn"
            onClick={() =>
              handleCopy(
                activeTab === "carousel"
                  ? carouselSlideText
                  : activeTab === "newsletter"
                  ? newsletterText
                  : scriptText
              )
            }
          >
            {copied ? <Check size={16} /> : <Copy size={16} />}
            <span>{copied ? "Copied!" : "Copy Asset"}</span>
          </button>
        </div>
      </div>
    </div>
  );
}

export default ContentStudio;
