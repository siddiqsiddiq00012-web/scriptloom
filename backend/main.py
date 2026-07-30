from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.router import api_router
from backend.core.config import settings
from backend.db.database import engine
from backend.models import Base  # Imports all models via __init__.py


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


app.include_router(api_router)


@app.get("/")
def root():
    return {
        "message": f"{settings.APP_NAME} is running."
    }