import React, { useState } from "react";
import "./PublishingQueue.css";
import { Send, Clock, CheckCircle2, Copy, Download, Calendar } from "lucide-react";

function PublishingQueue({ onShowToast }) {
  const [queueItems, setQueueItems] = useState([
    {
      id: 1,
      title: "The End of Commodity Marketing (Substack Newsletter)",
      scheduled_for: "Tomorrow, 9:00 AM",
      channel: "Substack",
      status: "Scheduled",
    },
    {
      id: 2,
      title: "Spoken Conviction Gap (LinkedIn Carousel)",
      scheduled_for: "Friday, 2:00 PM",
      channel: "LinkedIn",
      status: "Scheduled",
    },
    {
      id: 3,
      title: "B2B Positioning Teleprompter Script",
      scheduled_for: "Monday, 10:30 AM",
      channel: "YouTube Shorts",
      status: "Scheduled",
    },
  ]);

  const handlePublishNow = (id, title) => {
    setQueueItems(queueItems.map((item) => (item.id === id ? { ...item, status: "Published" } : item)));
    if (onShowToast) onShowToast(`Published "${title}" live!`);
  };

  return (
    <div className="publishingQueue">
      <div className="publishingQueue__header">
        <div>
          <h2>Publishing Queue & Channel Sync</h2>
          <p>Schedule, preview, and deploy multi-platform campaign assets</p>
        </div>
      </div>

      <div className="publishingQueue__list">
        {queueItems.map((item) => (
          <div key={item.id} className="publishingQueue__card">
            <div className="publishingQueue__left">
              <div className="publishingQueue__iconBox">
                <Send size={20} color="#4F46E5" />
              </div>
              <div>
                <h3>{item.title}</h3>
                <p>
                  <Calendar size={13} /> {item.scheduled_for} • <strong>{item.channel}</strong>
                </p>
              </div>
            </div>

            <div className="publishingQueue__right">
              <span className={`publishingQueue__badge ${item.status === "Published" ? "badge--done" : ""}`}>
                {item.status === "Published" ? <CheckCircle2 size={12} /> : <Clock size={12} />}
                {item.status}
              </span>

              {item.status !== "Published" && (
                <button
                  className="publishingQueue__btnPublish"
                  onClick={() => handlePublishNow(item.id, item.title)}
                >
                  Publish Now
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default PublishingQueue;
