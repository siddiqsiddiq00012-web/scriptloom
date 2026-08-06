import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./ProjectsWorkspace.css";
import { Folder, Plus, Search, ArrowUpRight, Sparkles, FolderPlus } from "lucide-react";
import { getProjects, createProject } from "../../api/projects";

function ProjectsWorkspace({ onOpenUpload }) {
  const navigate = useNavigate();
  const [search, setSearch] = useState("");
  const [projectsList, setProjectsList] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    getProjects()
      .then((data) => {
        if (Array.isArray(data)) {
          setProjectsList(data);
        } else if (data && data.id) {
          setProjectsList([data]);
        }
      })
      .catch(() => {
        setProjectsList([]);
      })
      .finally(() => setLoading(false));
  }, []);

  const handleCreateNewProject = async () => {
    const name = window.prompt("Enter new project name:", "My Content Project");
    if (!name) return;
    
    try {
      const newProj = await createProject({
        name: name,
        description: "Organize multi-channel content packs",
      });
      if (newProj) {
        setProjectsList([...projectsList, newProj]);
      }
    } catch (err) {
      console.error("Failed to create project", err);
    }
  };

  const filtered = projectsList.filter((p) =>
    (p.name || p.title || "").toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="projectsWorkspace">
      <div className="projectsWorkspace__header">
        <div>
          <h2>Projects Workspace</h2>
          <p>Organize content campaigns, media assets, and generated deliverables</p>
        </div>

        <button className="projectsWorkspace__btnPrimary" onClick={handleCreateNewProject}>
          <Plus size={16} /> Create Content Project
        </button>
      </div>

      <div className="projectsWorkspace__toolbar">
        <div className="projectsWorkspace__search">
          <Search size={16} />
          <input
            type="text"
            placeholder="Search projects by title..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
      </div>

      {filtered.length === 0 ? (
        <div className="mediaLibrary__emptyCard">
          <div className="mediaLibrary__emptyIconBox">
            <FolderPlus size={40} color="#4F46E5" />
          </div>
          <h3>No Content Projects Created Yet</h3>
          <p>
            Create your first content project to organize recordings, LinkedIn carousels, newsletters, and video scripts.
          </p>
          <button className="projectsWorkspace__btnPrimary" onClick={handleCreateNewProject}>
            <Plus size={16} /> Create Your First Project
          </button>
        </div>
      ) : (
        <div className="projectsWorkspace__grid">
          {filtered.map((proj) => (
            <div key={proj.id} className="projectsWorkspace__card">
              <div className="projectsWorkspace__cardHeader" style={{ display: 'flex', justifyContent: 'space-between', width: '100%' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <div className="projectsWorkspace__folderIcon">
                    <Folder size={20} color="#4F46E5" />
                  </div>
                  <span className="projectsWorkspace__badge">{proj.category || "Active Project"}</span>
                </div>
                <button 
                  style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#dc2626' }}
                  onClick={async (e) => {
                    e.stopPropagation();
                    if(window.confirm("Are you sure you want to delete this project?")) {
                      try {
                        const { deleteProject } = await import("../../api/projects");
                        await deleteProject(proj.id);
                        setProjectsList(projectsList.filter(p => p.id !== proj.id));
                      } catch(err) {
                        console.error("Failed to delete", err);
                      }
                    }
                  }}
                >
                  Delete
                </button>
              </div>

              <h3>{proj.name || proj.title}</h3>
              <p className="projectsWorkspace__date">Updated {proj.updated_at ? new Date(proj.updated_at).toLocaleDateString() : "Just now"}</p>

              <div className="projectsWorkspace__stats">
                <div>
                  <strong>{proj.mediaCount || 0}</strong>
                  <span>Recordings</span>
                </div>
                <div>
                  <strong>{proj.packsCount || 0}</strong>
                  <span>Campaign Packs</span>
                </div>
              </div>

              <button className="projectsWorkspace__openBtn" onClick={() => navigate(`/projects/${proj.id}`)}>
                <span>Open Project</span>
                <ArrowUpRight size={16} />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default ProjectsWorkspace;
