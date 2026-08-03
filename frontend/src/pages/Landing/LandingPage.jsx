import React from "react";
import { Link } from "react-router-dom";
import PublicLayout from "../../components/layout/PublicLayout";
import Hero from "../../components/landing/Hero";
import "./LandingPage.css";
import {
  UploadCloud,
  Sparkles,
  Send,
  CheckCircle2,
  XCircle,
  ShieldCheck,
  Lock,
  Server,
  Zap,
  ArrowRight,
  Crown,
} from "lucide-react";

function LandingPage() {
  return (
    <PublicLayout>
      <main className="landingMain">
        <Hero />

        {/* 1. HOW IT WORKS (3-STEP PIPELINE) */}
        <section id="features" className="landingSection landingSection--pipeline">
          <div className="landingSection__header">
            <span className="landingSection__tag">THE CREATOR ENGINE</span>
            <h2>Build a Scalable Content Engine Without Burnout</h2>
            <p>Turn a single raw idea or recording into a month of high-converting multi-platform content</p>
          </div>

          <div className="landingSection__pipelineGrid">
            <div className="pipelineCard">
              <div className="pipelineCard__num">01</div>
              <div className="pipelineCard__iconBox">
                <UploadCloud size={24} color="#4F46E5" />
              </div>
              <h3>1-Click Content Multiplier</h3>
              <p>
                Drop any voice note, text outline, or video. Scriptloom analyzes core hooks, key insights, and audience takeaways.
              </p>
            </div>

            <div className="pipelineCard">
              <div className="pipelineCard__num">02</div>
              <div className="pipelineCard__iconBox">
                <Sparkles size={24} color="#8B5CF6" />
              </div>
              <h3>Personal Brand Voice System</h3>
              <p>
                Enforces your unique writing style, brand tone, and banned jargon filters so every post sounds 100% authentic.
              </p>
            </div>

            <div className="pipelineCard">
              <div className="pipelineCard__num">03</div>
              <div className="pipelineCard__iconBox">
                <Send size={24} color="#06B6D4" />
              </div>
              <h3>Omnichannel Creator Export</h3>
              <p>
                Instantly exports formatted LinkedIn Carousels, viral X Threads, Substack Newsletters, and Video Scripts.
              </p>
            </div>
          </div>
        </section>

        {/* 2. VOICE DNA VS GENERIC AI COMPARISON TABLE */}
        <section id="comparison" className="landingSection landingSection--comparison">
          <div className="landingSection__header">
            <span className="landingSection__tag">THE ZERO-SLOP GUARANTEE</span>
            <h2>Why B2B Leaders Choose Scriptloom Over Generic LLMs</h2>
            <p>As marginal text cost approaches zero, authentic conviction becomes your only moat</p>
          </div>

          <div className="comparisonTable">
            <div className="comparisonTable__header">
              <div className="colFeature">Capability</div>
              <div className="colScriptloom">
                <Sparkles size={16} /> Scriptloom AI OS
              </div>
              <div className="colGeneric">Generic AI Wrappers</div>
            </div>

            <div className="comparisonTable__row">
              <div className="colFeature">Source Material</div>
              <div className="colScriptloom">
                <CheckCircle2 size={16} color="#10B981" /> Spoken unscripted conviction
              </div>
              <div className="colGeneric">
                <XCircle size={16} color="#EF4444" /> Text prompts & guesswork
              </div>
            </div>

            <div className="comparisonTable__row">
              <div className="colFeature">Jargon Enforcement</div>
              <div className="colScriptloom">
                <CheckCircle2 size={16} color="#10B981" /> 0% AI slop (banned buzzword filter)
              </div>
              <div className="colGeneric">
                <XCircle size={16} color="#EF4444" /> Heavy AI clichés ("game-changer")
              </div>
            </div>

            <div className="comparisonTable__row">
              <div className="colFeature">Brand Memory RAG</div>
              <div className="colScriptloom">
                <CheckCircle2 size={16} color="#10B981" /> 32-dim semantic vector quote store
              </div>
              <div className="colGeneric">
                <XCircle size={16} color="#EF4444" /> Zero memory across sessions
              </div>
            </div>

            <div className="comparisonTable__row">
              <div className="colFeature">Multi-Platform Asset Output</div>
              <div className="colScriptloom">
                <CheckCircle2 size={16} color="#10B981" /> LinkedIn, Camera Script, Newsletter, ZIP
              </div>
              <div className="colGeneric">
                <XCircle size={16} color="#EF4444" /> Single unformatted text wall
              </div>
            </div>
          </div>
        </section>

        {/* 3. ENTERPRISE SECURITY & COMPLIANCE BAR */}
        <section className="landingSection landingSection--security">
          <div className="securityCard">
            <div className="securityCard__left">
              <ShieldCheck size={36} color="#4F46E5" />
              <div>
                <h3>Enterprise Security & Private Voice Storage</h3>
                <p>Your spoken knowledge and Voice DNA models are strictly private to your organization.</p>
              </div>
            </div>

            <div className="securityCard__badges">
              <div className="secBadge">
                <Lock size={16} /> 256-Bit SSL Encryption
              </div>
              <div className="secBadge">
                <Server size={16} /> SOC2 Type II Compliant
              </div>
              <div className="secBadge">
                <Zap size={16} /> Zero AI Training on Creator Data
              </div>
            </div>
          </div>
        </section>

        {/* 4. FOUNDER PRICING MATRIX */}
        <section id="pricing" className="landingSection landingSection--pricing">
          <div className="landingSection__header">
            <span className="landingSection__tag">TRANSPARENT PRICING</span>
            <h2>Designed for Executive Founders & Growth Teams</h2>
            <p>Start free today. Scale as your spoken content library grows.</p>
          </div>

          <div className="pricingGrid">
            <div className="pricingCard">
              <h3>Starter</h3>
              <div className="pricingCard__price">
                $0<span>/month</span>
              </div>
              <p>For founders testing spoken content repurposing</p>
              <ul>
                <li>
                  <CheckCircle2 size={16} color="#10B981" /> 5 hours audio processing/mo
                </li>
                <li>
                  <CheckCircle2 size={16} color="#10B981" /> 10 Campaign Packs
                </li>
                <li>
                  <CheckCircle2 size={16} color="#10B981" /> 1 Voice DNA Profile
                </li>
              </ul>
              <Link to="/dashboard" className="pricingBtn pricingBtn--starter">
                Get Started Free
              </Link>
            </div>

            <div className="pricingCard pricingCard--featured">
              <div className="pricingCard__featuredBadge">
                <Crown size={14} /> MOST POPULAR
              </div>
              <h3>Founder Pro</h3>
              <div className="pricingCard__price">
                $49<span>/month</span>
              </div>
              <p>For active creators & growing marketing teams</p>
              <ul>
                <li>
                  <CheckCircle2 size={16} color="#10B981" /> 50 hours audio processing/mo
                </li>
                <li>
                  <CheckCircle2 size={16} color="#10B981" /> Unlimited Campaign Packs
                </li>
                <li>
                  <CheckCircle2 size={16} color="#10B981" /> 3 Voice DNA Profiles
                </li>
                <li>
                  <CheckCircle2 size={16} color="#10B981" /> Creator Memory RAG Vector Search
                </li>
              </ul>
              <Link to="/dashboard" className="pricingBtn pricingBtn--pro">
                Upgrade to Founder Pro
              </Link>
            </div>

            <div className="pricingCard">
              <h3>Enterprise</h3>
              <div className="pricingCard__price">Custom</div>
              <p>For media networks & high-volume organizations</p>
              <ul>
                <li>
                  <CheckCircle2 size={16} color="#10B981" /> Unlimited audio processing
                </li>
                <li>
                  <CheckCircle2 size={16} color="#10B981" /> Dedicated Voice DNA Fine-tuning
                </li>
                <li>
                  <CheckCircle2 size={16} color="#10B981" /> Custom Team Seats & SLA
                </li>
              </ul>
              <Link to="/dashboard" className="pricingBtn pricingBtn--starter">
                Contact Sales
              </Link>
            </div>
          </div>
        </section>

        {/* 5. ENTERPRISE FOOTER */}
        <footer className="landingFooter">
          <div className="landingFooter__container">
            <div className="landingFooter__brand">
              <div className="landingFooter__logo">
                <div className="landingFooter__logoIcon">S</div>
                <span>Scriptloom</span>
              </div>
              <p>AI Content OS for Knowledge Creators & Executive Founders</p>
            </div>

            <div className="landingFooter__links">
              <div>
                <h4>Product</h4>
                <Link to="/dashboard">Content Studio</Link>
                <Link to="/dashboard">Voice DNA Engine</Link>
                <Link to="/dashboard">Vector Memory</Link>
              </div>

              <div>
                <h4>Resources</h4>
                <a href="#whitepaper">Strategic Whitepaper</a>
                <a href="#roadmap">Master Roadmap</a>
                <a href="#api">API Reference</a>
              </div>

              <div>
                <h4>Company</h4>
                <a href="#about">About Us</a>
                <a href="#security">Security</a>
                <a href="#privacy">Privacy Policy</a>
              </div>
            </div>
          </div>

          <div className="landingFooter__bottom">
            <span>© 2026 Scriptloom AI Inc. All rights reserved.</span>
          </div>
        </footer>
      </main>
    </PublicLayout>
  );
}

export default LandingPage;