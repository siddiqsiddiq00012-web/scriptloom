import "./ResourceWorkspace.css";

export default function ResourceWorkspace() {
  return (
    <div className="resource-workspace">
      <header className="workspace-header">
        <h1>Scriptloom</h1>
        <p>Turn one resource into content for every platform.</p>
      </header>

      <section className="workspace-grid">

        <div className="workspace-card">
          <h2>Create from a Resource</h2>

          <p>Upload a video to begin.</p>

          <button className="primary-btn">
            Upload Resource
          </button>

          <small>
            Supported: MP4 • MOV • MKV
          </small>
        </div>

        <div className="workspace-card">
          <h2>Recent Projects</h2>

          <ul>
            <li>No projects yet</li>
          </ul>
        </div>

        <div className="workspace-card">
          <h2>Continue Working</h2>

          <ul>
            <li>No active processing jobs</li>
          </ul>
        </div>

        <div className="workspace-card">
          <h2>Quick Actions</h2>

          <button disabled>Generate Clips</button>
          <button disabled>Content Studio</button>
          <button disabled>Media Library</button>

          <small>Available after uploading a resource.</small>
        </div>

      </section>
    </div>
  );
}