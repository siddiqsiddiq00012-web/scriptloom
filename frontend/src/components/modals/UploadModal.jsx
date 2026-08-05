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
  BookOpen,
  Send,
  Video,
  Globe,
  AlertCircle,
  FileAudio,
} from "lucide-react";
import { uploadMediaFile, transcribeMedia } from "../../api/media";
import { getProjects } from "../../api/projects";
import { progressStream } from "../../services/progressStream";

function UploadModal({ isOpen, onClose }) {
  const [stage, setStage] = useState("upload"); // 'upload' | 'confirm' | 'processing' | 'results'
  const [selectedFile, setSelectedFile] = useState(null);
  const [pastedUrl, setPastedUrl] = useState("");
  const [uploadProgress, setUploadProgress] = useState(0);
  const [activeTab, setActiveTab] = useState("carousel"); // 'carousel' | 'script' | 'newsletter'
  const [carouselIndex, setCarouselIndex] = useState(0);
  const [copied, setCopied] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  // Live Backend Data
  const [uploadedMedia, setUploadedMedia] = useState(null);
  const [transcriptData, setTranscriptData] = useState(null);

  const fileInputRef = React.useRef(null);

  React.useEffect(() => {
    const handleStreamUpdate = (msg) => {
      if (msg.type === "event" && msg.data?.payload?.progress) {
        setUploadProgress(msg.data.payload.progress);
      }
    };
    progressStream.subscribe(handleStreamUpdate);
    return () => progressStream.unsubscribe(handleStreamUpdate);
  }, []);

  if (!isOpen) return null;

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setStage("confirm");
      setErrorMessage("");
    }
  };

  const handleStartProcessing = async () => {
    if (!selectedFile && !pastedUrl) return;

    setStage("processing");
    setUploadProgress(20);
    setErrorMessage("");

    try {
      if (selectedFile) {
        setUploadProgress(30);

        // Fetch user's projects to determine which project to upload to
        const projects = await getProjects();
        if (!Array.isArray(projects) || projects.length === 0) {
          setErrorMessage("Please create a project first before uploading media.");
          setStage("confirm");
          return;
        }
        const targetProjectId = projects[0].id;

        setUploadProgress(40);
        const media = await uploadMediaFile(targetProjectId, selectedFile);
        setUploadedMedia(media);

        // Connect SSE progress stream
        progressStream.connect(media.id);
        setUploadProgress(70);

        const transcript = await transcribeMedia(media.id);
        setTranscriptData(transcript);
        setUploadProgress(100);
        setStage("results");
      } else if (pastedUrl) {
        setUploadProgress(50);
        setTimeout(() => {
          setUploadProgress(100);
          setStage("results");
        }, 1200);
      }
    } catch (err) {
      console.error("Upload & Processing error:", err);
      setErrorMessage(err.message || "Failed to process media file on live server.");
      setStage("confirm");
    }
  };

  const handleCopy = (text) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

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
                : stage === "confirm"
                ? "Confirm Recording File"
                : "Ingest Unscripted Expertise"}
            </h2>
          </div>
          <button className="uploadModal__closeBtn" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        {/* Modal Body */}
        <div className="uploadModal__body">
          {errorMessage && (
            <div className="uploadModal__errorBanner">
              <AlertCircle size={16} />
              <span>{errorMessage}</span>
            </div>
          )}

          {/* STAGE 1: FILE SELECT */}
          {stage === "upload" && (
            <div className="uploadModal__uploadStage">
              <div
                className="uploadModal__dropZone"
                onClick={() => fileInputRef.current?.click()}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="audio/*,video/*,.mp4,.mov,.mp3,.wav,.m4a"
                  onChange={handleFileChange}
                  style={{ display: "none" }}
                />
                <div className="uploadModal__dropIconBox">
                  <UploadCloud size={32} />
                </div>
                <h3>Select your Recording or Podcast File</h3>
                <p>Click here to choose an MP4, MOV, MP3, or WAV file (up to 4GB)</p>
                <span className="uploadModal__selectBtn">
                  Select Recording File
                </span>
              </div>

              <div className="uploadModal__divider">
                <span>OR PASTE RECORDING URL</span>
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
                  onClick={() => pastedUrl && setStage("confirm")}
                >
                  Process URL
                </button>
              </div>
            </div>
          )}

          {/* STAGE 2: CONFIRM FILE SELECTION */}
          {stage === "confirm" && (
            <div className="uploadModal__confirmStage">
              <div className="uploadModal__fileCard">
                <div className="uploadModal__fileIconBox">
                  {selectedFile?.name?.endsWith(".mp4") ? (
                    <FileVideo size={28} color="#4F46E5" />
                  ) : (
                    <FileAudio size={28} color="#8B5CF6" />
                  )}
                </div>
                <div className="uploadModal__fileDetails">
                  <strong>{selectedFile ? selectedFile.name : "Zoom Cloud Recording URL"}</strong>
                  <p>
                    {selectedFile
                      ? `${(selectedFile.size / (1024 * 1024)).toFixed(2)} MB • Ready for Voice DNA extraction`
                      : pastedUrl}
                  </p>
                </div>
                <button
                  className="uploadModal__changeFileBtn"
                  onClick={() => {
                    setSelectedFile(null);
                    setStage("upload");
                  }}
                >
                  Change File
                </button>
              </div>

              <button
                className="uploadModal__startProcessBtn"
                onClick={handleStartProcessing}
              >
                <Sparkles size={18} />
                <span>Upload & Extract Spoken Knowledge</span>
              </button>
            </div>
          )}

          {/* STAGE 3: PROCESSING STAGE */}
          {stage === "processing" && (
            <div className="uploadModal__processingStage">
              <div className="uploadModal__spinnerCircle">
                <Sparkles size={28} className="uploadModal__sparkleAnim" />
              </div>
              <h3>Processing Recording on Live Server...</h3>
              <p>Extracting 16kHz mono WAV, diarizing speakers & executing Voice DNA rules</p>

              <div className="uploadModal__progressBarTrack">
                <div
                  className="uploadModal__progressBarFill"
                  style={{ width: `${uploadProgress}%` }}
                />
              </div>

              <div className="uploadModal__processingSteps">
                <div className={uploadProgress >= 20 ? "step--done" : ""}>
                  <CheckCircle2 size={16} /> File Upload & Verification
                </div>
                <div className={uploadProgress >= 50 ? "step--done" : ""}>
                  <CheckCircle2 size={16} /> Speaker Attribution & Diarization
                </div>
                <div className={uploadProgress >= 70 ? "step--done" : ""}>
                  <CheckCircle2 size={16} /> Voice DNA Cadence & Jargon Filter
                </div>
                <div className={uploadProgress >= 100 ? "step--done" : ""}>
                  <CheckCircle2 size={16} /> Campaign Pack Generation Complete
                </div>
              </div>
            </div>
          )}

          {/* STAGE 4: RESULTS STAGE */}
          {stage === "results" && (
            <div className="uploadModal__resultsStage">
              <div className="uploadModal__assetTabs">
                <button
                  className={`uploadModal__tabBtn ${activeTab === "carousel" ? "uploadModal__tabBtn--active" : ""}`}
                  onClick={() => setActiveTab("carousel")}
                >
                  <BookOpen size={16} />
                  <span>LinkedIn Carousel</span>
                </button>

                <button
                  className={`uploadModal__tabBtn ${activeTab === "script" ? "uploadModal__tabBtn--active" : ""}`}
                  onClick={() => setActiveTab("script")}
                >
                  <Video size={16} />
                  <span>Camera Script</span>
                </button>

                <button
                  className={`uploadModal__tabBtn ${activeTab === "newsletter" ? "uploadModal__tabBtn--active" : ""}`}
                  onClick={() => setActiveTab("newsletter")}
                >
                  <Send size={16} />
                  <span>Executive Newsletter</span>
                </button>
              </div>

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
                        onClick={() => setCarouselIndex((prev) => Math.min(carouselSlides.length - 1, prev + 1))}
                      >
                        Next <ChevronRight size={18} />
                      </button>
                    </div>
                  </div>

                  <div className="uploadModal__tabActions">
                    <button
                      className="uploadModal__primaryCopyBtn"
                      onClick={() => handleCopy(JSON.stringify(carouselSlides[carouselIndex], null, 2))}
                    >
                      {copied ? <Check size={16} /> : <Copy size={16} />}
                      <span>{copied ? "Copied Slide Data!" : "Copy Carousel Slide"}</span>
                    </button>
                  </div>
                </div>
              )}

              {activeTab === "script" && (
                <div className="uploadModal__tabView">
                  <div className="uploadModal__scriptBox">
                    <div className="uploadModal__scriptHeader">
                      <strong>Hook Option A (High Conviction)</strong>
                      <span>Estimated Duration: 45s</span>
                    </div>
                    <p className="uploadModal__scriptText">
                      "Stop converting B2B buyers with generic AI slop. When every company produces low-context LLM prose, authentic spoken insight becomes your only defensible commercial strategy..."
                    </p>
                  </div>
                  <button
                    className="uploadModal__primaryCopyBtn"
                    onClick={() => handleCopy("Stop converting B2B buyers with generic AI slop...")}
                  >
                    {copied ? <Check size={16} /> : <Copy size={16} />}
                    <span>{copied ? "Copied Script!" : "Copy Teleprompter Script"}</span>
                  </button>
                </div>
              )}

              {activeTab === "newsletter" && (
                <div className="uploadModal__tabView">
                  <div className="uploadModal__scriptBox">
                    <h3>Subject: The End of Commodity Marketing</h3>
                    <p className="uploadModal__scriptText">
                      Dear Reader,<br /><br />
                      This week on our internal strategy call, we unpacked why modern B2B buyers are completely immune to generic AI articles.<br /><br />
                      <strong>Key Insight:</strong> Software buyers don't buy features—they buy proof of domain authority.
                    </p>
                  </div>
                  <button
                    className="uploadModal__primaryCopyBtn"
                    onClick={() => handleCopy("Subject: The End of Commodity Marketing...")}
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
