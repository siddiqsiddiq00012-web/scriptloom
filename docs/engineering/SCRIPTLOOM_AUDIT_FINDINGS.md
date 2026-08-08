# Scriptloom Engineering Audit — Findings & Remediation

**Date:** 2026-08-05
**Scope:** Full-stack production-readiness audit of the Scriptloom codebase (backend, frontend, tests, migrations, configuration).
**Method:** Manual inspection of every backend module (API, services, models, repositories, storage, jobs, middleware), every frontend source file, all tests and migrations, plus automated sub-agent audits across five subsystems.

> This document records **what is wrong**. The companion `CHANGES.md` records **what was fixed**, issue by issue, in priority order.

---

## 1. Executive Summary

Scriptloom has a solid architectural skeleton — clean layering (API → service → repository), ownership checks on every resource endpoint, a provider-neutral storage abstraction, a Celery job queue, and a functional (if in-memory) event/rate-limit layer. **However, a large portion of the product is placeb-ware**:

- The **AI Generation Engine never calls an LLM** — it returns four hardcoded template assets.
- **Speaker diarization / chapter / key-assertion extraction is fabricated** (alternating speaker labels, 4 recycled hardcoded strings).
- **Failure fallbacks fabricate data**: ffprobe returns fake metadata for invalid files, FFmpeg failure writes a silent WAV, waveform failure synthesizes sine waves, upload validation is bypassable.
- The **event bus is fully wired but `publish()` is never called** — so SSE progress streams and event-driven webhooks are dead.
- **Billing quota checks are dead code** — no endpoint enforces or records usage.
- The **frontend is largely disconnected** — hardcoded analytics, fake publishing queue, fake settings, hardcoded `project_id=1` uploads, a fake Google-login button, and a broken `voiceDna.js` API wrapper.
- The **Alembic migration chain is broken** and cannot be applied to a fresh database.

---

## 2. Critical / High-Severity Findings

### 2.1 Backend — "AI" generation is hardcoded templates (no LLM call)

**Files:** `backend/services/generation_engine.py:63-201`, `backend/api/generation.py:25-58`

- `generate_campaign_pack()` builds four assets (LinkedIn carousel, X thread, newsletter, camera script) from **static string literals**.
- The only dynamic substitutions are banned-word replacement (`_clean_zero_slop`, line 25-33) and a single RAG quote injected on slide 3 (line 91).
- No call to any LLM (Gemini/OpenAI) exists in the generation path. The "AI OS" claims in docstrings/comments are not backed by inference.
- The `POST /generation/campaign-pack/{media_id}` endpoint presents this as AI-generated per-user content.

**Impact:** The flagship feature's output never varies with the actual transcript or Voice DNA. Test `test_generation_engine.py:73-79` is tautological (verifies a constant).

### 2.2 Backend — Diarization / topic segmentation is fabricated

**File:** `backend/processing/stt_engine.py:69-97`

- After real Whisper transcription, speakers are assigned by segment-index parity: `"Speaker 1 (Founder)"` / `"Speaker 2 (Host)"` (`idx % 2`).
- `chapters` and `key_assertions` are four hardcoded strings recycled by `idx % len(...)`.
- A hardcoded `summary` is persisted.
- These values are written to `transcript_segments` (`repositories/transcript_repository.py:45-73`) and served by the transcript API as genuine analysis.

**Impact:** Users are shown fabricated speaker/chapter/assertion structure as if it were real STT diarization.

### 2.3 Backend — Failure fallbacks fabricate data (data integrity + security)

| # | Location | Problem |
|---|----------|---------|
| M3 | `backend/processing/audio_processor.py:43-54` | On *any* ffmpeg failure, writes a **44-byte silent WAV header** (or copies a possibly-corrupt WAV). Pipeline then "succeeds"; transcription reports "No speech detected". |
| M4 | `backend/processing/waveform_processor.py:56-64` | On read error, `except Exception: pass` then replaces peaks with **synthesized sine waves** and persists them as the media waveform. |
| M5 | `backend/services/ffprobe_service.py:84-96` | `except Exception` returns fabricated `VideoMetadata` (`codec="fallback"`, `bitrate=128000`, guessed duration). This is the "authoritative" upload validation (`upload_service.py:85-90`), so **invalid files pass upload** and get fake duration/codec stored. |
| S1 | `backend/services/upload_service.py:49-90`, `backend/services/file_sanitizer.py` | `FileSanitizer.validate_magic_bytes` / `sanitize_filename` are **never called** (grep-verified). Upload validation is extension-allowlist + ffprobe (which never raises). A renamed executable passes upload. |

**Impact:** Real processing/conversion errors are invisible; invalid files are stored as if valid; the visualizer shows fabricated waveforms.

### 2.4 Backend — Event bus is fully wired but `publish()` is never called

**Files:** `backend/events/event_bus.py:46`, `backend/api/stream.py:21-92`, `backend/services/webhook_service.py:117-135`

- Repo-wide grep confirms **zero callers** of `EventBus.publish`.
- The SSE hub subscribes to the bus and the generator emits only `connected`/`heartbeat` frames — no progress events are ever delivered.
- `webhook_event_bus_subscriber` never fires, so **automatic webhook delivery never happens** during real processing. Only the manual "test webhook" endpoint triggers dispatch.
- `ProgressEvent` DB model is never instantiated.

**Impact:** "Streaming progress updates" and event-driven webhooks are non-functional features.

### 2.5 Backend — Billing quota enforcement is dead code

**Files:** `backend/services/billing_service.py:91-108`, `backend/api/billing.py:51-71`

- `check_quota()` / `record_usage()` are **never called** anywhere (grep-verified). `hours_processed` and `campaign_packs_generated` are never incremented; no upload/transcribe/generate/process endpoint enforces quota.
- `/billing/usage` always reports `hours_processed: 0.0` and full remaining quota.
- `POST /billing/upgrade` just flips `plan_name` to any value (`"enterprise"` included) with no payment/checkout/audit.

**Impact:** Quota-based monetization is non-functional; users can upgrade themselves for free.

### 2.6 Backend — Alembic migration chain is broken

**Files:** `alembic/versions/*.py` vs `backend/models/*.py`

- `a74b5a4fe2d4_initial_schema.py` creates `users` with only `id/name/email/hashed_password`; `ab25ca1d7f50_create_processing_jobs_table.py:50-65` then calls `op.alter_column('users','is_active'|'is_verified'|'created_at'|'updated_at', ...)` on columns **no migration creates** → `NoSuchColumnError` on a fresh DB. It also uses `postgresql.TIMESTAMP` (non-portable to SQLite).
- **12 model tables have no migration** (`transcripts`, `transcript_segments`, `voice_dna`, `creator_memories`, `generated_contents`, `user_subscriptions`, `usage_records`, `audit_logs`, `progress_events`, `webhook_endpoints`, `webhook_delivery_logs`, `dead_letter_queue`). `e6d4b0d91577_extend_webhook_delivery_logs_schema.py` targets a table no migration creates.
- `c1b778f09fc4_create_clips_table.py` creates `clips` with `start_time`/`end_time` as `Integer` and a `status` column, but the model has `Float` start/end, `reason: String(1000)` NOT NULL, `subtitle_path`, and **no** `status`.
- The app only works because `backend/main.py:74` runs `Base.metadata.create_all()` at startup (which adds missing tables but never missing columns).

**Impact:** `alembic upgrade head` fails on any clean install; schema cannot be reproduced by tooling; clip persistence would 500 against a migration-built DB.

### 2.7 Backend — Clip extraction timing is wrong

**File:** `backend/processing/clip_extraction/service.py:26-31`

```python
command = [ffmpeg, "-y", "-ss", str(start), "-to", str(end), "-i", input_video, ...]
```

- Both `-ss` and `-to` precede `-i`. `-ss` becomes an **input** seek (output timestamps reset to 0 at `start`) and `-to` becomes an **output** option interpreted **relative to the seek point**.
- `extract_clip(start=10.5, end=30.2)` produces source `[10.5, 40.7]` — a 30.2s clip instead of the intended 19.7s.
- `pipeline/service.py:56-58` records `start_time=10.5, end_time=30.2` in the DB, so persisted metadata mismatches the actual clip. Burned subtitles are offset by `start` seconds.

**Impact:** Wrong, over-long clips shipped to users with incorrect timestamps.

### 2.8 Backend — Webhook URLs allow SSRF

**Files:** `backend/api/webhooks.py:26-46,76-99`, `backend/services/webhook_service.py:94-98`, `backend/jobs/tasks/webhook_delivery.py:96-101`

- `WebhookEndpointCreate.url` / `Update.url` accept any string; the delivery task does `requests.post(log_entry.request_url, ...)`.
- No scheme restriction, no private-IP/loopback/link-local block, no allowlist.
- A user can register a webhook to `http://169.254.169.254/...` (cloud metadata), `http://localhost:<port>`, or internal services, and trigger POSTs immediately via `/endpoints/{id}/test` or via event dispatch.

**Impact:** SSRF from the server toward internal infrastructure.

### 2.9 Backend — Double router registration exposes bare-root API

**File:** `backend/main.py:78-79`

```python
app.include_router(api_router, prefix="/api/v1")
app.include_router(api_router)
```

- Empirically verified: 38 unique routes × 2 = **76 OpenAPI paths**; every endpoint served at both `/api/v1/...` and bare `/...`.
- `GET /` returns `root.py`'s message; `main.py`'s own `@app.get("/")` (line 82-86) is dead code (shadowed).
- Duplicate `operationId` warning; OpenAPI doubled (breaks codegen); any `/api/v1/*`-scoped WAF/security rule is bypassable via the bare paths.

### 2.10 Backend — Hardcoded OAuth password for Google-created accounts

**File:** `backend/services/auth_service.py:81`

```python
hashed_password=hash_password("oauth_google_protected_pass")
```

- Every Google-created user's real bcrypt hash verifies against this **constant known string**. The normal `login()` path checks it, so anyone knowing this constant can log into any Google-created account via `{"email": victim, "password": "oauth_google_protected_pass"}`.

**Impact:** Account-takeover backdoor for all OAuth-created users.

### 2.11 Frontend — `voiceDna.js` API wrapper sends wrong HTTP method

**File:** `frontend/src/api/voiceDna.js:7-9,11-16` vs `frontend/src/api/client.js:5`

- `apiRequest` signature is `(endpoint, options = {})`. `updateVoiceDNA(payload)` calls `apiRequest("/voice-dna/me", "PUT", payload)` — the third arg is dropped, `"PUT"` is spread into fetch options as a string, so `method` stays GET and no body is sent. `searchMemory` has the same bug (GET with no body).
- `getVoiceDNA` "works" only by accident (default GET).
- Result: **Voice DNA saves silently do a GET (never persist)**; memory search always fails, and `VoiceDNAManager` falls back to hardcoded mock results.

### 2.12 Frontend — Google login can never succeed

**Files:** `frontend/src/pages/Auth/Login.jsx:15-41,96-104`, `frontend/src/pages/Auth/Register.jsx`, `frontend/src/api/auth.js:34-46`

- The button `window.prompt`s for an email and calls `loginWithGoogle(email, name, avatarUrl)` which POSTs `{email, name, avatar_url}`.
- The backend `GoogleAuthRequest` (schemas/auth.py) requires an `id_token`/`token`/`credential` and verifies it with Google — so the request always returns **400 "Google ID Token is required."**
- There is no Google Identity Services (GIS) integration at all.

**Impact:** "Continue with Google" is a misleading, always-failing fake SSO button.

### 2.13 Frontend — Uploads hardcode `project_id = 1`

**Files:** `frontend/src/components/modals/UploadModal.jsx:70`, `frontend/src/components/ingestion/IngestionWorkspace.jsx:56`

- `uploadMediaFile(1, selectedFile)` always uploads to project id 1. Any user whose first project isn't id 1 (or who has no project) gets a 404 / ownership error.

### 2.14 Frontend — Hardcoded mock results after a real upload

**File:** `frontend/src/components/modals/UploadModal.jsx:101-134,365-404`

- The "results" stage after a real upload+transcribe renders a **hardcoded carousel**, **hardcoded teleprompter script**, and **hardcoded newsletter**. The real `transcriptData` fetched at line 77 is never rendered, and `POST /generation/campaign-pack` is never called.
- The URL-paste path (lines 81-86) is pure fake: `setTimeout(() => { setUploadProgress(100); setStage("results"); }, 1200)` — no backend call; the backend has no URL-ingestion endpoint.

### 2.15 Frontend — Analytics, Publishing Queue, and Settings are 100% hardcoded

| Component | Findings |
|-----------|----------|
| `AnalyticsWorkspace.jsx:21-79` | `142.5 hrs`, `99.4%`, `184 hrs`, `38 Packs`, `32 Scripts`, channel bars — no API call at all. |
| `PublishingQueue.jsx:6-28,30-33` | Hardcoded queue array; "Publish Now" only toggles local state; no publish backend exists. |
| `SettingsWorkspace.jsx:21-34` | Hardcoded `name="Sarah Jenkins"`, `email="founder@scriptloom.ai"`, fake webhook URL; "Save Settings" is a `setTimeout` toast. |

### 2.16 Frontend — Dashboard shows fabricated stats and mismatched data

**File:** `frontend/src/pages/App/Dashboard.jsx`

- `liveUsage` initialized to `{hours_processed:0, campaign_packs_generated:0}` and **never updated** → metric cards always show `0h`/`0`.
- `voiceDnaInfo` default `match: "99.4%"` (line 63), hardcoded in fetch handler (line 103), and in header badge (line 175).
- The "Spoken Conversations & Campaign Packs" table renders `getProjects()` output (only `id/owner_id/name`) padded with hardcoded fallbacks: `speaker || "Creator"`, `type || "Audio"`, `duration || "--"`, `assets || ["LinkedIn Carousel","Substack Essay"]`.
- "Download Assets" (line 146-148) only shows a toast — no export call (backend `GET /export/...` exists but is unused).
- "Inspect Campaign Pack" (Eye, line 468-474) sets `selectedPack` which nothing renders.

### 2.17 Frontend — MediaLibrary is not a real library

**File:** `frontend/src/components/media/MediaLibrary.jsx`

- Line 24: `getMediaDetails(1)` — hardcoded media id 1; the backend has no "list media" endpoint, so it can only ever display one hardcoded item.
- Lines 121-130: waveform peaks are `Math.sin(idx * 0.4) * 80 + 20` bars — not real waveform data (`getMediaWaveform` exists but is never called).
- Lines 42-45: on API failure the catch block still removes the item and toasts "Removed recording …", **hiding the failure**.

### 2.18 Frontend — ContentStudio and VoiceDNAManager are disconnected

- `ContentStudio.jsx:22-30,60-66` — editor content is hardcoded demo text; `handleSave` is a fake `setTimeout` toast. The real `PUT /generation/content/{content_id}` is never called.
- `VoiceDNAManager.jsx:16-19,64-78` — hardcoded DNA defaults and a **mock fallback array** of memory-search results that render when `searchMemory` fails (which it always does, see 2.11).

### 2.19 Frontend — No route guard and broken dev API base URL

- `routes/AppRouter.jsx:17` + `Dashboard.jsx:78-83` — `/dashboard` is protected only by a post-render `useEffect` navigate, so unauthenticated users see a flash of protected UI + failing API calls.
- `config.js` + `vite.config.js` — `apiUrl` defaults to `/api/v1` with **no Vite proxy** and no frontend `.env`; in `npm run dev` every API call hits the Vite server (5173) and fails unless `VITE_API_URL` is set.

---

## 3. Medium-Severity Findings

### 3.1 Backend

| # | Location | Problem |
|---|----------|---------|
| R1 | `backend/services/billing_service.py:91-108` | `check_quota` + `record_usage` is a non-atomic read-modify-write → TOCTOU; two concurrent transcribes can exceed the limit. |
| R2 | `billing_service.py:36-69`, `voice_dna_service.py:10-21` | `get_or_create_*` are query-then-insert races → duplicate rows / IntegrityError 500. |
| B3 | `generation_engine.py:46` | `owner_id = media.project.owner_id if media.project else 1` — cross-tenant Voice DNA/RAG exposure for orphaned media. |
| B4 | `processing_service.py:140-150` | Per-clip `db.commit()`; if clip *k* fails, clips 1..k-1 remain committed while storage compensation deleted the files → orphaned DB rows. |
| B5 | `processing_service.py:169-176` | FAILED status write inside exception handler is `except Exception: pass`; crash between COMPLETED and final commit strands a job in `processing`. |
| B6 | `storage/r2.py:90-99` | `exists()` returns `False` for any `ClientError` (403/500) → R2 misconfiguration surfaces as "media not found". |
| B2 | `services/export_engine.py:33,45` | Unguarded `json.loads(asset.body_json)` → malformed stored JSON raises `ValueError` → 500. |
| C2 | `waveform_processor.py:28-31` | Reads entire WAV into RAM (1 hr @16kHz ≈ 115 MB); upload waveform recompute does this in-request. |
| P1 | `upload_service.py:35-132` | Upload request synchronously runs ffprobe + full media pipeline on the event loop; large uploads stall FastAPI. Failure is swallowed and reported as HTTP 200 "success". |
| P2 | `transcription/service.py:11-15` | `WhisperModel("base")` loaded per `ProcessingPipeline()` per job (~100 MB+ per job). |
| P5 | `creator_memory_service.py:99-133` | `search_memory` loads every user memory row into Python; no SQL LIMIT. |
| 2.2 | `api/auth.py:38-44` | Register TOCTOU → uncaught `IntegrityError` → 500. |
| 2.3 | `core/dependencies.py:48` | `int(user_id)` ValueError → 500 (not 401); no `is_active` check. |
| 2.4 | `generation_engine.py:54-58`, `transcript_repository.py:50-54`, `creator_memory_service.py:56-60` | Delete-then-insert committed separately → data loss on mid-failure. |
| 2.6 | `api/webhooks.py:135-170` | Test endpoint fans out to all user endpoints; 500s when target subscribes to specific events or is inactive. |
| 2.7 | `main.py:56-60` | Webhook crash recovery resets status to PENDING but never re-enqueues a Celery task → deliveries stuck PENDING. |
| 2.8 | `api/processing.py:37-65` | Job commit and Celery dispatch are not transactional; crash between them strands a PENDING job. |
| 2.9 | `api/health.py:40,51-57` | Storage check is always-true, mutates filesystem, checks wrong dir (`MEDIA_FOLDER` vs `LOCAL_STORAGE_ROOT`); public `/ready` discloses `cache_stats`, `performance_metrics`, `active_worker_tasks`. |
| 2.10 | `upload_service.py:49,89,108` | Filenames only `Path(...).name.replace("..","")` (no CRLF/`"` stripping for Content-Disposition); `str(e)` from ffprobe/storage leaks internal paths. |
| 2.13 | `exceptions/handlers.py:7`, `main.py` | Global exception handlers written but never registered → inconsistent error envelope, unhandled exceptions. |
| 2.14 | `exports.py:38-42` vs `generation.py:54-58` | Same class of `ValueError` mapped to 404 vs 400; inconsistent codes. |
| 2.15 | `creator_memory_service.py:21-36` | "Vector store" is a 32-dim hash bag-of-words with cosine similarity — not semantic RAG; API overstates it. |
| 2.19 | `middleware/rate_limiter.py` | Per-process in-memory dict, no lock, never purged, trusts `request.client.host` (proxy → shared bucket); `/transcribe` POST throttled as "upload". |
| H3 | `middleware/rate_limiter.py` | Not shared across workers; `REDIS_URL` configured but unused. |
| H5 | `storage/local.py:17-31` | Legacy keys resolved against CWD; containment check accepts anywhere under workspace; lexical `is_relative_to` bypassable via symlink. |
| M13 | `upload_service.py:58` | Temp dir created in process CWD (relative), not system temp. |
| M10 | `webhook_delivery.py:36-40` | Idempotency check doesn't cover `PROCESSING` → concurrent delivery double-attempts. |
| M1 | `core/security.py:9-19`, `schemas/auth.py:8` | bcrypt silently truncates passwords >72 bytes; no max-length enforcement. |
| M2 | `core/config.py:12` | `SECRET_KEY` required but never strength-validated. |
| M3 | `core/dependencies.py:50-53` | Disabled users keep valid tokens (no `is_active` check). |
| M5 | `api/health.py` | `/ready` GET mutates filesystem as a side effect. |
| M9 | `main.py:23-29` + `config.py:21-37` | `allow_credentials=True` with no rejection of `*` in `ALLOWED_ORIGINS`. |
| M10 | `api/webhooks.py:39,91` | Webhook `secret` client-supplied with no min length; stored plaintext. |

### 3.2 Frontend

| # | Location | Problem |
|---|----------|---------|
| M | `ProjectsWorkspace.jsx:27-39,91-105` | Sends `description` (not in `ProjectCreate` schema); reads `category/updated_at/mediaCount/packsCount` (not in response); error handler opens the upload modal instead of surfacing errors; "Open Project" opens the upload modal. |
| M | `Dashboard.jsx` | `HomeDashboard` and `ResourceWorkspace` imported but never rendered (dead imports); `DemoModal` can never open (`isDemoOpen` never true); `selectedPack` set but never read. |
| M | `MediaLibrary.jsx:42-45` | Delete failure hidden (item removed + success toast). |
| M | `IngestionWorkspace.jsx:61` | `progressStream.connect(media.id)` with no subscriber; connection never cleaned up on unmount. |
| M | `Dashboard.jsx:73-76` | `showToast` setTimeout never cleared → setState after unmount risk. |
| M | `UploadModal.jsx:49` | `if (!isOpen) return null` after `useEffect` — SSE subscription kept for every mounted instance regardless of open state. |
| M | `Navbar.jsx:32-46` | `navigate('/#target')` relies on hash routing React Router 7 doesn't support → scroll may silently fail. |
| M | Many | Clickable `div`s without `role="button"`/`tabIndex`; labels without `htmlFor`; icon-only buttons use `title` not `aria-label`; no modal focus trap. |

### 3.3 Tests, Migrations, Configuration

| # | Location | Problem |
|---|----------|---------|
| F1.1 | `tests/test_streaming_and_webhooks.py:60-74` | Test depends on a live broker + worker + real network (no `celery_eager` fixture) → cannot pass in CI. |
| F1.2 | `tests/test_webhooks.py:291-349` + `webhook_delivery.py:178-199` | The task swallows Celery's `Retry` control exception → transient webhook failures are **never retried** (production bug), and the retry test cannot pass. |
| F1.3 | `tests/test_generation_engine.py:73-79` | Tautological — verifies a constant (the hardcoded templates). |
| F1.4 | `tests/test_billing_service.py:38-45,61-62` | Config tautology — copies literal values from `PLAN_LIMITS`. |
| F1.5 | `tests/conftest.py:5` | Rate limiter globally disabled; no rate-limit tests exist. |
| F1.6 | — | Coverage gaps: SSE success path, password reset, chunked uploads, migrations, creator-memory relevance, webhook secret rotation. |
| F1.7 | `tests/test_load_and_stress.py:28` | Timing-based asserts are flaky under CI. |
| F2.1-2.6 | `alembic/*` | Migration chain broken (see 2.6). |
| F3.1 | `.env.example` | 13 settings defined in `core/config.py` are absent from `.env.example`. |
| F3.2 | `tests/conftest.py:17` | Real-looking Google OAuth client ID hardcoded in tracked source. |
| F3.3 | `tests/conftest.py:8` | `test_scriptloom.db` not gitignored. |
| F5.1-5.6 | `docs/MASTER_ROADMAP.md` | Generation, billing, diarization, and memory are declared shipped but are placeholders. |

---

## 4. Low / Dead-Code Findings

- `backend/auth/hashing.py` + `backend/auth/jwt_handler.py` — full duplicates of `core/security.py` / `core/token.py`, never imported.
- `backend/core/token.py:39` `verify_access_token` — no callers.
- `backend/app_logging/logger.py` — `configure_logging` never called; no logging config applied.
- `backend/middleware/logging.py` — `log_requests` never registered.
- `backend/services/audit_logger.py` — never called.
- `backend/services/file_sanitizer.py` — never used in the upload flow.
- `backend/exceptions/handlers.py` — never registered.
- `backend/services/cache_service.py` — `CacheInvalidator` never invoked; cache only read in health.
- `backend/core/async_worker.py` — `async_worker_pool.submit_task` never called; health reads `active_tasks` (always 0).
- `backend/ai/services/clip_selector.py` — full OpenAI client + prompt loader, never imported.
- `backend/processing/whisper/__init__.py` — empty stub.
- `backend/processing/video_processor.py` — empty stub.
- `backend/schemas/clip.py`, `schemas/token.py`, `routes/auth.py` — unused/empty.
- `backend/db/migrations/` — stale duplicate alembic scaffold.
- Frontend: `components/layout/`, `components/dashboard/`, most of `components/landing/`, empty `pages/Dashboard/{Home,Content,Library,Settings,ProjectWorkspace}.jsx` (0 bytes), `structure.txt`/`iron.txt` (garbage `tree` dumps), unused deps (`@tanstack/react-query`, `axios`, `framer-motion`, `react-icons`), empty `context/`, `hooks/`, `styles/`, `utils/`.

---

## 5. Verified CLEAN

- **No IDOR/BOLA** — every resource-by-ID endpoint is gated by an ownership verifier (`verify_project/media/content/segment/clip/webhook_endpoint_ownership`), returning 404 (not 403), avoiding enumeration. Empirically checked `processing.py:100-105` ownership walk.
- **No SQL injection** — SQLAlchemy query API used throughout; no raw string interpolation in queries.
- **No missing dependencies** — every backend import resolves in `requirements.txt`.
- **No committed secrets** — only `.env.example` tracked; grep found no `sk-`, `AIza`, `AKIA`, PEM keys.
- **Storage keys** are validated centrally (`validate_storage_key`) against `..`, backslash, colon, absolute prefixes.

---

## 6. Prioritized Remediation Order

1. **Clip timing** (2.7) — wrong outputs shipped to users.
2. **Router double registration** (2.9) — security surface + dead root.
3. **Auth hardening** (2.10, 2.3) — account-takeover backdoor; 500-on-bad-token.
4. **Remove fabricated data** (2.1, 2.2, 2.3) — product truth + data integrity.
5. **Wire dead subsystems** (2.4 event bus, 2.5 billing) — make features real.
6. **SSRF + webhook retry** (2.8, F1.2) — security + reliability.
7. **Upload hardening** (2.3 S1, M13) — validation + temp dir.
8. **Frontend API integration** (2.11, 2.12, 2.13, 2.14, 2.15, 2.16, 2.17, 2.18) — replace mocks with real data.
9. **Migrations** (2.6) — reconcile alembic chain with models.
10. **Tests** — fix flaky tests (F1.1, F1.2), add regression tests for each fix.

---

*See `CHANGES.md` for the issue-by-issue fix log.*
