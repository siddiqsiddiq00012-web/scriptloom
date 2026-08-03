import React, { useState } from "react";
import { Link } from "react-router-dom";
import "./Hero.css";
import Navbar from "./Navbar";
import DemoModal from "../modals/DemoModal";
import UploadModal from "../modals/UploadModal";
import UpgradeModal from "../modals/UpgradeModal";
import { ArrowRight, Play, CheckCircle2, Zap, Target, Sparkles } from "lucide-react";

function Hero() {
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [activeTab, setActiveTab] = useState("dashboard");

  // Modals state
  const [isDemoOpen, setIsDemoOpen] = useState(false);
  const [isUploadOpen, setIsUploadOpen] = useState(false);
  const [isUpgradeOpen, setIsUpgradeOpen] = useState(false);

  return (
    <div className="heroLayout">
      {/* Background Soft Glow Halos */}
      <div className="heroLayout__glows">
        <div className="heroLayout__glow heroLayout__glow--purple" />
        <div className="heroLayout__glow heroLayout__glow--blue" />
        <div className="heroLayout__glow heroLayout__glow--cyan" />
      </div>

      <Navbar onToggleDrawer={() => setIsDrawerOpen(!isDrawerOpen)} />

      <section className="hero">
        <div className={`hero__mainGrid ${!isDrawerOpen ? "hero__mainGrid--fullWidth" : ""}`}>
          {/* Left / Center Main Content */}
          <div className="hero__centerContent">
            {/* Top AI Badge */}
            <div className="hero__badge" onClick={() => setIsDemoOpen(true)}>
              <Sparkles size={14} className="hero__badgeIcon" />
              <span>🚀 #1 Content OS for Creators & Personal Brands</span>
            </div>

            {/* Main Headline */}
            <h1 className="hero__title">
              Turn Any Idea or Recording into a
              <br />
              <span className="hero__titleHighlight">Multi-Platform Content Empire.</span>
            </h1>

            {/* Subtitle */}
            <p className="hero__subtitle">
              Scriptloom generates viral LinkedIn Carousels, X Threads, Substack Newsletters, and Short-Form Video Scripts from your voice, text notes, or videos — perfectly aligned with your authentic brand voice.
            </p>

            {/* Action Buttons */}
            <div className="hero__actions">
              <Link
                to="/dashboard"
                className="hero__btnPrimary"
                style={{ textDecoration: "none" }}
              >
                <span>Launch Content Studio</span>
                <ArrowRight size={18} />
              </Link>

              <button
                className="hero__btnSecondary"
                onClick={() => setIsUploadOpen(true)}
              >
                <span>Create Campaign Pack</span>
              </button>

              <button
                className="hero__btnSecondary"
                onClick={() => setIsDemoOpen(true)}
              >
                <div className="hero__playCircle">
                  <Play size={14} className="hero__playIcon" />
                </div>
                <span>Watch Product Tour</span>
              </button>
            </div>

            {/* Trust Benefits */}
            <div className="hero__benefits">
              <div className="hero__benefitItem" onClick={() => setIsUploadOpen(true)}>
                <CheckCircle2 size={16} className="hero__checkIcon" />
                <span>LinkedIn, X, Substack & Reels Ready</span>
              </div>

              <div className="hero__benefitItem" onClick={() => setIsUploadOpen(true)}>
                <CheckCircle2 size={16} className="hero__checkIcon" />
                <span>Personal Brand Voice Guard</span>
              </div>

              <div className="hero__benefitItem" onClick={() => setIsUploadOpen(true)}>
                <CheckCircle2 size={16} className="hero__checkIcon" />
                <span>1-Click Multi-Asset Generator</span>
              </div>
            </div>

            {/* 3 Feature Cards Grid */}
            <div className="hero__featureGrid">
              <div className="hero__featureCard" onClick={() => setIsUploadOpen(true)}>
                <div className="hero__featureIconBox hero__featureIconBox--purple">
                  <Zap size={20} />
                </div>
                <h3 className="hero__featureTitle">Save Time</h3>
                <p className="hero__featureDesc">
                  Automate content repurposing and focus on creating.
                </p>
              </div>

              <div className="hero__featureCard" onClick={() => setIsUploadOpen(true)}>
                <div className="hero__featureIconBox hero__featureIconBox--pink">
                  <Target size={20} />
                </div>
                <h3 className="hero__featureTitle">Reach More</h3>
                <p className="hero__featureDesc">
                  Get discovered across all major platforms effortlessly.
                </p>
              </div>

              <div className="hero__featureCard" onClick={() => setIsDemoOpen(true)}>
                <div className="hero__featureIconBox hero__featureIconBox--cyan">
                  <Sparkles size={20} />
                </div>
                <h3 className="hero__featureTitle">Grow Faster</h3>
                <p className="hero__featureDesc">
                  Consistent content. Maximum impact. Zero extra effort.
                </p>
              </div>
            </div>

            {/* Social Proof Bar */}
            <div className="hero__socialProof">
              <p className="hero__socialProofText">
                Trusted by creators and teams worldwide
              </p>
              <div className="hero__avatarBar" onClick={() => setIsUpgradeOpen(true)}>
                <div className="hero__avatarStack">
                  <img
                    src="https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=80&q=80"
                    alt="User 1"
                    className="hero__avatarImg"
                  />
                  <img
                    src="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=80&q=80"
                    alt="User 2"
                    className="hero__avatarImg"
                  />
                  <img
                    src="https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=80&q=80"
                    alt="User 3"
                    className="hero__avatarImg"
                  />
                  <img
                    src="https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=80&q=80"
                    alt="User 4"
                    className="hero__avatarImg"
                  />
                </div>
                <div className="hero__badgeUsers">2K+</div>
                <span className="hero__usersText">Happy users</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Interactive Modals */}
      <DemoModal
        isOpen={isDemoOpen}
        onClose={() => setIsDemoOpen(false)}
        onOpenUpload={() => setIsUploadOpen(true)}
      />

      <UploadModal
        isOpen={isUploadOpen}
        onClose={() => setIsUploadOpen(false)}
      />

      <UpgradeModal
        isOpen={isUpgradeOpen}
        onClose={() => setIsUpgradeOpen(false)}
      />
    </div>
  );
}

export default Hero;