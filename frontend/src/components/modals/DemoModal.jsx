import React, { useState } from "react";
import "./DemoModal.css";
import { X, Play, CheckCircle2, Sparkles, Cpu, Layers, FileText, ArrowRight, Share2, Copy } from "lucide-react";

function DemoModal({ isOpen, onClose, onOpenUpload }) {
  const [activeStep, setActiveStep] = useState(1);
  const [copied, setCopied] = useState(false);

  if (!isOpen) return null;

  const handleCopy = (text) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="demoModal__overlay" onClick={onClose}>
      <div className="demoModal__container" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="demoModal__header">
          <div className="demoModal__headerTitle">
            <div className="demoModal__badge">
              <Sparkles size={14} />
              <span>Interactive Workflow Demo</span>
            </div>
            <h2>How Scriptloom Operationalizes Expertise</h2>
          </div>
          <button className="demoModal__closeBtn" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        {/* Workflow Steps Nav */}
        <div className="demoModal__stepsNav">
          <button
            className={`demoModal__stepItem ${activeStep === 1 ? "demoModal__stepItem--active" : ""}`}
            onClick={() => setActiveStep(1)}
          >
            <span className="demoModal__stepNum">1</span>
            <div className="demoModal__stepText">
              <strong>Ingestion</strong>
              <span>Raw Spoken Dialogue</span>
            </div>
          </button>

          <button
            className={`demoModal__stepItem ${activeStep === 2 ? "demoModal__stepItem--active" : ""}`}
            onClick={() => setActiveStep(2)}
          >
            <span className="demoModal__stepNum">2</span>
            <div className="demoModal__stepText">
              <strong>Voice DNA & Memory</strong>
              <span>Semantic Reasoning</span>
            </div>
          </button>

          <button
            className={`demoModal__stepItem ${activeStep === 3 ? "demoModal__stepItem--active" : ""}`}
            onClick={() => setActiveStep(3)}
          >
            <span className="demoModal__stepNum">3</span>
            <div className="demoModal__stepText">
              <strong>Campaign Pack</strong>
              <span>Zero-Edit Output</span>
            </div>
          </button>
        </div>

        {/* Step Content */}
        <div className="demoModal__body">
          {activeStep === 1 && (
            <div className="demoModal__stepView">
              <div className="demoModal__videoPreviewCard">
                <div className="demoModal__videoHeader">
                  <div className="demoModal__videoTag">Webinar Recording (.MP4)</div>
                  <span className="demoModal__time">42:15 • 1.2 GB</span>
                </div>
                <div className="demoModal__videoPlayerSim">
                  <div className="demoModal__playBtnCircle">
                    <Play size={24} className="demoModal__playIcon" />
                  </div>
                  <div className="demoModal__speakerBar">
                    <div className="demoModal__speakerAvatar">SJ</div>
                    <div>
                      <strong>Sarah Jenkins</strong> — CEO & Founder
                      <p>"Why generic AI copy fails B2B software buyers in 2026..."</p>
                    </div>
                  </div>
                </div>
              </div>

              <div className="demoModal__stepInfo">
                <h3>1. Ingest Spoken Conversations</h3>
                <p>
                  Upload keynote speeches, podcasts, Zoom webinars, or executive voice notes.
                  Scriptloom automatically attributes speakers and extracts timestamped assertions.
                </p>
                <div className="demoModal__infoCheckList">
                  <div><CheckCircle2 size={16} color="#6366F1" /> Speaker Diarization</div>
                  <div><CheckCircle2 size={16} color="#6366F1" /> Background Noise Removal</div>
                  <div><CheckCircle2 size={16} color="#6366F1" /> Key Assertion Timestamping</div>
                </div>
                <button className="demoModal__nextBtn" onClick={() => setActiveStep(2)}>
                  Next: See Reasoning Engine <ArrowRight size={16} />
                </button>
              </div>
            </div>
          )}

          {activeStep === 2 && (
            <div className="demoModal__stepView">
              <div className="demoModal__reasoningCard">
                <div className="demoModal__reasoningHeader">
                  <Cpu size={18} color="#8B5CF6" />
                  <span>Voice DNA & Brand Memory Alignment</span>
                </div>

                <div className="demoModal__metricsGrid">
                  <div className="demoModal__metricItem">
                    <span className="demoModal__metricValue">99.4%</span>
                    <span className="demoModal__metricLabel">Tone Cadence Match</span>
                  </div>
                  <div className="demoModal__metricItem">
                    <span className="demoModal__metricValue">0%</span>
                    <span className="demoModal__metricLabel">Generic AI Buzzwords</span>
                  </div>
                  <div className="demoModal__metricItem">
                    <span className="demoModal__metricValue">14</span>
                    <span className="demoModal__metricLabel">Core Assertions Filtered</span>
                  </div>
                </div>

                <div className="demoModal__dnaSample">
                  <strong>Active Voice DNA Rules:</strong>
                  <ul>
                    <li>Direct, authoritative founder perspective; no corporate filler.</li>
                    <li>Prefers short punchy declarations followed by concrete data.</li>
                    <li>Banned Jargon: "game-changer", "synergy", "paradigm shift".</li>
                  </ul>
                </div>
              </div>

              <div className="demoModal__stepInfo">
                <h3>2. Reasoning Over Authentic Knowledge</h3>
                <p>
                  Scriptloom matches spoken dialogue against your historical Brand Memory store and
                  executes linguistic cadence rules to eliminate "AI slop".
                </p>
                <button className="demoModal__nextBtn" onClick={() => setActiveStep(3)}>
                  Next: View Generated Campaign <ArrowRight size={16} />
                </button>
              </div>
            </div>
          )}

          {activeStep === 3 && (
            <div className="demoModal__stepView">
              <div className="demoModal__outputCard">
                <div className="demoModal__outputHeader">
                  <FileText size={18} color="#4F46E5" />
                  <span>Zero-Edit Campaign Pack Preview</span>
                  <button
                    className="demoModal__copyBtn"
                    onClick={() =>
                      handleCopy("Why Generic AI Prose is Killing B2B Authority in 2026...")
                    }
                  >
                    <Copy size={14} />
                    <span>{copied ? "Copied!" : "Copy Asset"}</span>
                  </button>
                </div>

                <div className="demoModal__outputContent">
                  <h4>Hook: Why Generic AI Prose is Killing B2B Authority</h4>
                  <p>
                    "As the marginal cost of text generation approaches zero, the market value of
                    authentic human conviction approaches infinity. B2B buyers don't convert via
                    SEO keyword stuffing—they convert through proof of domain authority."
                  </p>
                  <div className="demoModal__tagsRow">
                    <span className="demoModal__tag">🎬 Video Script</span>
                    <span className="demoModal__tag">💼 LinkedIn Carousel</span>
                    <span className="demoModal__tag">📰 Substack Essay</span>
                  </div>
                </div>
              </div>

              <div className="demoModal__stepInfo">
                <h3>3. Publish-Ready Multi-Channel Output</h3>
                <p>
                  One single recording automatically outputs camera-ready video hooks, formatted
                  LinkedIn slide decks, and executive newsletter essays.
                </p>
                <button
                  className="demoModal__actionBtn"
                  onClick={() => {
                    onClose();
                    if (onOpenUpload) onOpenUpload();
                  }}
                >
                  Try It With Your Recording <ArrowRight size={16} />
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default DemoModal;
