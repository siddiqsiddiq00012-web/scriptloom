import { Link } from "react-router-dom";
import "./Hero.css";
import Navbar from "./Navbar";
import { ArrowRight, CheckCircle2, UploadCloud, Film, FileText, Sparkles } from "lucide-react";

function Hero() {
  return (
    <div className="heroLayout">
      <div className="heroLayout__glows">
        <div className="heroLayout__glow heroLayout__glow--purple" />
        <div className="heroLayout__glow heroLayout__glow--blue" />
        <div className="heroLayout__glow heroLayout__glow--cyan" />
      </div>

      <Navbar />

      <section className="hero">
        <div className="hero__mainGrid">
          {/* Left Content */}
          <div className="hero__leftContent">
            <div className="hero__badge animate-fadeInUp stagger-1">
              <Sparkles size={14} className="hero__badgeIcon" />
              <span>AI-Powered Content Repurposing</span>
            </div>

            <h1 className="hero__title animate-fadeInUp stagger-2">
              Turn One Piece of Content Into
              <br />
              <span className="hero__titleHighlight">A Month of Assets.</span>
            </h1>

            <p className="hero__subtitle animate-fadeInUp stagger-3">
              Upload a podcast, video, webinar, or interview once. Scriptloom produces clips,
              a full transcript, and repurposed written content — ready to publish across
              LinkedIn, X, Substack, and beyond.
            </p>

            <div className="hero__actions animate-fadeInUp stagger-4">
              <Link to="/dashboard" className="hero__btnPrimary" style={{ textDecoration: "none" }}>
                <span>Launch Content Studio</span>
                <ArrowRight size={18} />
              </Link>
              <Link to="/register" className="hero__btnSecondary" style={{ textDecoration: "none" }}>
                Create Free Account
              </Link>
            </div>

            <div className="hero__benefits animate-fadeInUp stagger-5">
              <div className="hero__benefitItem">
                <CheckCircle2 size={16} className="hero__checkIcon" />
                <span>Clips, transcripts & written posts</span>
              </div>
              <div className="hero__benefitItem">
                <CheckCircle2 size={16} className="hero__checkIcon" />
                <span>Built for LinkedIn, X & Substack</span>
              </div>
              <div className="hero__benefitItem">
                <CheckCircle2 size={16} className="hero__checkIcon" />
                <span>Free to start</span>
              </div>
            </div>
          </div>

          {/* Right — Product Mockup */}
          <div className="hero__rightContent animate-fadeInUp stagger-3">
            <div className="mockup">
              {/* Mockup window chrome */}
              <div className="mockup__chrome">
                <div className="mockup__dots">
                  <span /><span /><span />
                </div>
                <div className="mockup__url">app.scriptloom.ai/dashboard</div>
              </div>

              {/* Mockup app content */}
              <div className="mockup__body">
                {/* Sidebar */}
                <div className="mockup__sidebar">
                  <div className="mockup__sidebarItem mockup__sidebarItem--active"><Film size={14} /> Projects</div>
                  <div className="mockup__sidebarItem"><FileText size={14} /> Media</div>
                  <div className="mockup__sidebarItem"><Sparkles size={14} /> Content</div>
                </div>

                {/* Main area */}
                <div className="mockup__main">
                  <div className="mockup__metricRow">
                    <div className="mockup__metric">
                      <span className="mockup__metricValue">47.2</span>
                      <span className="mockup__metricLabel">Hours</span>
                    </div>
                    <div className="mockup__metric mockup__metric--purple">
                      <span className="mockup__metricValue">12</span>
                      <span className="mockup__metricLabel">Packs</span>
                    </div>
                    <div className="mockup__metric mockup__metric--green">
                      <span className="mockup__metricValue">3</span>
                      <span className="mockup__metricLabel">Projects</span>
                    </div>
                  </div>

                  <div className="mockup__projectCard">
                    <UploadCloud size={16} color="#4F46E5" />
                    <div>
                      <strong>AI Founder Podcast</strong>
                      <span>3 sources · 9 content packs</span>
                    </div>
                  </div>
                  <div className="mockup__projectCard">
                    <UploadCloud size={16} color="#8B5CF6" />
                    <div>
                      <strong>Product Launch Series</strong>
                      <span>5 sources · 14 content packs</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Trust bar */}
        <div className="hero__trust animate-fadeInUp stagger-6">
          <span>Trusted by creators and teams worldwide</span>
          <div className="hero__trustLogos">
            <span>Content Studio</span>
            <span>·</span>
            <span>Clip Generation</span>
            <span>·</span>
            <span>AI Transcription</span>
            <span>·</span>
            <span>Multi-Platform Export</span>
          </div>
        </div>
      </section>
    </div>
  );
}

export default Hero;
