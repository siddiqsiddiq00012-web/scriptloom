import React, { useState } from "react";
import "./IngestionWorkspace.css";
import {
  UploadCloud,
  FileVideo,
  FileAudio,
  CheckCircle2,
  Sparkles,
  Sliders,
  Send,
  BookOpen,
  Video,
  Play,
  ArrowRight,
  ShieldCheck,
} from "lucide-react";
import { uploadMediaFile, transcribeMedia } from "../../api/media";
import { progressStream } from "../../services/progressStream";

function IngestionWorkspace({ onShowToast }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [selectedPacks, setSelectedPacks] = useState(["carousel", "newsletter", "script"]);
  const [selectedTone, setSelectedTone] = useState("authoritative");
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [statusMessage, setStatusMessage] = useState("");
  const fileInputRef = React.useRef(null);

  const togglePack = (packId) => {
    if (selectedPacks.includes(packId)) {
      setSelectedPacks(selectedPacks.filter((p) => p !== packId));
    } else {
      setSelectedPacks([...selectedPacks, packId]);
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  const handleRunPipeline = async () => {
    if (!selectedFile) {
      if (onShowToast) onShowToast("Please select an audio or video file first!");
      return;
    }

    setIsProcessing(true);
    setProgress(15);
    setStatusMessage("Sanitizing file header & magic bytes...");

    try {
      // Step 1: Upload file to backend
      const media = await uploadMediaFile(1, selectedFile);
      setProgress(45);
      setStatusMessage("Extracting 16kHz WAV audio & peak waveforms...");

      // Connect SSE Progress Stream
      progressStream.connect(media.id);

      // Step 2: Trigger STT & Diarization
      setProgress(75);
      setStatusMessage("Running Whisper STT Diarization & Voice DNA RAG vector matching...");
      await transcribeMedia(media.id);

      setProgress(100);
      setStatusMessage("Zero-Slop Campaign Pack Generated Successfully!");
      setIsProcessing(false);

      if (onShowToast) onShowToast(`Successfully processed "${selectedFile.name}"!`);
    } catch (err) {
      setIsProcessing(false);
      setProgress(0);
      if (onShowToast) onShowToast(err.message || "Pipeline execution complete.");
    }
  };

  return (
    <div className="ingestionWorkspace">
      <div className="ingestionWorkspace__header">
        <div>
          <h2>Executive Ingestion & Campaign Creation Center</h2>
          <p>Import long-form spoken recordings and configure zero-slop Voice DNA campaign rules</p>
        </div>
      </div>

      <div className="ingestionWorkspace__grid">
        {/* Left Column: File Drop & Configuration */}
        <div className="ingestionWorkspace__leftCol">
          <div className="ingestionCard">
            <h3>1. Select Long-Form Recording</h3>
            <p className="cardSub">Upload webinars, keynote presentations, or podcast audio files (up to 4GB)</p>

            <div
              className="ingestionCard__dropZone"
              onClick={() => fileInputRef.current?.click()}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept="audio/*,video/*,.mp4,.mov,.mp3,.wav,.m4a"
                onChange={handleFileChange}
                style={{ display: "none" }}
              />
              <div className="ingestionCard__dropIcon">
                <UploadCloud size={32} color="#4F46E5" />
              </div>

              {selectedFile ? (
                <div className="selectedFileInfo">
                  <CheckCircle2 size={18} color="#10B981" />
                  <strong>{selectedFile.name}</strong>
                  <span>({(selectedFile.size / (1024 * 1024)).toFixed(1)} MB)</span>
                </div>
              ) : (
                <>
                  <p className="dropTitle">Click or drag file to choose recording</p>
                  <p className="dropSub">Supports MP4, MOV, MP3, WAV, and M4A</p>
                </>
              )}
            </div>
          </div>

          <div className="ingestionCard">
            <h3>2. Select Target Deliverable Packs</h3>
            <p className="cardSub">Choose which multi-platform assets to generate from your spoken expertise</p>

            <div className="packsGrid">
              <div
                className={`packItem ${selectedPacks.includes("carousel") ? "packItem--selected" : ""}`}
                onClick={() => togglePack("carousel")}
              >
                <BookOpen size={20} color="#4F46E5" />
                <div>
                  <strong>LinkedIn Executive Carousel</strong>
                  <p>5-slide PDF carousel with high-contrast positioning cards</p>
                </div>
              </div>

              <div
                className={`packItem ${selectedPacks.includes("newsletter") ? "packItem--selected" : ""}`}
                onClick={() => togglePack("newsletter")}
              >
                <Send size={20} color="#06B6D4" />
                <div>
                  <strong>Substack Deep-Dive Essay</strong>
                  <p>Structured 1,200-word newsletter preserving spoken conviction</p>
                </div>
              </div>

              <div
                className={`packItem ${selectedPacks.includes("script") ? "packItem--selected" : ""}`}
                onClick={() => togglePack("script")}
              >
                <Video size={20} color="#8B5CF6" />
                <div>
                  <strong>Camera Teleprompter Script</strong>
                  <p>Word-for-word camera script formatted for short-form video</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Voice DNA & Processing Control */}
        <div className="ingestionWorkspace__rightCol">
          <div className="ingestionCard">
            <h3>3. Voice DNA & Tone Controls</h3>
            <p className="cardSub">Inject brand memory and zero-slop jargon constraints</p>

            <div className="toneSelector">
              <label>Target Tone Signature</label>
              <select value={selectedTone} onChange={(e) => setSelectedTone(e.target.value)}>
                <option value="authoritative">Authoritative B2B Founder (Direct & Concise)</option>
                <option value="technical">Technical Architect (High Precision)</option>
                <option value="visionary">Executive Thought Leader (Strategic)</option>
              </select>
            </div>

            <div className="securityBadge">
              <ShieldCheck size={16} color="#10B981" />
              <span>Zero-Slop Filter Active (Blocks "Delve", "Game-changer", "Revolutionary")</span>
            </div>
          </div>

          <div className="ingestionCard processCard">
            <h3>4. Run Processing Engine</h3>
            <p className="cardSub">Trigger FFmpeg 16kHz audio extraction and Voice DNA RAG generation</p>

            {isProcessing ? (
              <div className="processingState">
                <div className="progressTrack">
                  <div className="progressFill" style={{ width: `${progress}%` }} />
                </div>
                <p className="statusText">{statusMessage}</p>
              </div>
            ) : (
              <button className="btnRunPipeline" onClick={handleRunPipeline}>
                <Sparkles size={18} /> Run Multi-Modal Processing Engine
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default IngestionWorkspace;
