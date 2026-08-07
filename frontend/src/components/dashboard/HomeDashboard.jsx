import "./HomeDashboard.css";
import { Plus, FolderOpen, UploadCloud, Scissors } from "lucide-react";

export default function HomeDashboard() {
  return (
    <div className="homeDashboard">
      <div className="homeDashboard__hero">
        <div>
          <h1>Welcome to Scriptloom</h1>
          <p>
            Turn one long-form video into multiple short-form content assets.
          </p>
        </div>

        <button className="homeDashboard__primaryButton">
          <Plus size={18} />
          Create Project
        </button>
      </div>

      <div className="homeDashboard__grid">

        <div className="homeDashboard__card">
          <FolderOpen size={26} />
          <h3>Projects</h3>
          <p>Create and manage your content projects.</p>
        </div>

        <div className="homeDashboard__card">
          <UploadCloud size={26} />
          <h3>Upload Resource</h3>
          <p>Upload podcasts, interviews, webinars or videos.</p>
        </div>

        <div className="homeDashboard__card">
          <Scissors size={26} />
          <h3>Generate Clips</h3>
          <p>Generate viral clips using your existing AI pipeline.</p>
        </div>

      </div>

      <div className="homeDashboard__recent">
        <h2>Recent Projects</h2>

        <div className="homeDashboard__empty">
          No projects yet.
          <br />
          Create your first project to begin.
        </div>
      </div>
    </div>
  );
}