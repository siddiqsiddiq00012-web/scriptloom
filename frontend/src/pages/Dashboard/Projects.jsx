import { useEffect, useState } from "react";
import "./Projects.css";
import { FolderPlus, FolderOpen } from "lucide-react";
import { getProjects } from "../../api/projects";

export default function Projects() {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadProjects();
  }, []);

  async function loadProjects() {
    try {
      const data = await getProjects();
      setProjects(data || []);
    } catch (err) {
      console.error(err);
      setProjects([]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="projectsPage">

      <div className="projectsPage__header">

        <div>
          <h1>Projects</h1>

          <p>
            Every uploaded resource belongs to a project.
          </p>

        </div>

        <button className="projectsPage__button">

          <FolderPlus size={18} />

          New Project

        </button>

      </div>

      {loading ? (

        <div className="projectsPage__loading">

          Loading projects...

        </div>

      ) : projects.length === 0 ? (

        <div className="projectsPage__empty">

          <FolderOpen size={56} />

          <h2>No projects yet</h2>

          <p>Create your first project to begin.</p>

        </div>

      ) : (

        <div className="projectsPage__grid">

          {projects.map((project) => (

            <div
              className="projectsPage__card"
              key={project.id}
            >

              <h3>{project.name}</h3>

              <p>
                {project.description || "No description"}
              </p>

            </div>

          ))}

        </div>

      )}

    </div>
  );
}