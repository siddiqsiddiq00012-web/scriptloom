# Scriptloom Master Product Specification & Architecture Roadmap

**Version**: 1.0.0 (Creator-First MVP & V2/V3 Vision)  
**Status**: Active Master Blueprint  

---

## Overview & Core Philosophy

Scriptloom is an **AI-powered content operating system** that helps knowledge creators transform long-form content (webinars, podcasts, keynotes, Zoom calls) into high-quality, multi-platform campaign packs while preserving their authentic voice.

---

## Frontend Feature Architecture (User-Facing)

1. **Authentication**: Sign up, Login, Google OAuth (future), Password Reset, Email Verification, Profile Setup.
2. **Dashboard**: Executive Home page showing Recent Projects, Latest Uploads, Live Processing Status, Generated Content, Creator Statistics, and Quick Ingestion.
3. **Upload Workspace**: Drag-and-drop support for MP4, MOV, MP3, WAV, YouTube URLs, Podcast RSS feeds. Upload progress & file pre-parser.
4. **Processing Screen**: Real-time progress tracker (*Uploading*, *Transcribing*, *Speaker Diarization*, *Content Understanding*, *Voice Matching*, *Output Generation*).
5. **Project Workspace**: Split-screen canvas with media player, interactive transcript timeline, speaker labels, and generated multi-platform campaign assets.
6. **Rich Content Editor**: Multi-format editor with markdown, undo/redo, AI rewrite, tone adjuster, shorten/expand, and transcript highlight back-links.
7. **Voice DNA Inspector**: Creator persona engine managing writing style, cadence, vocabulary preferences, CTAs, hook styles, banned jargon, emoji rules, and sentence length.
8. **Creator Memory RAG**: Semantic vector index over all historical uploads, key quotes, stories, analogies, frameworks, and customer discovery insights.
9. **Content Library**: Filterable repository of all generated assets (*Videos*, *Carousels*, *Threads*, *Newsletters*, *Drafts*, *Published*).
10. **Export Center**: Export formats (*Markdown*, *PDF*, *DOCX*, *TXT*, *Teleprompter Script*, *Copy to Clipboard*).
11. **Analytics**: Upload count, assets created, translation time saved, content authority score.
12. **Billing**: Subscription tiers (*Starter $0*, *Founder Pro $49/mo*, *Enterprise*), usage tracking, invoices.
13. **Settings**: Profile, Password, Security, Notifications, Language, Theme, Voice DNA parameters, Danger Zone.

---

## Backend Microservices & API Architecture

1. **Authentication Service**: JWT Auth, OAuth, Session Management, Password Hashing (`passlib`/`bcrypt`), Password Reset, Email Verification.
2. **User Management Service**: User Profile, Subscription Status, Preferences, Voice Settings store.
3. **Upload Service**: Chunked large file uploads, file validation, storage handlers (`storage/uploads/`).
4. **Media Processing Pipeline**: Audio extraction via FFmpeg, video metadata, waveform generation, compression.
5. **Speech-to-Text Engine**: High-fidelity diarized transcript generation, speaker labeling, timestamping.
6. **Transcript Engine**: Structural breakdown into chapters, topics, key assertions, and highlights.
7. **Voice DNA Engine**: Vocabulary learning, sentence rhythm calculation, tone calibration, hook & CTA style matching.
8. **Creator Memory Engine**: Vector embeddings, RAG indexing over historical uploads, semantic search.
9. **AI Generation Engine**: Campaign pack generator (*LinkedIn Posts*, *X Threads*, *Carousels*, *Newsletters*, *Camera Scripts*, *Hooks & Titles*).
10. **Prompt Orchestrator**: Context injection, system prompt templating, memory retrieval, zero-AI-slop filter.
11. **Content Management Service**: Draft storage, revision history, asset state machine.
12. **Export Engine**: PDF carousel generator, DOCX/Markdown/TXT converter.
13. **Notification Service**: Email notifications, processing complete alerts, weekly digest.
14. **Subscription & Billing System**: Usage tracking, tier enforcement, plan limits.
15. **API Layer**: RESTful OpenAPI specs (`/api/v1/auth`, `/api/v1/users`, `/api/v1/uploads`, `/api/v1/projects`, `/api/v1/content`, `/api/v1/voice-dna`, `/api/v1/creator-memory`, `/api/v1/billing`).
16. **Admin Dashboard Service**: System metrics, user management, storage audit, error logs.

---

## MVP Execution Order

1. **Section 1 (Current)**: Backend Authentication & User Management Service.
2. **Section 2**: Upload & Media Processing Pipeline Service.
3. **Section 3**: Speech-to-Text & Transcript Engine.
4. **Section 4**: Voice DNA Engine & Creator Memory RAG Store.
5. **Section 5**: AI Generation Engine & Prompt Orchestrator.
6. **Section 6**: Content Management & Export Engine.
7. **Section 7**: Billing & Usage System.
