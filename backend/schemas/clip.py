from pydantic import BaseModel, ConfigDict, Field


class ClipCreate(BaseModel):
    media_id: int

    title: str = Field(
        min_length=1,
        max_length=255,
    )

    start_time: int = Field(
        ge=0,
    )

    end_time: int = Field(
        gt=0,
    )


class ClipUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    start_time: int | None = Field(
        default=None,
        ge=0,
    )

    end_time: int | None = Field(
        default=None,
        gt=0,
    )

    status: str | None = None

    output_path: str | None = None


class ClipResponse(BaseModel):
    id: int
    project_id: int
    media_id: int
    title: str
    start_time: int
    end_time: int
    status: str
    output_path: str | None

    model_config = ConfigDict(
        from_attributes=True,
    )