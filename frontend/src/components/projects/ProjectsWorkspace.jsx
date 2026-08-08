import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import "./ProjectsWorkspace.css";
import { Folder, Plus, Search, ArrowUpRight, FolderPlus } from "lucide-react";
import { getProjects, createProject, deleteProject } from "../../api/projects";
import { getProjectMedia } from "../../api/media";
import { Modal, ConfirmDialog, SkeletonGrid, EmptyState } from "../ui";

function ProjectsWorkspace() {
  const navigate = useNavigate();
  const [search, setSearch] = useState("");
  const [projectsList, setProjectsList] = useState([]);
  const [mediaCounts, setMediaCounts] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showCreate, setShowCreate] = useState(false);
  const [newName, setNewName] = useState("");
  const [creating, setCreating] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState(null);

  const fetchProjectsData = useCallback(async () => {
    const data = await getProjects();
    const projects = Array.isArray(data) ? data : [];
    const counts = {};
    await Promise.all(
      projects.map(async (p) => {
        try {
          const media = await getProjectMedia(p.id);
          counts[p.id] = Array.isArray(media) ? media.length : 0;
        } catch {
          counts[p.id] = 0;
        }
      })
    );
    return { projects, mediaCounts: counts };
  }, []);

  const loadData = useCallback(() => {
    return fetchProjectsData()
      .then(({ projects, mediaCounts }) => {
        setError("");
        setProjectsList(projects);
        setMediaCounts(mediaCounts);
      })
      .catch((err) => setError(err.message || "Failed to load projects."))
      .finally(() => setLoading(false));
  }, [fetchProjectsData]);

  useEffect(() => { loadData(); }, [loadData]);

  const handleCreate = async () => {
    if (!newName.trim()) return;
    setCreating(true);
    try {
      const newProj = await createProject({ name: newName.trim() });
      setProjectsList((prev) => [...prev, newProj]);
      setMediaCounts((prev) => ({ ...prev, [newProj.id]: 0 }));
      setShowCreate(false);
      setNewName("");
    } catch (err) {
      setError(err.message || "Failed to create project.");
    } finally {
      setCreating(false);
    }
  };

  const handleDelete = async () => {
    if (!deleteTarget) return;
    try {
      await deleteProject(deleteTarget.id);
      setProjectsList((prev) => prev.filter((p) => p.id !== deleteTarget.id));
      setDeleteTarget(null);
    } catch (err) {
      setError(err.message || "Failed to delete project.");
      setDeleteTarget(null);
    }
  };

  const filtered = projectsList.filter((p) =>
    (p.name || "").toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="animate-fadeIn">
      <div className="projects__header">
        <div>
          <h2 className="projects__title">Projects</h2>
          <p className="projects__subtitle">Organize your source media and generated content by project.</p>
        </div>
        <button className="btn btn-primary" onClick={() => setShowCreate(true)}>
          <Plus size={16} /> New Project
        </button>
      </div>

      {error && <div className="projects__error">{error}</div>}

      <div className="projects__toolbar">
        <div className="projects__search">
          <Search size={16} />
          <input type="text" placeholder="Search projects..." value={search} onChange={(e) => setSearch(e.target.value)} />
        </div>
      </div>

      {loading ? (
        <SkeletonGrid count={3} />
      ) : filtered.length === 0 && projectsList.length === 0 ? (
        <EmptyState
          icon={FolderPlus}
          title="No Projects Yet"
          description="Create your first project to start uploading media and generating content."
          action={<button className="btn btn-primary" onClick={() => setShowCreate(true)}><Plus size={16} /> Create Your First Project</button>}
        />
      ) : filtered.length === 0 ? (
        <EmptyState icon={Search} title="No Matching Projects" description={`No projects match "${search}". Try a different search term.`} />
      ) : (
        <div className="projects__grid">
          {filtered.map((proj, i) => (
            <div key={proj.id} className={`projects__card card card-hover animate-fadeInUp stagger-${Math.min(i + 1, 6)}`}>
              <div className="projects__cardTop">
                <div className="projects__folderIcon"><Folder size={20} color="var(--primary)" /></div>
                <button className="btn btn-ghost btn-sm" onClick={() => setDeleteTarget(proj)} aria-label="Delete project">✕</button>
              </div>
              <h3 className="projects__cardName">{proj.name}</h3>
              <div className="projects__cardMeta">
                <span>{mediaCounts[proj.id] ?? 0} sources</span>
              </div>
              <button className="projects__openBtn" onClick={() => navigate(`/projects/${proj.id}`)}>
                Open Project <ArrowUpRight size={15} />
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Create Modal */}
      <Modal
        isOpen={showCreate}
        onClose={() => { setShowCreate(false); setNewName(""); }}
        title="New Project"
        footer={
          <>
            <button className="btn btn-secondary" onClick={() => { setShowCreate(false); setNewName(""); }}>Cancel</button>
            <button className="btn btn-primary" onClick={handleCreate} disabled={!newName.trim() || creating}>
              {creating ? "Creating..." : "Create Project"}
            </button>
          </>
        }
      >
        <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
          <label style={{ fontSize: "13px", fontWeight: 600, color: "var(--text-secondary)" }}>Project Name</label>
          <input className="input" type="text" placeholder="e.g., My Podcast, Interview Series" value={newName} onChange={(e) => setNewName(e.target.value)} onKeyDown={(e) => e.key === "Enter" && handleCreate()} autoFocus />
        </div>
      </Modal>

      {/* Delete Confirmation */}
      <ConfirmDialog
        isOpen={!!deleteTarget}
        onClose={() => setDeleteTarget(null)}
        onConfirm={handleDelete}
        title="Delete Project"
        message={`Are you sure you want to delete "${deleteTarget?.name}" and all of its media? This action cannot be undone.`}
        confirmLabel="Delete"
        danger
      />
    </div>
  );
}

export default ProjectsWorkspace;
