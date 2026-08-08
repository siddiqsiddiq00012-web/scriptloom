# Scriptloom

**One Resource. Infinite Content.**

Scriptloom is an AI-powered content repurposing platform that transforms uploaded video and audio resources into multi-platform, publish-ready campaign assets. Upload a recording, get a timestamped transcript, generate AI-curated clips, and produce real content for LinkedIn, X/Twitter, newsletters, blogs, and more — all powered by the actual content of your resource.

---

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
  - [Environment Variables](#environment-variables)
- [Project Structure](#project-structure)
- [API Reference](#api-reference)
- [Core Pipeline](#core-pipeline)
- [AI Content Generation](#ai-content-generation)
- [Storage](#storage)
- [Deployment](#deployment)
- [License](#license)

---

## Features

### Resource Management
- Upload video and audio files (MP4, MOV, MP3, WAV, WebM, and more)
- Automatic metadata extraction via FFprobe (duration, codec, resolution, bitrate, FPS)
- Project-based organization with full ownership controls

### Transcription
- Speech-to-text transcription via Whisper (faster-whisper)
- Timestamped transcript segments with speaker detection
- Inline transcript editing with segment-level precision

### AI Clip Generation
- Gemini-powered clip selection that identifies the most compelling moments
- FFmpeg-based clip extraction with configurable output
- Frame-accurate start/end time controls
- Streaming clip playback in the browser

### AI Content Studio
- Generate real AI content from your transcript using Gemini
- **9 content types supported:**
  - **Social:** LinkedIn Post, X/Twitter Thread, Instagram Caption
  - **Long-form:** Newsletter, Blog Article, Video Script
  - **Ideas:** Content Hooks, Titles & Headlines, Content Ideas
- Per-type generation with tone, audience, length, and custom instruction controls
- Copy, view, and delete generated assets
- Content persists across sessions

### Voice & Style Controls
- Per-user tone and style preferences that shape AI output
- Banned-word filtering to remove AI jargon from generated content
- Ensures generated content matches the creator's authentic voice

### Webhooks & Integrations
- Configurable webhook endpoints with HMAC signature verification
- Event-based delivery with retry logic
- Test ping and delivery log inspection

### Export Engine
- Single-asset export as Markdown, TXT, or JSON
- Campaign pack ZIP export with all generated assets
- Format-validated with proper Content-Disposition headers

### Profile & Account
- Full profile customization (name, bio, company, role, timezone)
- Profile completion indicator
- Password management
- Account data export (JSON)
- Account deletion with confirmation

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Frontend (React)                     │
│  Vite + React 19 · React Router · Lucide Icons          │
│  http://localhost:5173                                   │
└──────────────────────┬──────────────────────────────────┘
                       │ /api/v1 proxy
┌──────────────────────▼──────────────────────────────────┐
│                   Backend (FastAPI)                       │
│  Python · SQLAlchemy · Pydantic · Uvicorn                │
│  http://localhost:8000                                   │
└──────────────────────┬──────────────────────────────────┘
                       │
    ┌──────────┬───────┼───────┬──────────┐
    │          │       │       │          │
┌───▼───┐ ┌───▼───┐ ┌─▼─┐ ┌───▼───┐ ┌───▼────┐
│  DB   │ │ Redis │ │AI │ │Celery │ │Storage │
│PG/SQL │ │Queue  │ │Gem│ │Worker │ │Local/R2│
└───────┘ └───────┘ └───┘ └───────┘ └────────┘
```

---

## Tech Stack

### Backend
| Component | Technology |
|-----------|-----------|
| Framework | FastAPI |
| ORM | SQLAlchemy 2.0 |
| Validation | Pydantic v2 |
| Database | PostgreSQL (production) / SQLite (development) |
| Task Queue | Celery + Redis |
| STT | faster-whisper (Whisper) |
| AI | Google Gemini (gemini-3.6-flash) |
| Video Processing | FFmpeg / FFprobe |
| Auth | JWT (python-jose) + bcrypt |
| Storage | Local filesystem / Cloudflare R2 (S3-compatible) |
| Server | Uvicorn |

### Frontend
| Component | Technology |
|-----------|-----------|
| Framework | React 19 |
| Build Tool | Vite 8 |
| Routing | React Router 7 |
| Icons | Lucide React |
| Animation | Framer Motion |
| OAuth | Google Identity Services (@react-oauth/google) |
| HTTP | Native fetch with custom API client |

---

## Getting Started

### Prerequisites

- **Python 3.11+**
- **Node.js 18+** and npm
- **FFmpeg** and **FFprobe** installed and on PATH
- **Redis** (for Celery task queue)
- **PostgreSQL** (recommended) or SQLite for development

### Backend Setup

```bash
# Clone the repository
git clone https://github.com/your-org/scriptloom.git
cd scriptloom

# Create and activate a virtual environment
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables (see below)
cp .env.example .env
# Edit .env with your configuration

# Start the backend server
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

The API documentation is available at `http://localhost:8000/docs`.

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment variables
cp .env.example .env
# Edit .env with your configuration

# Start the development server
npm run dev
```

The application is available at `http://localhost:5173`.

### Environment Variables

#### Backend (`.env`)

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | Database connection string (e.g., `postgresql+psycopg://user:pass@localhost:5432/scriptloom`) |
| `SECRET_KEY` | Yes | JWT signing secret (generate a strong random string) |
| `GEMINI_API_KEY` | Yes | Google Gemini API key for AI generation |
| `GOOGLE_CLIENT_ID` | Yes | Google OAuth client ID for sign-in |
| `REDIS_URL` | No | Redis connection string (default: `redis://localhost:6379/0`) |
| `CELERY_BROKER_URL` | No | Celery broker URL (defaults to Redis) |
| `CELERY_RESULT_BACKEND` | No | Celery result backend (defaults to Redis) |
| `OPENAI_API_KEY` | No | OpenAI API key (optional, for alternative AI providers) |
| `ALLOWED_ORIGINS` | Yes | JSON array of allowed CORS origins |

#### Frontend (`frontend/.env`)

| Variable | Required | Description |
|----------|----------|-------------|
| `VITE_GOOGLE_CLIENT_ID` | Yes | Google OAuth client ID |
| `VITE_API_URL` | No | API base URL (default: `/api/v1`) |

---

## Project Structure

```
scriptloom/
├── backend/
│   ├── ai/
│   │   ├── prompts/              # AI prompt templates
│   │   │   ├── clip_selection.md
│   │   │   ├── clip_prompt.txt
│   │   │   └── content_generation.md
│   │   └── services/
│   │       ├── gemini_service.py  # Gemini API client
│   │       └── clip_selector.py   # OpenAI clip selector (optional)
│   ├── api/                       # FastAPI route handlers
│   │   ├── auth.py                # Registration, login, Google OAuth
│   │   ├── users.py               # Profile management
│   │   ├── projects.py            # CRUD + PATCH
│   │   ├── uploads.py             # File upload, streaming, waveform
│   │   ├── transcripts.py         # Transcription, segments
│   │   ├── clips.py               # Clip listing and streaming
│   │   ├── generation.py          # AI content generation
│   │   ├── processing.py          # Video processing jobs
│   │   ├── exports.py             # Single/batch export
│   │   ├── billing.py             # Subscription and usage
│   │   ├── webhooks.py            # Webhook CRUD + delivery
│   │   ├── stream.py              # SSE progress streaming
│   │   ├── health.py              # Health checks
│   │   ├── root.py                # Root endpoint
│   │   └── router.py              # Router registration
│   ├── core/
│   │   ├── config.py              # Pydantic settings
│   │   ├── dependencies.py        # Auth + ownership verification
│   │   ├── security.py            # Password hashing (bcrypt)
│   │   └── security_headers.py    # Security middleware
│   ├── db/
│   │   ├── database.py            # Engine + session factory
│   │   └── dependencies.py        # DB session dependency
│   ├── events/
│   │   └── event_bus.py           # Internal event system
│   ├── jobs/
│   │   └── tasks/
│   │       ├── video_processing.py # Celery task
│   │       └── webhook_delivery.py # Webhook dispatch task
│   ├── middleware/
│   │   ├── rate_limiter.py        # Redis-based rate limiting
│   │   └── request_id.py          # Request ID injection
│   ├── models/                    # SQLAlchemy ORM models
│   │   ├── user.py
│   │   ├── project.py
│   │   ├── media.py
│   │   ├── transcript.py
│   │   ├── clip.py
│   │   ├── generated_content.py
│   │   ├── processing_job.py
│   │   ├── billing.py
│   │   ├── webhook.py
│   │   └── base.py
│   ├── processing/
│   │   └── pipeline/
│   │       └── service.py         # Orchestration pipeline
│   ├── repositories/              # Data access layer
│   ├── schemas/                   # Pydantic request/response schemas
│   ├── services/                  # Business logic
│   │   ├── auth_service.py
│   │   ├── upload_service.py
│   │   ├── media_pipeline.py
│   │   ├── processing_service.py
│   │   ├── generation_engine.py   # Legacy campaign pack
│   │   ├── content_generator.py   # Real Gemini content generation
│   │   ├── export_engine.py
│   │   ├── webhook_service.py
│   │   ├── billing_service.py
│   │   └── ffprobe_service.py
│   ├── storage/
│   │   ├── local.py               # Local filesystem storage
│   │   ├── r2.py                  # Cloudflare R2 (S3) storage
│   │   └── manager.py             # Storage abstraction
│   └── main.py                    # Application entry point
│
├── frontend/
│   ├── src/
│   │   ├── api/                   # API client modules
│   │   │   ├── client.js          # Base HTTP client with auth
│   │   │   ├── auth.js
│   │   │   ├── projects.js
│   │   │   ├── media.js
│   │   │   ├── clips.js
│   │   │   ├── generation.js
│   │   │   ├── processing.js
│   │   │   ├── exports.js
│   │   │   └── users.js
│   │   ├── components/
│   │   │   ├── auth/              # Login, Register, Google OAuth
│   │   │   ├── landing/           # Landing page, Hero, Navbar
│   │   │   ├── layout/            # App shell, navigation
│   │   │   ├── media/             # Media library, upload
│   │   │   ├── projects/          # Project workspace
│   │   │   ├── settings/          # Settings (Profile, Preferences, Billing, Webhooks, Account)
│   │   │   ├── ui/                # Shared UI components
│   │   │   ├── common/            # Common shared components
│   │   │   └── workspace/         # Resource workspace (tabs, clips, content studio)
│   │   ├── pages/
│   │   │   ├── Auth/              # Login, Register pages
│   │   │   ├── App/               # Dashboard, ProjectDetail
│   │   │   └── Landing/           # Landing page
│   │   ├── routes/                # React Router configuration
│   │   ├── services/              # SSE progress streaming
│   │   ├── config.js              # Environment config
│   │   └── main.jsx               # Application entry point
│   ├── package.json
│   └── vite.config.js
│
├── alembic/                       # Database migrations
├── requirements.txt
└── README.md
```

---

## API Reference

All endpoints are prefixed with `/api/v1`.

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/auth/register` | Register a new account |
| `POST` | `/auth/login` | Sign in with email/password |
| `POST` | `/auth/google` | Sign in with Google OAuth |
| `GET` | `/auth/me` | Get current user |
| `POST` | `/auth/forgot-password` | Request password reset |

### Users
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/users/me` | Get profile |
| `PUT` | `/users/me` | Update profile (name, bio, company, role, timezone) |
| `POST` | `/users/me/change-password` | Change password |
| `DELETE` | `/users/me` | Delete account |
| `GET` | `/users/me/export` | Export account data |

### Projects
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/projects` | List user projects |
| `POST` | `/projects` | Create project |
| `GET` | `/projects/{id}` | Get project |
| `PATCH` | `/projects/{id}` | Update project |
| `DELETE` | `/projects/{id}` | Delete project |

### Media
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/projects/{id}/media` | Upload media file |
| `GET` | `/projects/{id}/media` | List project media |
| `GET` | `/projects/media/{id}` | Get media details |
| `GET` | `/projects/media/{id}/stream` | Stream media file |
| `GET` | `/projects/media/{id}/waveform` | Get waveform data |
| `DELETE` | `/projects/media/{id}` | Delete media |

### Transcription
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/media/{id}/transcribe` | Start transcription (Whisper) |
| `GET` | `/media/{id}/transcript` | Get transcript |
| `PUT` | `/transcripts/segments/{id}` | Edit segment |

### Clips
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/clips/project/{id}` | List project clips |
| `GET` | `/clips/{id}/stream` | Stream clip file |

### AI Content Generation
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/generation/content-types` | List available content types |
| `POST` | `/generation/media/{id}/generate` | Generate content from transcript |
| `GET` | `/generation/media/{id}/content` | Get all generated content (grouped by type) |
| `GET` | `/generation/campaign-pack/{id}` | Get legacy campaign pack |
| `POST` | `/generation/campaign-pack/{id}` | Generate legacy campaign pack |
| `PUT` | `/generation/content/{id}` | Edit generated content |
| `DELETE` | `/generation/content/{id}` | Delete generated content |

### Processing
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/processing/process` | Start video processing |
| `GET` | `/processing/jobs` | List user's processing jobs |
| `GET` | `/processing/jobs/{id}` | Get job status |
| `GET` | `/processing/media/{id}/jobs/latest` | Get latest job for media |

### Export
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/export/content/{id}?format=` | Export single asset (markdown/txt/json) |
| `GET` | `/export/campaign-pack/{id}` | Export all as ZIP |

### SSE Progress
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/stream/progress/{media_id}` | Subscribe to processing progress events |

### Webhooks
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/webhooks/endpoints` | List endpoints |
| `POST` | `/webhooks/endpoints` | Create endpoint |
| `PUT` | `/webhooks/endpoints/{id}` | Update endpoint |
| `DELETE` | `/webhooks/endpoints/{id}` | Delete endpoint |
| `POST` | `/webhooks/endpoints/{id}/test` | Send test ping |
| `GET` | `/webhooks/endpoints/{id}/deliveries` | Get delivery logs |

---

## Core Pipeline

The processing pipeline transforms a raw upload into publish-ready content:

```
Upload (MP4/MOV/WAV/MP3/WebM)
  │
  ├─► Metadata Extraction (FFprobe)
  │     Duration, codec, resolution, bitrate, FPS
  │
  ├─► Audio Extraction (FFmpeg)
  │     Isolated audio track for transcription
  │
  ├─► Waveform Generation (FFmpeg)
  │     Peak data for visual waveform display
  │
  ├─► Transcription (Whisper)
  │     Timestamped text segments with speaker labels
  │
  ├─► AI Clip Selection (Gemini)
  │     Identifies compelling moments from transcript
  │
  ├─► Clip Extraction (FFmpeg)
  │     Frame-accurate video clips with metadata
  │
  └─► AI Content Generation (Gemini)
        Platform-specific content from transcript
```

---

## AI Content Generation

Scriptloom uses Google Gemini to generate real content from your transcripts. Unlike template-based systems, every piece of content is generated from the actual spoken content of your resource.

### Supported Content Types

| Type | Category | Output |
|------|----------|--------|
| LinkedIn Post | Social | Professional post with hook and insight |
| X/Twitter Thread | Social | 5-8 tweet thread with narrative arc |
| Instagram Caption | Social | Caption with hashtags |
| Newsletter | Long-form | Email newsletter in markdown |
| Blog Article | Long-form | SEO-friendly article with sections |
| Video Script | Long-form | Short-form script with visual cues |
| Content Hooks | Ideas | 10 powerful opening hooks |
| Titles & Headlines | Ideas | 10 headline options in various styles |
| Content Ideas | Ideas | 8 ideas with platform suggestions |

### Generation Options

Each generation request supports:

- **Tone:** Professional, Casual, Authoritative, Conversational, Inspirational
- **Audience:** Executives, Technical, Founders, Marketers, Developers
- **Length:** Short, Medium, Long, Auto
- **Custom Instructions:** Free-text additional context

---

## Storage

Scriptloom supports two storage backends:

### Local Filesystem (Development)
Files are stored in the `storage/` directory, organized by project:
```
storage/
├── projects/
│   └── {project_id}/
│       ├── media/         # Original uploaded files
│       ├── clips/         # Extracted video clips
│       ├── waveforms/     # Waveform JSON data
│       └── subtitles/     # Generated subtitle files
```

### Cloudflare R2 (Production)
S3-compatible object storage via Cloudflare R2. Configure via environment variables:
```
R2_ACCOUNT_ID=...
R2_ACCESS_KEY_ID=...
R2_SECRET_ACCESS_KEY=...
R2_BUCKET_NAME=...
R2_PUBLIC_URL=...
```

---

## Deployment

### Docker (Recommended)

```bash
docker compose up -d
```

This starts the backend, frontend, PostgreSQL, Redis, and Celery worker.

### Manual Deployment

1. **Database:** Run `alembic upgrade head` for migrations
2. **Backend:** `uvicorn backend.main:app --host 0.0.0.0 --port 8000`
3. **Celery Worker:** `celery -A backend.jobs.tasks worker --loglevel=info`
4. **Frontend:** `npm run build` and serve `dist/` with a static file server

### Production Checklist

- [ ] Set a strong `SECRET_KEY`
- [ ] Configure `ALLOWED_ORIGINS` for your domain
- [ ] Use PostgreSQL (not SQLite)
- [ ] Set up Redis for Celery and rate limiting
- [ ] Configure Cloudflare R2 for production storage
- [ ] Enable HTTPS via reverse proxy (nginx/Caddy)
- [ ] Set up process manager (systemd/supervisor)

---

## License

MIT License. See [LICENSE](LICENSE) for details.
