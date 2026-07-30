import "./LandingDashboard.css";

import UploadCard from "./UploadCard";
import Queue from "./Queue";
import Analytics from "./Analytics";
import PlatformIcons from "./PlatformIcons";

function LandingDashboard() {
  return (
    <div className="hero__right">
      <div className="dashboard">

        <div className="dashboard__top">
          <div className="dots">
            <span></span>
            <span></span>
            <span></span>
          </div>

          <div className="dashboard__title">
            Scriptloom Dashboard
          </div>

          <div className="dashboard__status">
            AI
          </div>
        </div>

        <div className="dashboard__content">
          <UploadCard />
          <Queue />
          <Analytics />
          <PlatformIcons />
        </div>

      </div>
    </div>
  );
}

export default LandingDashboard;