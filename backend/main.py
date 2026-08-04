from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.router import api_router
from backend.core.config import settings
from backend.db.database import engine
from backend.models import Base  # Imports all models via __init__.py


from backend.middleware.request_id import RequestIDMiddleware
from backend.core.security_headers import SecurityHeadersMiddleware
from backend.middleware.rate_limiter import RateLimiterMiddleware

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)

# Add Middleware Stack
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimiterMiddleware)
app.add_middleware(RequestIDMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


app.include_router(api_router, prefix="/api/v1")
app.include_router(api_router)


@app.get("/")
def root():
    return {
        "message": f"{settings.APP_NAME} is running."
    }