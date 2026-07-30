from pydantic import BaseModel, ConfigDict


class MediaResponse(BaseModel):
    id: int
    project_id: int
    filename: str
    storage_path: str
    file_size: int
    status: str

    model_config = ConfigDict(
        from_attributes=True,
    )