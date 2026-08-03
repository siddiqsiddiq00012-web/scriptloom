import React from "react";
import "./AnalyticsWorkspace.css";
import { BarChart2, Sparkles, Zap, TrendingUp, BookOpen, Send, Video } from "lucide-react";

function AnalyticsWorkspace() {
  return (
    <div className="analyticsWorkspace">
      <div className="analyticsWorkspace__header">
        <div>
          <h2>Executive Spoken Knowledge Analytics</h2>
          <p>Track Voice DNA fidelity, repurposing velocity, and multi-channel content reach</p>
        </div>
      </div>

      <div className="analyticsWorkspace__grid">
        <div className="analyticsWorkspace__card">
          <div className="analyticsWorkspace__cardHeader">
            <TrendingUp size={20} color="#4F46E5" />
            <span>Spoken Knowledge Velocity</span>
          </div>
          <span className="analyticsWorkspace__num">142.5 hrs</span>
          <p>Total raw audio ingested across 38 recordings</p>
        </div>

        <div className="analyticsWorkspace__card">
          <div className="analyticsWorkspace__cardHeader">
            <Sparkles size={20} color="#8B5CF6" />
            <span>Voice DNA Match Score</span>
          </div>
          <span className="analyticsWorkspace__num">99.4%</span>
          <p>0% generic AI slop detected across all assets</p>
        </div>

        <div className="analyticsWorkspace__card">
          <div className="analyticsWorkspace__cardHeader">
            <Zap size={20} color="#EC4899" />
            <span>Operational Time Saved</span>
          </div>
          <span className="analyticsWorkspace__num">184 hrs</span>
          <p>Eliminated manual copywriter drag & transcription</p>
        </div>
      </div>

      <div className="analyticsWorkspace__channelsCard">
        <h3>Multi-Platform Distribution Breakdown</h3>
        <div className="analyticsWorkspace__channelList">
          <div className="analyticsWorkspace__channelRow">
            <div className="channelInfo">
              <BookOpen size={18} color="#4F46E5" />
              <strong>LinkedIn Carousels</strong>
            </div>
            <div className="channelBarTrack">
              <div className="channelBarFill" style={{ width: "85%" }} />
            </div>
            <span>38 Packs</span>
          </div>

          <div className="analyticsWorkspace__channelRow">
            <div className="channelInfo">
              <Video size={18} color="#8B5CF6" />
              <strong>Camera Teleprompter Scripts</strong>
            </div>
            <div className="channelBarTrack">
              <div className="channelBarFill" style={{ width: "70%" }} />
            </div>
            <span>32 Scripts</span>
          </div>

          <div className="analyticsWorkspace__channelRow">
            <div className="channelInfo">
              <Send size={18} color="#06B6D4" />
              <strong>Substack Executive Newsletters</strong>
            </div>
            <div className="channelBarTrack">
              <div className="channelBarFill" style={{ width: "90%" }} />
            </div>
            <span>38 Essays</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default AnalyticsWorkspace;
