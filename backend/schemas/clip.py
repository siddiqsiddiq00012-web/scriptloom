from pydantic import BaseModel, ConfigDict, Field


class ClipCreate(BaseModel):
    media_id: int

    title: str = Field(
        min_length=1,
        max_length=255,
    )

    start_time: float = Field(
        ge=0,
    )

    end_time: float = Field(
        gt=0,
    )


class ClipUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    start_time: float | None = Field(
        default=None,
        ge=0,
    )

    end_time: float | None = Field(
        default=None,
        gt=0,
    )

    output_path: str | None = None


class ClipResponse(BaseModel):
    id: int
    project_id: int
    media_id: int
    title: str
    start_time: float
    end_time: float
    reason: str
    output_path: str | None
    subtitle_path: str | None = None

    model_config = ConfigDict(
        from_attributes=True,
    )
