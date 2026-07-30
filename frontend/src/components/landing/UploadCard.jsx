import "./UploadCard.css";
import { Upload, Sparkles } from "lucide-react";

function UploadCard() {
  return (
    <div className="uploadCard">

      <div className="uploadCard__icon">
        <Upload size={28} />
      </div>

      <div className="uploadCard__info">
        <h3>Weekly Podcast.mp4</h3>
        <p>2.1 GB • AI Ready</p>
      </div>

      <button className="uploadCard__button">
        <Sparkles size={18} />
        Generate
      </button>

    </div>
  );
}

export default UploadCard;