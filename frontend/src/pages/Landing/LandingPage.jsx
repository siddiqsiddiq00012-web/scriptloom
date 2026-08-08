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
            <span className="landingSection__tag">HOW IT WORKS</span>
            <h2>From One Recording to a Full Content System</h2>
            <p>Upload once, and let the pipeline handle the rest — no manual editing between formats.</p>
          </div>

          <div className="landingSection__pipelineGrid">
            <div className="pipelineCard">
              <div className="pipelineCard__num">01</div>
              <div className="pipelineCard__iconBox">
                <UploadCloud size={24} color="#4F46E5" />
              </div>
              <h3>Upload Your Source</h3>
              <p>
                Add a podcast, video, webinar, or interview to a project. We transcribe it and
                surface the key moments automatically.
              </p>
            </div>

            <div className="pipelineCard">
              <div className="pipelineCard__num">02</div>
              <div className="pipelineCard__iconBox">
                <Sparkles size={24} color="#8B5CF6" />
              </div>
              <h3>AI Extracts & Repurposes</h3>
              <p>
                Our pipeline identifies clips, generates a clean transcript, and produces
                ready-to-publish written content from your material.
              </p>
            </div>

            <div className="pipelineCard">
              <div className="pipelineCard__num">03</div>
              <div className="pipelineCard__iconBox">
                <Send size={24} color="#06B6D4" />
              </div>
              <h3>Review, Edit & Export</h3>
              <p>
                Polish each asset in the workspace, then export single pieces or the whole
                pack as Markdown, text, JSON, or a ZIP.
              </p>
            </div>
          </div>
        </section>

        {/* 2. COMPARISON TABLE */}
        <section id="comparison" className="landingSection landingSection--comparison">
          <div className="landingSection__header">
            <span className="landingSection__tag">WHY SCRIPTLOOM</span>
            <h2>Built for Content Repurposing, Not Generic Text Generation</h2>
            <p>Compare the end-to-end workflow against manual, copy-paste repurposing.</p>
          </div>

          <div className="comparisonTable">
            <div className="comparisonTable__header">
              <div className="colFeature">Capability</div>
              <div className="colScriptloom">
                <Sparkles size={16} /> Scriptloom
              </div>
              <div className="colGeneric">Manual / Generic Tools</div>
            </div>

            <div className="comparisonTable__row">
              <div className="colFeature">Source Material</div>
              <div className="colScriptloom">
                <CheckCircle2 size={16} color="#10B981" /> Podcasts, videos, webinars, interviews
              </div>
              <div className="colGeneric">
                <XCircle size={16} color="#EF4444" /> Text prompts & paste-in transcripts
              </div>
            </div>

            <div className="comparisonTable__row">
              <div className="colFeature">Outputs</div>
              <div className="colScriptloom">
                <CheckCircle2 size={16} color="#10B981" /> Clips, transcripts & written assets
              </div>
              <div className="colGeneric">
                <XCircle size={16} color="#EF4444" /> Single unformatted text wall
              </div>
            </div>

            <div className="comparisonTable__row">
              <div className="colFeature">Workflow</div>
              <div className="colScriptloom">
                <CheckCircle2 size={16} color="#10B981" /> One project, one pipeline
              </div>
              <div className="colGeneric">
                <XCircle size={16} color="#EF4444" /> Copy between tabs & tools
              </div>
            </div>

            <div className="comparisonTable__row">
              <div className="colFeature">Export</div>
              <div className="colScriptloom">
                <CheckCircle2 size={16} color="#10B981" /> Markdown, text, JSON & ZIP downloads
              </div>
              <div className="colGeneric">
                <XCircle size={16} color="#EF4444" /> Copy / paste only
              </div>
            </div>
          </div>
        </section>

        {/* 3. SECURITY & COMPLIANCE BAR */}
        <section className="landingSection landingSection--security">
          <div className="securityCard">
            <div className="securityCard__left">
              <ShieldCheck size={36} color="#4F46E5" />
              <div>
                <h3>Security & Privacy</h3>
                <p>Your projects and media are private to your account and protected end to end.</p>
              </div>
            </div>

            <div className="securityCard__badges">
              <div className="secBadge">
                <Lock size={16} /> 256-Bit SSL Encryption
              </div>
              <div className="secBadge">
                <Server size={16} /> Secure Cloud Storage
              </div>
              <div className="secBadge">
                <Zap size={16} /> No Sharing of Your Data
              </div>
            </div>
          </div>
        </section>

        {/* 4. PRICING MATRIX */}
        <section id="pricing" className="landingSection landingSection--pricing">
          <div className="landingSection__header">
            <span className="landingSection__tag">TRANSPARENT PRICING</span>
            <h2>Simple Plans for Every Creator</h2>
            <p>Start free today. Upgrade as your content library grows.</p>
          </div>

          <div className="pricingGrid">
            <div className="pricingCard">
              <h3>Starter</h3>
              <div className="pricingCard__price">
                $0<span>/month</span>
              </div>
              <p>For creators exploring content repurposing</p>
              <ul>
                <li>
                  <CheckCircle2 size={16} color="#10B981" /> 5 hours of processing / month
                </li>
                <li>
                  <CheckCircle2 size={16} color="#10B981" /> 10 generated content packs
                </li>
                <li>
                  <CheckCircle2 size={16} color="#10B981" /> Clips, transcripts & exports
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
                  <CheckCircle2 size={16} color="#10B981" /> 50 hours of processing / month
                </li>
                <li>
                  <CheckCircle2 size={16} color="#10B981" /> 500 generated content packs
                </li>
                <li>
                  <CheckCircle2 size={16} color="#10B981" /> Priority processing & support
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
                  <CheckCircle2 size={16} color="#10B981" /> Unlimited processing
                </li>
                <li>
                  <CheckCircle2 size={16} color="#10B981" /> Custom team seats & SLA
                </li>
                <li>
                  <CheckCircle2 size={16} color="#10B981" /> Dedicated support
                </li>
              </ul>
              <Link to="/dashboard" className="pricingBtn pricingBtn--starter">
                Contact Sales
              </Link>
            </div>
          </div>
        </section>

        {/* 5. FOOTER */}
        <footer className="landingFooter">
          <div className="landingFooter__container">
            <div className="landingFooter__brand">
              <div className="landingFooter__logo">
                <div className="landingFooter__logoIcon">S</div>
                <span>Scriptloom</span>
              </div>
              <p>AI content repurposing for creators & teams.</p>
            </div>

            <div className="landingFooter__links">
              <div>
                <h4>Product</h4>
                <Link to="/dashboard">Content Studio</Link>
                <Link to="/dashboard">Projects</Link>
                <Link to="/dashboard">Media Library</Link>
              </div>

              <div>
                <h4>Resources</h4>
                <Link to="/register">Get Started</Link>
                <Link to="/login">Sign In</Link>
              </div>

              <div>
                <h4>Company</h4>
                <Link to="/dashboard">Security</Link>
                <Link to="/register">Privacy</Link>
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
