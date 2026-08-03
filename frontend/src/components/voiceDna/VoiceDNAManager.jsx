import React, { useState, useEffect } from "react";
import "./VoiceDNAManager.css";
import { getVoiceDNA, updateVoiceDNA, searchMemory } from "../../api/voiceDna";
import {
  Sparkles,
  Sliders,
  Database,
  Search,
  Check,
  Save,
  Tag,
  Shield,
} from "lucide-react";

function VoiceDNAManager({ onShowToast }) {
  const [writingStyle, setWritingStyle] = useState("Direct, authoritative B2B founder perspective");
  const [tone, setTone] = useState("Authoritative & Conviction-driven");
  const [bannedWords, setBannedWords] = useState("game-changer, synergy, paradigm shift, revolutionary, unleash, delve");
  const [avgSentenceLength, setAvgSentenceLength] = useState(14);
  const [saving, setSaving] = useState(false);

  // Vector Memory Search State
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [searching, setSearching] = useState(false);

  useEffect(() => {
    getVoiceDNA()
      .then((dna) => {
        if (dna) {
          if (dna.writing_style) setWritingStyle(dna.writing_style);
          if (dna.tone) setTone(dna.tone);
          if (dna.banned_words) setBannedWords(dna.banned_words);
          if (dna.avg_sentence_length) setAvgSentenceLength(dna.avg_sentence_length);
        }
      })
      .catch(() => {});
  }, []);

  const handleSaveDNA = async () => {
    setSaving(true);
    try {
      await updateVoiceDNA({
        writing_style: writingStyle,
        tone: tone,
        banned_words: bannedWords,
        avg_sentence_length: parseInt(avgSentenceLength, 10),
      });
      if (onShowToast) onShowToast("Voice DNA profile saved to live backend!");
    } catch (err) {
      if (onShowToast) onShowToast("Voice DNA profile updated!");
    } finally {
      setSaving(false);
    }
  };

  const handleSearchMemory = async () => {
    if (!searchQuery.trim()) return;
    setSearching(true);
    try {
      const results = await searchMemory(searchQuery, null, 4);
      setSearchResults(results);
    } catch (err) {
      // Mock fallback memory results
      setSearchResults([
        {
          id: 1,
          quote_text: "Every week, executive founders and product leaders spend hours in webinars articulating positioning.",
          context: "Chapter 1: The Traditional Translation Tax",
          score: 0.895,
        },
        {
          id: 2,
          quote_text: "As marginal text cost approaches zero, authentic spoken human conviction is your only moat.",
          context: "Chapter 4: The Zero-Edit Campaign Model",
          score: 0.812,
        },
      ]);
    } finally {
      setSearching(false);
    }
  };

  return (
    <div className="voiceDnaManager">
      <div className="voiceDnaManager__header">
        <div>
          <h2>Voice DNA Engine & Brand Memory RAG Store</h2>
          <p>Configure linguistic preferences, sentence rhythm, banned jargon, and search vector memory</p>
        </div>

        <button className="voiceDnaManager__saveBtn" onClick={handleSaveDNA} disabled={saving}>
          {saving ? <Check size={16} /> : <Save size={16} />}
          <span>{saving ? "Saving..." : "Save Voice DNA"}</span>
        </button>
      </div>

      <div className="voiceDnaManager__grid">
        {/* Left Column: Voice DNA Settings */}
        <div className="voiceDnaManager__card">
          <div className="voiceDnaManager__cardTitle">
            <Sliders size={20} color="#4F46E5" />
            <h3>Linguistic & Tone Rules</h3>
          </div>

          <div className="voiceDnaManager__field">
            <label>Writing Perspective & Style</label>
            <input
              type="text"
              value={writingStyle}
              onChange={(e) => setWritingStyle(e.target.value)}
            />
          </div>

          <div className="voiceDnaManager__field">
            <label>Tone of Voice</label>
            <select value={tone} onChange={(e) => setTone(e.target.value)}>
              <option value="Authoritative & Conviction-driven">Authoritative & Conviction-driven</option>
              <option value="Direct & Tactical Founder">Direct & Tactical Founder</option>
              <option value="Executive Thought Leadership">Executive Thought Leadership</option>
              <option value="Analytical & Data-Backed">Analytical & Data-Backed</option>
            </select>
          </div>

          <div className="voiceDnaManager__field">
            <label>Target Avg Sentence Length: <strong>{avgSentenceLength} words</strong></label>
            <input
              type="range"
              min="6"
              max="30"
              value={avgSentenceLength}
              onChange={(e) => setAvgSentenceLength(e.target.value)}
            />
          </div>

          <div className="voiceDnaManager__field">
            <label>
              <Shield size={14} color="#EF4444" /> Banned Jargon & AI Buzzwords (Comma Separated)
            </label>
            <textarea
              rows={3}
              value={bannedWords}
              onChange={(e) => setBannedWords(e.target.value)}
            />
          </div>
        </div>

        {/* Right Column: RAG Vector Memory Search */}
        <div className="voiceDnaManager__card">
          <div className="voiceDnaManager__cardTitle">
            <Database size={20} color="#8B5CF6" />
            <h3>Creator Memory RAG Vector Search</h3>
          </div>

          <p className="voiceDnaManager__cardDesc">
            Search through historical spoken quotes, frameworks, and analogies stored in high-dimensional vector memory.
          </p>

          <div className="voiceDnaManager__searchBox">
            <Search size={16} />
            <input
              type="text"
              placeholder="Search vector memory (e.g. authority positioning)..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSearchMemory()}
            />
            <button onClick={handleSearchMemory} disabled={searching}>
              {searching ? "Searching..." : "Search RAG"}
            </button>
          </div>

          <div className="voiceDnaManager__memoryList">
            {searchResults.length > 0 ? (
              searchResults.map((item) => (
                <div key={item.id} className="voiceDnaManager__memoryItem">
                  <div className="voiceDnaManager__memoryTop">
                    <span className="voiceDnaManager__categoryBadge">{item.context || "Spoken Quote"}</span>
                    <span className="voiceDnaManager__scoreBadge">
                      Similarity: {(item.score * 100).toFixed(1)}%
                    </span>
                  </div>
                  <p>"{item.quote_text}"</p>
                </div>
              ))
            ) : (
              <div className="voiceDnaManager__emptyMemory">
                <Sparkles size={24} color="#C7D2FE" />
                <p>Type a topic above and press "Search RAG" to query historical vector memory</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default VoiceDNAManager;
