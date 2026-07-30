import React, { useState } from "react";
import "./UpgradeModal.css";
import { X, Crown, Check, Sparkles, Zap, ShieldCheck } from "lucide-react";

function UpgradeModal({ isOpen, onClose }) {
  const [selectedPlan, setSelectedPlan] = useState("pro"); // 'free' | 'pro' | 'enterprise'

  if (!isOpen) return null;

  return (
    <div className="upgradeModal__overlay" onClick={onClose}>
      <div className="upgradeModal__container" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="upgradeModal__header">
          <div className="upgradeModal__badge">
            <Crown size={14} className="upgradeModal__crown" />
            <span>Scriptloom Pro Workspace</span>
          </div>
          <h2>Unlock Full Operational Intelligence</h2>
          <p>Scale founder-led thought leadership without translation friction</p>
          <button className="upgradeModal__closeBtn" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        {/* Pricing Cards */}
        <div className="upgradeModal__grid">
          {/* Starter Plan */}
          <div
            className={`upgradeModal__card ${
              selectedPlan === "free" ? "upgradeModal__card--active" : ""
            }`}
            onClick={() => setSelectedPlan("free")}
          >
            <div className="upgradeModal__cardHeader">
              <h3>Starter</h3>
              <div className="upgradeModal__price">
                <span>$0</span>
                <small>/ month</small>
              </div>
            </div>
            <p className="upgradeModal__cardDesc">
              For solo creators testing spoken content extraction.
            </p>
            <ul className="upgradeModal__featuresList">
              <li><Check size={16} color="#6366F1" /> 2 Hours Ingestion / month</li>
              <li><Check size={16} color="#6366F1" /> Standard Voice DNA Calibration</li>
              <li><Check size={16} color="#6366F1" /> Camera & LinkedIn Campaign Packs</li>
            </ul>
            <button className="upgradeModal__planBtn upgradeModal__planBtn--outline">
              Current Plan
            </button>
          </div>

          {/* Pro Plan (Featured) */}
          <div
            className={`upgradeModal__card upgradeModal__card--featured ${
              selectedPlan === "pro" ? "upgradeModal__card--active" : ""
            }`}
            onClick={() => setSelectedPlan("pro")}
          >
            <div className="upgradeModal__popularBadge">MOST POPULAR</div>
            <div className="upgradeModal__cardHeader">
              <h3>Founder Pro</h3>
              <div className="upgradeModal__price">
                <span>$49</span>
                <small>/ month</small>
              </div>
            </div>
            <p className="upgradeModal__cardDesc">
              For founder-led B2B SaaS teams scaling market authority.
            </p>
            <ul className="upgradeModal__featuresList">
              <li><Check size={16} color="#4F46E5" /> <strong>Unlimited</strong> Audio & Video Ingestion</li>
              <li><Check size={16} color="#4F46E5" /> Custom Voice DNA & Jargon Filters</li>
              <li><Check size={16} color="#4F46E5" /> Persistent Brand Memory RAG Store</li>
              <li><Check size={16} color="#4F46E5" /> Substack & Carousel PDF Exports</li>
              <li><Check size={16} color="#4F46E5" /> Multi-speaker Diarization & Attribution</li>
            </ul>
            <button className="upgradeModal__planBtn upgradeModal__planBtn--primary">
              Upgrade to Founder Pro <Sparkles size={16} />
            </button>
          </div>

          {/* Enterprise */}
          <div
            className={`upgradeModal__card ${
              selectedPlan === "enterprise" ? "upgradeModal__card--active" : ""
            }`}
            onClick={() => setSelectedPlan("enterprise")}
          >
            <div className="upgradeModal__cardHeader">
              <h3>Enterprise</h3>
              <div className="upgradeModal__price">
                <span>Custom</span>
              </div>
            </div>
            <p className="upgradeModal__cardDesc">
              For executive teams with high security & dedicated API pipelines.
            </p>
            <ul className="upgradeModal__featuresList">
              <li><Check size={16} color="#6366F1" /> Dedicated Isolated Infrastructure</li>
              <li><Check size={16} color="#6366F1" /> Custom LLM & Voice Fine-tuning</li>
              <li><Check size={16} color="#6366F1" /> SSO, Audit Logs & SOC2 Compliance</li>
            </ul>
            <button className="upgradeModal__planBtn upgradeModal__planBtn--outline">
              Contact Sales
            </button>
          </div>
        </div>

        <div className="upgradeModal__footer">
          <ShieldCheck size={16} color="#64748B" />
          <span>7-day money-back guarantee • Cancel anytime with zero commitment</span>
        </div>
      </div>
    </div>
  );
}

export default UpgradeModal;
