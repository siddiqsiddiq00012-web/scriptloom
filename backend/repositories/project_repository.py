from sqlalchemy.orm import Session

from backend.models.project import Project


class ProjectRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_project(
        self,
        owner_id: int,
        name: str,
    ) -> Project:
        project = Project(
            owner_id=owner_id,
            name=name,
        )

        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)

        return project

    def get_all_by_owner(
        self,
        owner_id: int,
    ) -> list[Project]:
        return (
            self.db.query(Project)
            .filter(Project.owner_id == owner_id)
            .order_by(Project.id.desc())
            .all()
        )

    def get_by_id(
        self,
        project_id: int,
    ) -> Project | None:
        return (
            self.db.query(Project)
            .filter(Project.id == project_id)
            .first()
        )

    def get_by_id_and_owner(
        self,
        project_id: int,
        owner_id: int,
    ) -> Project | None:
        return (
            self.db.query(Project)
            .filter(
                Project.id == project_id,
                Project.owner_id == owner_id,
            )
            .first()
        )

    def update_project_name(
        self,
        project: Project,
        name: str,
    ) -> Project:
        project.name = name

        self.db.commit()
        self.db.refresh(project)

        return project

    def delete_project(
        self,
        project: Project,
    ) -> None:
        self.db.delete(project)
        self.db.commit()