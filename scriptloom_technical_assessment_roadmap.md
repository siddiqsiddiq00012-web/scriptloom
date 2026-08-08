# Scriptloom — Technical Assessment & Next-Step Roadmap

**Method:** Direct inspection of the current repository (181 backend Python files, 34 frontend JS/JSX files) — API routers, services, models, migrations, Celery tasks, and every currently-existing frontend page/component. Cross-checked against `SCRIPTLOOM_PRODUCT_VISION.md`, `docs/MASTER_ROADMAP.md`, and the prior internal audit (`docs/engineering/SCRIPTLOOM_AUDIT_FINDINGS.md` + `CHANGES.md`).

**Note on sources:** `CLAUDE_FRONTEND_MASTER_PLAN.md` does not exist anywhere in this repository — it was not used as a source (it may exist outside this archive, or the name may refer to `docs/MASTER_ROADMAP.md` / `claude.md`, both of which were read). Everything below is verified against actual code, not against what any document *claims* the code does. Where the prior audit's findings and the live code disagree, the code wins, and the disagreement is called out explicitly — this happens more than once, in both directions (some "critical" findings are now fixed; the single most damning one — "AI generation is fake" — turns out to be **half-true**: the feature the frontend actually calls today is real).

---

## 1. Current Project Status

| Area | Maturity | Summary |
|---|---|---|
| **Backend architecture** | Solid | Clean API → service → repository layering, consistent ownership checks on every resource, provider-neutral storage abstraction (local/R2), Celery + Redis wired. |
| **Authentication** | Good | Real JWT + bcrypt, real Google Identity Services OAuth (frontend and backend both verified working), account-takeover backdoor and 500-on-bad-token bugs from the prior audit are fixed. Password reset is still a non-functional stub. |
| **Core workflow (upload → clip → transcript → content → export)** | Partially working | Upload, transcription, and AI clip selection are real and use real services (Whisper + Gemini). Per-content-type AI generation (what the UI actually calls) is **real Gemini output**, not templates. Live progress *reporting* (SSE) is dead; the app still works via a polling fallback. |
| **AI features** | Mixed | Clip selection: real Gemini call. Content generation (LinkedIn/X/newsletter/etc.): real Gemini call, on the endpoint the frontend uses. Voice DNA & Creator Memory: real backend services exist but are **not wired into either generation path and have zero frontend UI** — a stated core differentiator that a user can never see or use today. |
| **Storage / processing** | Good | FFmpeg calls use argument lists (no shell injection), clip-timing bug is fixed, waveform/audio fabrication fallbacks are removed (errors now raise instead of faking data), storage key path-traversal validation is solid. |
| **Security** | Mixed | OAuth backdoor, IDOR, and webhook SSRF are fixed. Billing has **zero payment verification** (any user can free-upgrade). Rate limiting is in-memory (broken under >1 worker). Password reset flow doesn't exist end-to-end. |
| **Reliability** | Weak | No retry/idempotency on the core video-processing Celery task. Alembic migrations cover 7 of 19 model tables — the app only boots because of a `Base.metadata.create_all()` safety net at startup, not because migrations are complete. |
| **Frontend** | Substantially rebuilt, much smaller than the product vision describes | The frontend that exists today (Dashboard, ProjectDetail, ResourceWorkspace, ProjectsWorkspace, MediaLibrary, SettingsWorkspace) is real, wired to real endpoints, and free of the mock/hardcoded-data problems the prior audit found in *files that no longer exist* (UploadModal, IngestionWorkspace, AnalyticsWorkspace, PublishingQueue, ContentStudio, VoiceDNAManager — none of these are in the repo anymore). But large parts of the original product vision (Voice DNA UI, Creator Memory UI, Analytics, Content Library, Rich Content Editor, Billing/upgrade UI) simply have no frontend at all right now, not even a broken one. |
| **Developer experience** | Fair | Dependencies pinned, no dependency-vulnerability scanning, three duplicate/dead auth-logic files still in the tree, unused npm packages still installed, two now-orphaned generation code paths (old template engine + new real engine) coexist and will confuse the next engineer who doesn't know which one is live. |

---

## 2. Feature Completion Matrix

| Feature | Current State | Status | Backend Complete? | Frontend Complete? | Works End-to-End? | Evidence |
|---|---|---|---|---|---|---|
| Register / Login (email+password) | Real JWT auth, bcrypt hashing, race-condition on duplicate email fixed | COMPLETE | Yes | Yes | Yes | `api/auth.py`, `services/auth_service.py`, `pages/Auth/{Login,Register}.jsx` |
| Google OAuth login | Real GIS button (`@react-oauth/google`), real backend `id_token` verification (issuer + email_verified checked) | COMPLETE | Yes | Yes | Yes | `components/auth/GoogleLoginButton.jsx`, `api/auth.py::google_auth` |
| Password reset | Endpoint exists, returns generic success message, **sends no email, has no consume-token endpoint** | NOT IMPLEMENTED | No | No | No | `api/auth.py::forgot_password`; no SMTP/email service anywhere in repo |
| Project CRUD | Real API + real UI (create/list/update/delete), ownership-checked | COMPLETE | Yes | Yes | Yes | `api/projects.py`, `components/projects/ProjectsWorkspace.jsx` |
| Media upload | Real chunked-to-disk upload, magic-byte + ffprobe validation, sanitized temp dir | COMPLETE | Yes | Yes | Yes | `services/upload_service.py`, `components/media/MediaLibrary.jsx` |
| Media library (list/search/delete) | Real list endpoint, real per-item waveform fetch, delete failures now surfaced (not hidden) | COMPLETE | Yes | Yes | Yes | `api/uploads.py`, `components/media/MediaLibrary.jsx` |
| Processing pipeline trigger | Real Celery dispatch; job/media ownership checked before start | COMPLETE | Yes | Yes | Yes | `api/processing.py`, `jobs/tasks/video_processing.py` |
| Live processing progress (SSE) | `EventBus.publish()` is **never called anywhere in the codebase** — the SSE hub only ever emits `connected`/`heartbeat` frames | BROKEN | No | Partial | Partial (masked by polling) | `events/event_bus.py`, `api/stream.py`; frontend already has a 3s-interval polling fallback in `ResourceWorkspace.jsx` that keeps the UI correct despite this |
| Transcription (Whisper) | Real `faster-whisper` transcription, runs synchronously inside the request/worker | COMPLETE | Yes | Yes | Yes | `processing/transcription/service.py` |
| Speaker diarization / chapters / key assertions | Previously fabricated (alternating labels, 4 recycled strings) — now removed; fields are honestly `None`/neutral, not fake | PARTIAL (honestly incomplete, not broken) | No (never implemented for real) | N/A | N/A | `processing/stt_engine.py:65-111` |
| AI clip selection | Real Gemini call (`GeminiService.analyze_transcript`) selects clip boundaries from the transcript | COMPLETE | Yes | Yes | Yes | `ai/services/gemini_service.py`, `processing/pipeline/service.py` |
| Clip extraction (FFmpeg) | Timing bug (`-ss`/`-to` both before `-i`) is fixed; clip duration now matches `end - start` | COMPLETE | Yes | Yes | Yes | `processing/clip_extraction/service.py` |
| View/play clips | Real streaming endpoint, real player wiring | COMPLETE | Yes | Yes | Yes | `api/clips.py`, `ResourceWorkspace.jsx` |
| AI content generation (LinkedIn/X/Instagram/newsletter/article/script/hooks/titles/ideas) | **Real Gemini call**, JSON-structured output, model-fallback chain — this is the endpoint the frontend actually calls | COMPLETE | Yes | Yes | Yes | `services/content_generator.py`, `api/generation.py::generate_content_for_media`, called from `ResourceWorkspace.jsx` |
| "Campaign Pack" generation (older 4-asset flow) | Still present in the codebase, **hardcoded string templates, zero LLM call** — but the frontend no longer calls this endpoint at all | ORPHANED / OBSOLETE | No (by design, never was) | No (nothing calls it) | N/A | `services/generation_engine.py`, `api/generation.py::generate_campaign_pack` |
| Voice DNA (writing-style profile) | Backend model + service exist; only reachable from the now-orphaned campaign-pack path; zero frontend UI | NOT IMPLEMENTED (for the user) | Partial | No | No | `models/voice_dna.py`, `services/voice_dna_service.py`; no `voiceDna.js`, no UI component |
| Creator Memory (RAG over past content) | Backend model + service exist ("vector store" is a 32-dim bag-of-words hash, not real embeddings); only reachable from the orphaned campaign-pack path; zero frontend UI | NOT IMPLEMENTED (for the user) | Partial | No | No | `services/creator_memory_service.py`; no frontend wiring |
| Edit generated content | Real `PUT /generation/content/{id}` endpoint; used in `ResourceWorkspace.jsx` | COMPLETE | Yes | Yes | Yes | `api/generation.py::update_generated_content` |
| Export (content asset / campaign pack, as file) | Real endpoints, real frontend blob-download wiring | COMPLETE | Yes | Yes | Yes | `api/exports.py`, `frontend/src/api/exports.js` |
| Content Library (filterable repository of all assets) | Described in the product vision; no dedicated page/component exists | NOT IMPLEMENTED | Partial (`GET /generation/media/{id}/content` exists, grouped) | No | No | No route, no component beyond a raw list inside `ResourceWorkspace.jsx` |
| Analytics | Described in the product vision (upload count, authority score, etc.); no page exists at all (the old fake `AnalyticsWorkspace.jsx` was deleted, not replaced) | NOT IMPLEMENTED | No | No | No | Not found anywhere in `frontend/src` |
| Billing — view usage/plan | Real `/billing/usage`, `/billing/subscription` endpoints, real Dashboard widget | COMPLETE (display only) | Yes | Yes | Yes, but always shows near-zero usage (see below) | `api/billing.py`, `pages/App/Dashboard.jsx` |
| Billing — usage enforcement | `check_quota()` / `record_usage()` exist but are **never called from anywhere** — no upload/transcribe/generate call increments or checks usage | BROKEN | No | N/A | No | `services/billing_service.py:91-108` (grep-verified zero callers) |
| Billing — upgrade plan | `POST /billing/upgrade` changes the plan on request with **no payment verification of any kind** | BROKEN (security/business bug) | No (present but unsafe) | No (no upgrade UI exists in the frontend anyway) | No (exploitable via direct API call) | `api/billing.py::upgrade_user_plan` |
| Webhooks (developer feature) | Full CRUD + test + delivery-history UI in Settings; real SSRF-hardened URL validation; HMAC signing correct | PARTIAL | Yes (schema/CRUD) | Yes | Partial — manual "Test" works; **automatic delivery on real events never fires** because it depends on the same dead `event_bus.publish()` | `components/settings/SettingsWorkspace.jsx` (`WebhooksPane`), `services/webhook_service.py` |
| Account settings (profile, password, export data, delete account) | Fully real, all four wired to real endpoints | COMPLETE | Yes | Yes | Yes | `components/settings/SettingsWorkspace.jsx`, `api/users.js`, `api/users.py` |
| Rich Content Editor (markdown, undo/redo, AI rewrite, tone adjuster) | Product-vision feature; current editing is a simple field-level `PUT`, no rewrite/tone-adjust/undo-redo UI | PARTIAL | Partial (no AI-rewrite endpoint) | Partial (basic edit only) | Partial | `ResourceWorkspace.jsx` generation tab |

---

## 3. Core Workflow Audit

**Landing → Register/Login → Dashboard → Create Project → Upload Media → Generate Clips → Processing Progress → View Clips → Generate Transcript → View Transcript → Generate AI Content → Edit → Export**

| Step | Status | Root cause / evidence |
|---|---|---|
| Landing Page | Works | `pages/Landing/LandingPage.jsx` renders; no backend dependency. |
| Register / Login | Works | Real bcrypt + JWT flow; duplicate-email race now returns 400 not 500 (Fix confirmed in `api/auth.py`). |
| Dashboard | Works, with one caveat | Loads real project list and real `/billing/usage`. The usage numbers are always ~0/full-quota because nothing ever calls `record_usage()` — not a UI bug, a backend gap (see 2.). |
| Create Project | Works | `ProjectsWorkspace.jsx` → `POST /projects`, ownership-scoped. |
| Upload Media | Works | Real multipart upload, magic-byte + ffprobe validation, no more hardcoded `project_id = 1` (confirmed fixed — `uploadMediaFile(Number(targetId), file)` uses the selected project). |
| Generate Clips (trigger processing) | Works | `startProcessing(mediaId)` → Celery task → real Whisper transcription → real Gemini clip selection → real FFmpeg extraction (timing bug fixed) → clips persisted. |
| Processing Progress | **Partially works** | Job status transitions (`pending → processing → completed/failed`) are correctly reflected via a 3-second poll (`getProcessingJob`), so the UI never hangs or lies about completion. But the *granular* progress payload (`progressInfo` — stage name, %) depends on SSE events that the backend never publishes, so that part of the UI will sit empty/static during a run. Low severity because the poll-based fallback covers the functional requirement; medium severity as a UX gap. |
| View Clips | Works | `getProjectClips` / `getClipStreamUrl`, real playback. |
| Generate Transcript | Works | `transcribeMedia(mediaId)` → real Whisper output. Diarization/chapter/key-assertion fields are honestly `None` rather than fabricated — so the *transcript* is trustworthy, but the *structure* (speakers, chapters) the product vision describes is simply not built yet. |
| View Transcript | Works | `getMediaTranscript`, rendered in `ResourceWorkspace.jsx`. |
| Generate AI Content | **Works — and is real AI**, contradicting the prior audit's headline finding | `generateContent(mediaId, {...})` → `POST /generation/media/{id}/generate` → `ContentGenerator.generate()` → real `google-genai` call with a 4-model fallback chain, JSON-mode output. This is a materially different (and better) code path than the old hardcoded `generation_engine.py`, which the frontend does not call anymore. |
| Edit | Works, but minimal | `PUT /generation/content/{id}` persists title/body edits. No AI-assisted rewrite/tone-adjust/shorten-expand (product-vision features) exist yet. |
| Export | Works | Real file/blob export for both single assets and campaign packs, correct `Content-Disposition` filename handling. |

**Overall:** the *literal* click-path from account creation to exported content works today, end-to-end, with real AI at both AI-touching steps (clip selection, content generation). The two genuine gaps in the happy path are (a) granular live-progress display during processing, which is cosmetic, and (b) the fact that quota/usage tracking is disconnected, which is a business-logic gap rather than a workflow blocker.

---

## 4. Frontend Audit

**Confirmed dead/obsolete/missing (things the prior audit describes that no longer exist in this repo, or never existed here):**
- `UploadModal.jsx`, `IngestionWorkspace.jsx`, `AnalyticsWorkspace.jsx`, `PublishingQueue.jsx`, `ContentStudio.jsx`, `VoiceDNAManager.jsx`, `frontend/src/api/voiceDna.js`, and the empty stub pages (`pages/Dashboard/{Home,Content,Library,Settings,ProjectWorkspace}.jsx`) referenced in the prior audit **are not in the current repository at all**. The frontend was rebuilt around a much smaller, tab-based `Dashboard.jsx` that renders `ProjectsWorkspace`, `MediaLibrary`, and `SettingsWorkspace` inline. This is a positive finding (no lingering fake UI) but also means several product-vision features simply have no frontend anymore, fake or otherwise (Analytics, Content Library, Voice DNA Inspector, Creator Memory UI, Publishing Queue).

**Still-present issues (verified in the current files):**
- `Dashboard.jsx::showToast` creates a `setTimeout` via `useCallback` and returns a cleanup function that is never used as an effect cleanup (the return value of a plain callback, not a `useEffect`, is discarded) — a toast's timer is never explicitly cleared, so rapid successive toasts/unmounts can still trigger `setState` after unmount. Low severity, same class of bug the prior audit flagged; not yet fixed.
- No dedicated `/settings` route — Settings is only reachable as a Dashboard tab, so it can't be deep-linked or bookmarked.
- `MediaLibrary.jsx` does an N+1 fetch pattern: one call per project for media, then one call *per media item* for its waveform. Fine at demo scale, will visibly slow down once a user has dozens of media items.
- Unused npm dependencies still installed: `@tanstack/react-query`, `axios`, `framer-motion`, `react-icons` — confirmed zero imports of any of them anywhere in `frontend/src`. Dead weight in the bundle and a maintenance trap (someone will eventually half-adopt one of them).
- `ResourceWorkspace.jsx` (1,102 lines) is a single large component covering media detail, processing, clips, transcript, and generation — no obvious bugs found, but it is a maintainability risk as more tabs/features are added.
- Access token stored in `localStorage`, 30-minute expiry, no refresh flow (unchanged from the security audit's finding — still valid).

**Verified as genuinely fixed (do not "re-fix" these):**
- Google login is a real GIS button, not a `window.prompt` hack.
- Hardcoded `project_id = 1` uploads are gone.
- Media library, dashboard stats, and settings all call real endpoints — no hardcoded demo data anywhere in the current source tree (verified by grep across every `.jsx`/`.js` file for `hardcod|mock|fake|dummy|Math.sin|Math.random|setTimeout(() =>` — zero hits in the core workflow files).
- Vite dev proxy is configured (`/api/v1` → `localhost:8000`); the "every dev API call fails" bug from the prior audit is fixed.

---

## 5. Backend Audit

**Already fixed (verified against the prior audit's own findings list):**

| # | Prior finding | Verified current state |
|---|---|---|
| 2.7 | Clip extraction timing wrong (`-ss`/`-to` both before `-i`) | Fixed — `-ss` before `-i`, `-t (end-start)` after. |
| 2.9 | Double router registration (76 duplicate paths) | Fixed — `main.py` has a single `include_router(api_router, prefix="/api/v1")`. (Note: `CHANGES.md` claims this was "investigated, not fixed" — the code disagrees with its own changelog; trust the code.) |
| 2.10 | Hardcoded OAuth backdoor password | Fixed — `secrets.token_urlsafe(32)` per user. |
| 2.3 (S1) | ffprobe fabricates metadata on failure | Fixed — raises `RuntimeError` instead. |
| M3/M4 | Audio/waveform silent-failure fabrication (fake WAV, sine-wave peaks) | Fixed — both now raise instead of fabricating. |
| 2.2 | Diarization/chapters/key-assertions fabricated | Fixed — honestly `None`/neutral now. |
| S1 | Upload validation bypassable (`FileSanitizer` never called) | Fixed — magic-byte + filename sanitization wired into `upload_service.py`; temp dir moved to system temp. |
| 2.8 | Webhook SSRF (no private-IP/loopback validation) | Fixed — `_validate_webhook_url()` blocks loopback/private/link-local, enforces scheme, enforces ≥16-char secrets. |
| M3 (auth) | `get_current_user` 500s on bad token `sub`, no `is_active` check | Fixed — proper 401s, disabled-user check present. |
| 2.14 | Export engine crashes on malformed `body_json` | Fixed — guarded `json.loads` with fallback. |
| — | Health endpoint always-true check, wrong dir, info disclosure | Fixed — checks the real storage provider, only returns `status`/`database`/`storage`. |
| — | Register endpoint 500s on concurrent duplicate email | Fixed — `IntegrityError` caught, returns 400. |

**Still valid (confirmed still present in the current code):**

| Severity | Issue | Evidence |
|---|---|---|
| Critical | `POST /billing/upgrade` has no payment verification — free self-upgrade to Enterprise | `api/billing.py::upgrade_user_plan` — no Stripe/checkout call anywhere in the repo |
| Critical | `check_quota()` / `record_usage()` are dead code | Zero call sites, grep-verified |
| Critical | `event_bus.publish()` is never called | Zero call sites, grep-verified — kills both SSE progress and automatic webhook delivery |
| Critical | In-memory, IP-keyed rate limiter | `middleware/rate_limiter.py` — breaks under >1 worker/process, breaks behind any reverse proxy |
| High | Three duplicate/drifting auth-logic implementations | `core/security.py` vs `auth/hashing.py` (dead); `core/token.py` vs `auth/jwt_handler.py` (dead) vs inline decode in `core/dependencies.py` |
| High | Password reset is a stub (no email sent, no consume endpoint) | `api/auth.py::forgot_password` |
| High | Celery `process_video` has no retry policy and no idempotency guard | `jobs/tasks/video_processing.py` |
| High | Alembic migration chain covers 7 of 19 model tables; app only boots via `Base.metadata.create_all()` at startup | `alembic/versions/` (7 files) vs `backend/models/` (19 model classes); `main.py::startup()` |
| Medium | `local.py` storage containment check is broader than necessary for "legacy" keys (though `..` is independently blocked, so not currently exploitable) | `storage/local.py::_resolve_key` |
| Medium | `print()` used instead of the logger in several modules | `main.py`, `gemini_service.py`, `project_service.py`, several `db/migrate_*.py` scripts |
| Low | `backend/routes/auth.py`, `ai/services/clip_selector.py`, `backend/processing/video_processor.py`, `backend/processing/whisper/__init__.py` are dead/unused files | grep-verified zero imports |

**Obsolete / no longer applicable (prior audit findings that the current code has superseded):**
- "AI Generation Engine never calls an LLM" — **only true of the orphaned `generation_engine.py` / campaign-pack endpoint.** The endpoint the frontend actually uses (`content_generator.py` / `/generation/media/{id}/generate`) makes real Gemini calls. This is the single biggest correction to make to institutional memory about this codebase — treating "AI generation is fake" as still-true would be a wrong and consequential assumption going forward.
- "Google login can never succeed" — fixed, real GIS integration now exists.
- "Uploads hardcode `project_id=1`" — fixed.
- "MediaLibrary is not a real library" / "Dashboard shows fabricated stats" / "Settings is 100% hardcoded" — all fixed; the components that had these bugs were rebuilt, not patched.

---

## 6. Runtime Risks (ranked by likelihood × impact of breaking real usage)

1. **Free plan-upgrade exploit** (Critical) — any signed-up user can call `POST /billing/upgrade` directly and get Enterprise limits for $0. This is live, trivial to discover (it's a documented API), and directly costs money the moment there's a paying customer to compare against.
2. **Rate limiter doesn't rate-limit in production topology** (Critical) — the moment this runs behind a load balancer or with more than one worker process, brute-force/abuse protection on `/auth/login` and the AI-generation endpoints (which cost real Gemini API spend per call) effectively disappears.
3. **Gemini API cost exposure with no usage enforcement** (High) — `record_usage()`/`check_quota()` being dead code means a single user (or a script hitting the AI-generation endpoint in a loop) can generate unlimited Gemini calls with no plan-based ceiling. Combined with #1, a malicious or just enthusiastic free user can run up real API billing.
4. **Users who forget their password are permanently locked out** (High) — `forgot-password` returns a success message but does nothing. This is a support/churn risk the moment there are real, non-technical users.
5. **A crashed/retried Celery worker can double-process a video** (Medium-High) — no idempotency guard on `process_video`; a broker redelivery after a worker crash mid-job could run the whole pipeline (including a Gemini clip-selection call and multiple FFmpeg extractions) twice for the same media.
6. **Migrations don't reproduce the schema from scratch** (Medium) — deploying to a fresh database via `alembic upgrade head` alone would leave 12 tables missing; the app currently survives only because `Base.metadata.create_all()` papers over this at every startup, which itself is a landmine if that startup hook is ever removed or the app is deployed with a migration-only bootstrap process (common in production CI/CD).
7. **Processing progress UI silently shows nothing during long jobs** (Low-Medium, UX not correctness) — a user watching a multi-minute video process will see the job move from pending→processing→completed via polling, but no live "transcribing / selecting clips / extracting" stage detail, which can read as the app being stuck even though it isn't.
8. **Configured webhooks never fire automatically** (Low-Medium, developer-facing feature only) — a user who sets up a webhook expecting to be notified when processing completes will only ever see it work when they press "Test." No workflow-blocking impact for the core product, but the feature does not do what its UI implies.

---

## 7. Prioritized Roadmap

### Priority 1 — Critical blockers preventing the product from being trusted with real users/money

| Task | Why it matters | Dependencies | Complexity | User impact |
|---|---|---|---|---|
| Gate `/billing/upgrade` behind real payment confirmation (Stripe Checkout + webhook, or remove the self-service endpoint entirely) | Direct, live revenue leak the moment there's a paying tier | None | Medium (needs a payment provider integration) | Prevents free abuse of paid tiers |
| Wire `check_quota()` / `record_usage()` into the upload/transcribe/generate call paths | Without this, billing plans are cosmetic and Gemini spend is uncapped per user | None | Small–Medium | Makes plan limits real; protects API cost |
| Move rate limiting to a Redis-backed store; fix IP-source trust (parse `X-Forwarded-For` from a trusted proxy only) | Current limiter is a no-op under any real deployment topology (multi-worker or behind a proxy) | Redis already provisioned | Small–Medium | Restores brute-force/abuse protection |
| Finish or remove the password-reset flow | Users are currently permanently locked out with no recovery path | Needs an email-sending service (none exists yet) | Medium | Prevents account lockout/churn |

### Priority 2 — Core workflow completion

| Task | Why it matters | Dependencies | Complexity | User impact |
|---|---|---|---|---|
| Wire `event_bus.publish()` into the processing pipeline | Unlocks both live SSE progress *and* automatic webhook delivery in one fix — same root cause, two dead features | None | Medium | Real-time progress feedback; webhooks become truthful |
| Add retry policy (`bind=True`, backoff) and an idempotency guard to `process_video` | Prevents duplicate processing/double Gemini spend on worker crash+redelivery | None | Small–Medium | Reliability under real infrastructure failures |
| Reconcile Alembic migrations with the actual model set (12 missing tables) | Schema currently only reproducible via `create_all()`, not via the migration tool meant to be the source of truth | None | Medium–Large (mechanical but must be careful with existing data) | No user-facing change, but removes a deploy-time landmine |
| Decide the fate of `generation_engine.py` / campaign-pack endpoint: delete it, or intentionally repurpose it (e.g. as a "quick 4-asset pack" alongside the per-type generator) | It's dead code today but looks live to anyone reading the codebase; leaving it invites someone to "fix" or extend the wrong thing | None | Small (delete) or Medium (repurpose with real Gemini + Voice DNA/Memory) | None if deleted; differentiator feature if repurposed |
| Decide the fate of Voice DNA / Creator Memory: either build the frontend and wire them into the real `ContentGenerator` path, or explicitly scope them out of the near-term plan | Currently backend-only orphaned features that don't affect the AI output a user actually sees — the product vision calls this the core differentiator, so leaving it unresolved is a strategic gap, not just a bug | Content generator would need to accept Voice DNA/Memory context | Medium–Large | Directly affects whether the product delivers on its "authentic voice" promise |

### Priority 3 — Frontend UX improvements

| Task | Why it matters | Dependencies | Complexity | User impact |
|---|---|---|---|---|
| Add a real `/settings` route (currently tab-only, not deep-linkable) | Basic navigability | None | Small | Minor |
| Fix `MediaLibrary` N+1 waveform fetch pattern (batch endpoint or fetch-on-demand) | Will visibly slow down as media libraries grow | Backend: optional batch waveform endpoint | Small–Medium | Performance at scale |
| Build a real Content Library view (filterable across all generated assets, not just per-media) | Named in the product vision, currently only viewable per-media inside the workspace | `GET /generation/media/{id}/content` already exists; needs a cross-media aggregate endpoint + page | Medium | Discoverability of past output |
| Fix the `showToast` timer cleanup in `Dashboard.jsx` | Minor `setState`-after-unmount risk | None | Trivial | Robustness, not user-visible |
| Add AI-assisted rewrite/tone-adjust to the content editor (product-vision "Rich Content Editor") | Currently just a plain field edit | Needs a new Gemini-backed endpoint | Medium | Core editing experience upgrade |

### Priority 4 — Reliability and production hardening

| Task | Why it matters | Dependencies | Complexity | User impact |
|---|---|---|---|---|
| Consolidate the three duplicate auth-logic files into one (`core/security.py` + `core/token.py`, delete the `auth/` duplicates) | Already drifted once (algorithm fallback logic differs between copies); a future edit to the wrong copy is a silent security regression | None | Small | None visible, prevents future bugs |
| Add access-token refresh flow (currently hard-expires at 30 min with a forced re-login) | UX + security balance | None | Medium | Fewer forced logouts mid-session |
| Move JWT out of `localStorage` to an httpOnly cookie + CSRF token | Reduces XSS blast radius | Backend + frontend coordinated change | Medium–Large | Security posture, not user-visible |
| Add dependency vulnerability scanning to CI (`pip-audit`, `npm audit`/Dependabot) | Large ML/media dependency surface (torch, onnxruntime, faster-whisper) with pinned versions but no automated CVE tracking | CI pipeline | Small | None visible, ongoing risk reduction |

### Priority 5 — Developer experience and code quality

| Task | Why it matters | Dependencies | Complexity | User impact |
|---|---|---|---|---|
| Remove unused npm packages (`@tanstack/react-query`, `axios`, `framer-motion`, `react-icons`) | Dead weight, invites accidental half-adoption | None | Trivial | None |
| Remove dead backend files (`routes/auth.py`, `ai/services/clip_selector.py`, `processing/video_processor.py`, `processing/whisper/__init__.py`) | Confusing to a new engineer scanning the tree | None | Trivial | None |
| Replace `print()` with the existing logger across `main.py`, services, and migration scripts | Log visibility/structure in production | None | Small | None visible |
| Update `CHANGES.md`/`SCRIPTLOOM_AUDIT_FINDINGS.md` to reflect actual current state (several entries are now stale, e.g. the "double router, not fixed" note that is actually fixed) | Institutional memory currently disagrees with the code in places; the next person to read it will inherit wrong assumptions unless corrected | This document | Trivial | None |

---

## 8. Recommended Execution Order

Ordered to minimize regressions — security/money-risk fixes first (isolated, low blast radius), then the shared-root-cause fix that unlocks two features at once, then reliability, then everything else:

1. **Gate `/billing/upgrade`** behind real payment verification (isolated endpoint change, no dependency on anything else).
2. **Wire `check_quota`/`record_usage`** into upload/transcribe/generate (isolated service-layer change; test against the plan limits already defined in `billing_service.py`).
3. **Swap the rate limiter to Redis-backed**, fix the proxy-IP trust issue (isolated middleware change; Redis is already provisioned).
4. **Delete or finish the password-reset flow** — recommend deleting the misleading stub now (small change) and scheduling the real email-based flow as its own follow-up task, since it needs a new external dependency (email provider) that shouldn't block the other fixes above.
5. **Wire `event_bus.publish()` into the processing pipeline** — one root-cause fix that repairs both SSE progress and automatic webhook delivery. Do this before touching the frontend's progress display, since the frontend already has the subscriber code written and waiting.
6. **Add retry/idempotency to `process_video`** — do this right after #5 since both touch the same task/pipeline code; batching them avoids re-testing the processing pipeline twice.
7. **Reconcile Alembic migrations with the model set** — do this once the pipeline changes above are stable, since new migrations should capture the final schema rather than being written mid-change.
8. **Resolve the Voice DNA / Creator Memory / orphaned-campaign-pack decision** (delete vs. rebuild) — this is a product decision as much as an engineering one; recommend making the call before starting Priority 3 frontend work, since it determines whether "Content Library" and editor work should include Voice DNA controls.
9. **Priority 3 frontend items** (Settings route, waveform batching, Content Library, editor rewrite/tone tools) — safe to parallelize once #8 is decided, since none of them touch shared backend state.
10. **Priority 4 hardening** (auth-file consolidation, token refresh flow, httpOnly cookie migration, dependency scanning) — lowest urgency, no user-facing deadline pressure, best done as an ongoing background workstream rather than blocking any feature work.
11. **Priority 5 cleanup** (unused deps, dead files, logging, doc corrections) — do continuously, in small batches, alongside whichever task above is in flight; none of it needs to be a dedicated sprint.
