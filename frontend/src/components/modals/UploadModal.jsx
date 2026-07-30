import React, { useState } from "react";
import "./UploadModal.css";
import {
  X,
  UploadCloud,
  FileVideo,
  CheckCircle2,
  Sparkles,
  ChevronLeft,
  ChevronRight,
  Copy,
  Check,
  Zap,
  BookOpen,
  Send,
  Video,
  Globe,
} from "lucide-react";

function UploadModal({ isOpen, onClose }) {
  const [stage, setStage] = useState("upload"); // 'upload' | 'processing' | 'results'
  const [uploadProgress, setUploadProgress] = useState(0);
  const [activeTab, setActiveTab] = useState("carousel"); // 'script' | 'carousel' | 'newsletter'
  const [carouselIndex, setCarouselIndex] = useState(0);
  const [copied, setCopied] = useState(false);
  const [pastedUrl, setPastedUrl] = useState("");

  if (!isOpen) return null;

  const carouselSlides = [
    {
      slideNum: 1,
      tag: "THE TRADITIONAL GAP",
      headline: "Conversations Contain More Value Than Documents",
      body: "Formal docs are sanitized. Spoken webinars are where unedited conviction lives.",
      bgColor: "#4F46E5",
      textColor: "#FFFFFF",
    },
    {
      slideNum: 2,
      tag: "THE PROBLEM",
      headline: "The Rise of Generic 'AI Slop'",
      body: "Generic LLM wrappers produce robotic copy that alienates sophisticated B2B buyers.",
      bgColor: "#0F172A",
      textColor: "#FFFFFF",
    },
    {
      slideNum: 3,
      tag: "VOICE DNA",
      headline: "AI Must Amplify Authority, Not Invent Thoughts",
      body: "Scriptloom extracts authentic human expertise with absolute fidelity to tone.",
      bgColor: "#F8FAFC",
      textColor: "#0F172A",
    },
    {
      slideNum: 4,
      tag: "THE SOLUTION",
      headline: "Zero-Edit Campaign Packs Across All Channels",
      body: "1 hour of executive dialogue fuels an entire month of publish-ready assets.",
      bgColor: "#EEF2FF",
      textColor: "#3730A3",
    },
  ];

  const handleStartUpload = () => {
    setStage("processing");
    setUploadProgress(0);
    const interval = setInterval(() => {
      setUploadProgress((prev) => {
        if (prev >= 100) {
          clearInterval(interval);
          setStage("results");
          return 100;
        }
        return prev + 25;
      });
    }, 400);
  };

  const handleCopy = (text) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="uploadModal__overlay" onClick={onClose}>
      <div className="uploadModal__container" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="uploadModal__header">
          <div className="uploadModal__titleGroup">
            <div className="uploadModal__badge">
              <Sparkles size={14} />
              <span>Multi-Modal Content Operations</span>
            </div>
            <h2>
              {stage === "results"
                ? "Zero-Edit Campaign Pack Ready"
                : "Ingest Unscripted Expertise"}
            </h2>
          </div>
          <button className="uploadModal__closeBtn" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        {/* Modal Body */}
        <div className="uploadModal__body">
          {/* UPLOAD STAGE */}
          {stage === "upload" && (
            <div className="uploadModal__uploadStage">
              <div
                className="uploadModal__dropZone"
                onClick={handleStartUpload}
              >
                <div className="uploadModal__dropIconBox">
                  <UploadCloud size={32} />
                </div>
                <h3>Drop your Recording or Podcast here</h3>
                <p>Supports MP4, MOV, MP3, WAV or Zoom Cloud exports (up to 4GB)</p>
                <button className="uploadModal__selectBtn">Select Recording</button>
              </div>

              <div className="uploadModal__divider">
                <span>OR PASTE URL</span>
              </div>

              <div className="uploadModal__urlInputGroup">
                <Globe size={18} className="uploadModal__urlIcon" />
                <input
                  type="text"
                  placeholder="Paste Zoom recording link, YouTube URL, or podcast feed..."
                  value={pastedUrl}
                  onChange={(e) => setPastedUrl(e.target.value)}
                />
                <button
                  className="uploadModal__urlSubmitBtn"
                  onClick={handleStartUpload}
                >
                  Process URL
                </button>
              </div>
            </div>
          )}

          {/* PROCESSING STAGE */}
          {stage === "processing" && (
            <div className="uploadModal__processingStage">
              <div className="uploadModal__spinnerCircle">
                <Sparkles size={28} className="uploadModal__sparkleAnim" />
              </div>
              <h3>Analyzing Spoken Dialogue...</h3>
              <p>Diarizing speakers & matching against Voice DNA & Brand Memory</p>

              <div className="uploadModal__progressBarTrack">
                <div
                  className="uploadModal__progressBarFill"
                  style={{ width: `${uploadProgress}%` }}
                />
              </div>

              <div className="uploadModal__processingSteps">
                <div className={uploadProgress >= 25 ? "step--done" : ""}>
                  <CheckCircle2 size={16} /> Speaker Attribution & Diarization
                </div>
                <div className={uploadProgress >= 50 ? "step--done" : ""}>
                  <CheckCircle2 size={16} /> Voice DNA Cadence & Jargon Filter
                </div>
                <div className={uploadProgress >= 75 ? "step--done" : ""}>
                  <CheckCircle2 size={16} /> Brand Memory Index Cross-Reference
                </div>
                <div className={uploadProgress >= 100 ? "step--done" : ""}>
                  <CheckCircle2 size={16} /> Campaign Pack Generation
                </div>
              </div>
            </div>
          )}

          {/* RESULTS / CAMPAIGN PACK STAGE */}
          {stage === "results" && (
            <div className="uploadModal__resultsStage">
              {/* Asset Tabs */}
              <div className="uploadModal__assetTabs">
                <button
                  className={`uploadModal__tabBtn ${
                    activeTab === "carousel" ? "uploadModal__tabBtn--active" : ""
                  }`}
                  onClick={() => setActiveTab("carousel")}
                >
                  <BookOpen size={16} />
                  <span>LinkedIn Carousel</span>
                </button>

                <button
                  className={`uploadModal__tabBtn ${
                    activeTab === "script" ? "uploadModal__tabBtn--active" : ""
                  }`}
                  onClick={() => setActiveTab("script")}
                >
                  <Video size={16} />
                  <span>Camera Script</span>
                </button>

                <button
                  className={`uploadModal__tabBtn ${
                    activeTab === "newsletter" ? "uploadModal__tabBtn--active" : ""
                  }`}
                  onClick={() => setActiveTab("newsletter")}
                >
                  <Send size={16} />
                  <span>Executive Newsletter</span>
                </button>
              </div>

              {/* Tab 1: LinkedIn Carousel Preview */}
              {activeTab === "carousel" && (
                <div className="uploadModal__tabView">
                  <div className="uploadModal__carouselViewer">
                    <div
                      className="uploadModal__slideCard"
                      style={{
                        backgroundColor: carouselSlides[carouselIndex].bgColor,
                        color: carouselSlides[carouselIndex].textColor,
                      }}
                    >
                      <span className="uploadModal__slideTag">
                        {carouselSlides[carouselIndex].tag}
                      </span>
                      <h2>{carouselSlides[carouselIndex].headline}</h2>
                      <p>{carouselSlides[carouselIndex].body}</p>
                      <div className="uploadModal__slideFooter">
                        <span>Scriptloom • Slide {carouselIndex + 1} of 4</span>
                      </div>
                    </div>

                    <div className="uploadModal__carouselControls">
                      <button
                        disabled={carouselIndex === 0}
                        onClick={() => setCarouselIndex((prev) => Math.max(0, prev - 1))}
                      >
                        <ChevronLeft size={18} /> Prev
                      </button>
                      <span>{carouselIndex + 1} / {carouselSlides.length}</span>
                      <button
                        disabled={carouselIndex === carouselSlides.length - 1}
                        onClick={() =>
                          setCarouselIndex((prev) =>
                            Math.min(carouselSlides.length - 1, prev + 1)
                          )
                        }
                      >
                        Next <ChevronRight size={18} />
                      </button>
                    </div>
                  </div>

                  <div className="uploadModal__tabActions">
                    <button
                      className="uploadModal__primaryCopyBtn"
                      onClick={() =>
                        handleCopy(
                          JSON.stringify(carouselSlides[carouselIndex], null, 2)
                        )
                      }
                    >
                      {copied ? <Check size={16} /> : <Copy size={16} />}
                      <span>{copied ? "Copied Slide Data!" : "Copy PDF Carousel"}</span>
                    </button>
                  </div>
                </div>
              )}

              {/* Tab 2: Camera Script View */}
              {activeTab === "script" && (
                <div className="uploadModal__tabView">
                  <div className="uploadModal__scriptBox">
                    <div className="uploadModal__scriptHeader">
                      <strong>Hook Option A (High Conviction)</strong>
                      <span>Estimated Duration: 45s</span>
                    </div>
                    <p className="uploadModal__scriptText">
                      "Stop converting B2B buyers with generic AI slop. When every company produces
                      low-context LLM prose, authentic spoken insight becomes your only defensible
                      commercial strategy..."
                    </p>
                    <div className="uploadModal__scriptHeader" style={{ marginTop: "16px" }}>
                      <strong>Hook Option B (Counter-Intuitive)</strong>
                    </div>
                    <p className="uploadModal__scriptText">
                      "Your webinars contain 10x more positioning clarity than your landing pages.
                      Here is how we turn a 60-minute recorded session into an entire month's content
                      engine..."
                    </p>
                  </div>
                  <button
                    className="uploadModal__primaryCopyBtn"
                    onClick={() =>
                      handleCopy(
                        "Hook Option A: Stop converting B2B buyers with generic AI slop..."
                      )
                    }
                  >
                    {copied ? <Check size={16} /> : <Copy size={16} />}
                    <span>{copied ? "Copied Script!" : "Copy Teleprompter Script"}</span>
                  </button>
                </div>
              )}

              {/* Tab 3: Executive Newsletter */}
              {activeTab === "newsletter" && (
                <div className="uploadModal__tabView">
                  <div className="uploadModal__scriptBox">
                    <h3>Subject: The End of Commodity Marketing</h3>
                    <p className="uploadModal__scriptText">
                      Dear Reader,<br /><br />
                      This week on our internal strategy call, we unpacked why modern B2B buyers are
                      completely immune to generic AI articles.<br /><br />
                      <strong>Key Insight:</strong> Software buyers don't buy features—they buy proof of
                      domain authority. When expertise is trapped in linear 1GB Zoom files, your marketing
                      team loses 95% of your intellectual property.<br /><br />
                      Best,<br />
                      Founder & CEO
                    </p>
                  </div>
                  <button
                    className="uploadModal__primaryCopyBtn"
                    onClick={() =>
                      handleCopy("Subject: The End of Commodity Marketing...")
                    }
                  >
                    {copied ? <Check size={16} /> : <Copy size={16} />}
                    <span>{copied ? "Copied Newsletter!" : "Copy Markdown Essay"}</span>
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default UploadModal;
