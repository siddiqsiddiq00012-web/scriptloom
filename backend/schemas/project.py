from pydantic import BaseModel, ConfigDict, Field


class ProjectCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=255,
    )


class ProjectUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )


class ProjectResponse(BaseModel):
    id: int
    owner_id: int
    name: str

    model_config = ConfigDict(
        from_attributes=True,
    )