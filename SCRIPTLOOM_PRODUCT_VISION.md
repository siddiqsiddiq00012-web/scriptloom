# SCRIPTLOOM — PRODUCT VISION, MISSION & ENGINEERING CONTEXT

## Read This Before Working on the Repository

This document defines what **Scriptloom** is intended to become.

Before changing architecture, designing interfaces, adding features, removing features, or interpreting ambiguous code, understand this product vision.

The repository contains code created across multiple stages of development. Some existing components may represent old ideas, experiments, incomplete implementations, abandoned directions, or temporary interfaces.

Therefore:

> Existing code does not automatically define the product.

The product vision in this document defines the intended direction.

After understanding this document, inspect the actual repository to determine how much of this vision currently exists and how the existing backend can support it.

---

# 1. What Is Scriptloom?

Scriptloom is an **AI-powered content repurposing and creator intelligence platform**.

Its purpose is to take a creator's existing long-form content and transform it into multiple useful, reusable content assets.

A creator should be able to upload something once and use Scriptloom to extract substantially more value from it.

Examples of source material include:

- podcasts;
- interviews;
- YouTube videos;
- educational videos;
- recorded discussions;
- presentations;
- tutorials;
- webinars;
- audio recordings;
- other long-form creator content.

From that source, Scriptloom should help produce useful outputs such as:

- short-form video clips;
- transcripts;
- subtitles;
- social content;
- campaign content;
- reusable written assets;
- structured creator knowledge.

The core idea is:

> **One source. Many useful outputs.**

---

# 2. The Problem Scriptloom Solves

Creating long-form content requires substantial effort.

A creator may spend hours:

- researching;
- scripting;
- recording;
- interviewing;
- editing;
- presenting;
- publishing.

But after publication, much of the information inside that content remains trapped inside one video or audio file.

Repurposing it manually requires another workflow:

1. watch the entire recording;
2. identify interesting moments;
3. find timestamps;
4. cut clips;
5. transcribe speech;
6. clean the transcript;
7. identify useful ideas;
8. write posts;
9. create promotional copy;
10. organize the resulting assets;
11. export them;
12. repeat the process for every piece of content.

This creates a large amount of repetitive work.

Scriptloom exists to compress that workflow.

---

# 3. The Fundamental Product Promise

The basic user promise should eventually feel approximately like:

> **Upload your content once. Scriptloom finds the valuable parts and turns them into content you can use everywhere.**

The user should not have to understand:

- Whisper;
- FFmpeg;
- Gemini;
- Celery;
- embeddings;
- vector databases;
- storage materialization;
- processing jobs.

Those are implementation details.

The user should see outcomes:

- Generate Clips
- Transcribe
- Generate Content
- Export

---

# 4. The Core Product Loop

The most important Scriptloom workflow is:

```text
Create Project
      ↓
Upload Source
      ↓
Choose what you want Scriptloom to create
      ↓
AI Processing
      ↓
Review Results
      ↓
Edit / Refine
      ↓
Download / Export
```

More concretely:

```text
PROJECT
│
├── SOURCE MEDIA
│   │
│   ├── Generate Clips
│   │       ↓
│   │   AI identifies useful moments
│   │       ↓
│   │   FFmpeg extracts clips
│   │       ↓
│   │   User reviews / plays / downloads
│   │
│   ├── Transcribe
│   │       ↓
│   │   Speech-to-text
│   │       ↓
│   │   Timestamped transcript
│   │
│   ├── Generate AI Content
│   │       ↓
│   │   Understand source
│   │       ↓
│   │   Generate reusable written assets
│   │       ↓
│   │   User edits / exports
│   │
│   └── Creator Intelligence
│           ↓
│       Learn useful patterns/context
│           ↓
│       Improve future generation
│
└── OUTPUTS
    ├── Clips
    ├── Transcript
    ├── AI Content
    └── Exports
```

Everything in the application should support this loop.

---

# 5. Projects Are the Organizational Foundation

Scriptloom should be **project-oriented**.

A Project represents a body of related content or work.

For example:

```text
Project:
"AI Founder Podcast"

Sources:
Episode 01.mp4
Episode 02.mp4
Episode 03.mp4
```

Another user might organize projects as:

```text
Project:
"Python Course"

Sources:
Lesson 01.mp4
Lesson 02.mp4
Lesson 03.mp4
```

Projects provide context and organization.

The product should not feel like an unstructured global file dump.

---

# 6. Source Media Is the Starting Point

Uploaded media is not the final product.

It is the **source material** from which Scriptloom's tools operate.

This distinction matters greatly for UI design.

A poor interface would say:

```text
Uploaded Files

video.mp4
audio.mp3
```

and stop there.

A proper Scriptloom interface should communicate:

```text
video.mp4

What would you like to create?

[Generate Clips]
[Transcribe]
[Generate AI Content]
```

Uploading must lead directly into useful actions.

Upload cannot be a dead end.

---

# 7. Generate Clips

Clip generation is one of Scriptloom's primary capabilities.

The user uploads a long-form video.

Scriptloom should analyze it and identify moments that can stand on their own as useful short-form content.

Conceptually:

```text
Long-form video
      ↓
Transcription / understanding
      ↓
AI analysis
      ↓
Interesting moments identified
      ↓
Timestamp ranges selected
      ↓
FFmpeg extraction
      ↓
Short clips
```

The output should not simply be arbitrary slices of video.

The intelligence layer should help identify moments with potential value.

Examples could include:

- strong statements;
- explanations;
- insights;
- stories;
- surprising observations;
- useful advice;
- compelling moments.

The exact ranking algorithm should follow the backend implementation and evolve over time.

---

# 8. Clip Generation Must Feel Like Real Work Is Happening

A major product requirement is transparency.

When the user clicks:

**Generate Clips**

they should not stare indefinitely at:

`Generating...`

The application should communicate actual backend state.

For example:

```text
Queued
Waiting for processing worker...
```

then:

```text
Preparing media...
```

then:

```text
Transcribing media...
```

then:

```text
Analyzing transcript...
```

then:

```text
Extracting clip 2 of 5...
```

then:

```text
Saving clips...
```

then:

```text
5 clips generated
```

These stages must come from actual backend execution.

Scriptloom must never fabricate progress simply to make the UI look active.

---

# 9. Transcription

Transcription is another fundamental tool.

A user should be able to turn uploaded audio/video into a timestamped transcript.

The transcript is useful by itself, but it also forms a foundation for other intelligence features.

Potential uses include:

- reading content;
- searching content;
- editing text;
- finding moments;
- subtitles;
- clip analysis;
- AI generation;
- creator memory.

The frontend should therefore treat transcripts as first-class assets rather than hidden processing artifacts.

---

# 10. AI Content Generation

Scriptloom should also transform the meaning of the source into written content.

The intention is broader than generating generic social-media filler.

The AI should work from the creator's actual source material.

Conceptually:

```text
Source Media
      ↓
Transcript / Content Understanding
      ↓
Important ideas
      ↓
Creator context
      ↓
Generated content assets
```

The user should be able to review and edit generated content before export.

Generated content must never silently fall back to fake hardcoded examples.

If generation fails, show failure.

If no content exists, show an empty state.

---

# 11. Creator Intelligence

One of Scriptloom's longer-term differentiators is **Creator Intelligence**.

The goal is for Scriptloom to become better at understanding the creator over time.

This can include useful knowledge about:

- writing patterns;
- recurring topics;
- terminology;
- tone;
- previous content;
- creator context;
- communication patterns;
- useful memories extracted from previous sources.

The purpose is not merely to generate a synthetic voice.

It is to improve future AI output.

Conceptually:

```text
Generic AI
     +
Creator Context
     +
Previous Content
     +
Current Source
     ↓
More relevant generation
```

This should evolve carefully based on actual backend capabilities.

---

# 12. Voice DNA — Correct Interpretation

Earlier development produced interfaces that made Scriptloom appear heavily centered around voice generation.

That direction is not the intended product identity.

If **Voice DNA** remains, interpret it as part of Creator Intelligence.

It can represent understanding of:

- style;
- tone;
- vocabulary;
- patterns;
- creator identity/context.

It should not make Scriptloom look primarily like:

- ElevenLabs;
- a TTS generator;
- a voice cloning application;
- a speech synthesis tool.

Voice-related intelligence is supporting infrastructure, not the entire product.

---

# 13. What Scriptloom Is NOT

This section is critical.

Scriptloom is NOT primarily:

### A Voice Generator

Voice generation must not dominate the interface.

### A Fake Analytics Dashboard

Do not create meaningless cards such as:

```text
12.4K Views
89% Engagement
347 Hours Saved
+42% Growth
```

unless those numbers come from real supported backend data.

### A Social Scheduler

Do not build a fake publishing calendar or scheduling queue without real infrastructure.

### A Generic File Manager

Uploading files is merely the beginning.

### An AI Demo Collection

The tools should operate within one coherent workflow.

### A Prototype

The application should increasingly behave like production software.

---

# 14. Product Philosophy

Scriptloom should follow several product principles.

## Principle 1 — Source First

Generated outputs should originate from real user content.

## Principle 2 — User Control

AI creates drafts and suggestions.

The user reviews the results.

## Principle 3 — Transparency

Long-running operations should expose real state.

## Principle 4 — Persistence

Refreshing the browser should not destroy important state.

## Principle 5 — No Illusions

If something is unavailable, say so.

Never fabricate functionality.

## Principle 6 — Simplicity

Advanced backend architecture should result in a simpler frontend experience, not a more complicated one.

---

# 15. Desired User Experience

A new user should be able to open Scriptloom and understand the application quickly.

The ideal first experience:

```text
Welcome to Scriptloom

Turn your long-form content into clips,
transcripts, and reusable content.

[Create Your First Project]
```

After creating a project:

```text
Project: My Podcast

Add source content to begin.

[Upload Video or Audio]
```

After upload:

```text
podcast-episode.mp4

Ready

Turn this source into:

[Generate Clips]
[Transcribe]
[Generate AI Content]
```

There should be almost no ambiguity about what to do next.

---

# 16. Desired Product Hierarchy

A reasonable top-level structure is:

```text
Dashboard
Projects
Creator Intelligence
Settings
```

The actual implementation should be determined from the repository.

The most important content creation workflow should live inside Projects.

---

# 17. Dashboard Vision

The Dashboard is not the product itself.

It is the user's starting point.

Its primary purposes are:

- resume recent work;
- see real projects;
- create a project;
- understand the product.

It should be calm and useful.

Avoid clutter.

---

# 18. Project Workspace Vision

Projects are where meaningful work happens.

A Project Workspace should show:

```text
Project Name

Sources
────────────────────────────

episode-01.mp4
Ready

[Generate Clips]
[Transcribe]
[Generate AI Content]

episode-02.mp4
Processing clips — 3/5

[View Progress]
```

The exact design can differ.

The principle cannot:

> Every source must naturally expose the tools that operate on it.

---

# 19. Resource Workspace Vision

Opening a source should provide a focused working environment.

Conceptually:

```text
Podcast Episode 12

[Generate Clips] [Transcribe] [Generate AI Content] [Export]

Overview | Transcript | Clips | AI Content
```

This is the main production workspace.

---

# 20. Overview

Overview should answer:

- What is this source?
- What has already been generated?
- What is currently processing?
- What can I do next?

Do not fill it with decorative statistics.

---

# 21. Transcript

The Transcript workspace should provide a readable representation of the source.

Where supported:

- timestamps;
- segments;
- speaker information;
- editing.

---

# 22. Clips

The Clips workspace should be designed for reviewing generated moments.

Users should be able to:

- play;
- inspect;
- understand timestamps;
- see useful AI reasoning where available;
- download.

Future improvements may add more editing capabilities.

Do not invent them before the backend supports them.

---

# 23. AI Content

The AI Content workspace should be a content review/editor environment.

The user should see generated assets based on their actual source.

They should be able to edit and persist changes where supported.

Export should be easy.

---

# 24. Exports

Scriptloom should make it easy to take generated work outside the application.

Outputs should not become trapped inside Scriptloom.

Where supported:

- download clips;
- export individual content;
- export campaign/content packs.

---

# 25. Backend Philosophy

The backend should remain responsible for:

- authentication;
- authorization;
- persistence;
- storage;
- processing;
- AI calls;
- job state;
- generation;
- exports;
- secure media access.

The frontend should not recreate backend business logic.

---

# 26. Existing Storage Direction

Scriptloom has moved toward provider-neutral storage.

The architecture may support:

```text
Local Storage
       or
Cloudflare R2
```

Frontend code should never assume local filesystem paths.

It should interact with authenticated backend APIs.

---

# 27. Existing Processing Direction

Heavy processing should run outside the FastAPI request process where appropriate.

The architecture uses or is moving toward:

```text
FastAPI
   ↓
ProcessingJob
   ↓
Celery
   ↓
Redis
   ↓
Worker
   ↓
AI / FFmpeg / Storage
```

The frontend should expose this architecture as a simple job experience:

```text
Queued
→ Processing
→ Completed
```

---

# 28. Reliability Matters

Scriptloom may process expensive media.

Therefore:

- jobs should survive page refresh;
- job state should be persisted;
- errors should terminate correctly;
- duplicate jobs should be prevented;
- temporary files should be cleaned up;
- remote storage should be handled correctly.

The frontend must respect these guarantees.

---

# 29. Security Matters

Projects and media belong to users.

Never weaken authorization to make frontend development easier.

A user must not be able to access another user's:

- projects;
- media;
- jobs;
- transcripts;
- clips;
- generated content;
- exports;
- webhook resources.

Use the existing backend ownership architecture.

---

# 30. External Services Are Infrastructure, Not Product Identity

Scriptloom may depend on technologies such as:

- Google OAuth;
- Gemini;
- Faster-Whisper;
- FFmpeg;
- Redis;
- Celery;
- Cloudflare R2.

These are implementation tools.

Do not design the UI around technology names.

Users should see:

```text
Generate Clips
```

not:

```text
Run Gemini + Whisper + FFmpeg Pipeline
```

---

# 31. Professional Design Direction

Scriptloom should visually communicate:

- intelligence;
- productivity;
- control;
- clarity;
- reliability.

It should feel closer to a professional workspace than an AI gimmick.

Prefer:

- restrained layout;
- strong typography;
- useful whitespace;
- consistent components;
- clear hierarchy;
- focused action areas;
- professional loading states;
- meaningful status indicators.

Avoid:

- excessive gradients;
- giant decorative hero elements inside the app;
- unnecessary animations;
- dozens of colorful metric cards;
- fake charts;
- random AI sparkle icons everywhere;
- excessive glassmorphism;
- interfaces designed primarily to look impressive in screenshots.

---

# 32. Professional Engineering Direction

The implementation should be understandable by another engineer.

Prefer:

```text
clear API modules
small reusable hooks
focused components
typed/validated contracts where practical
centralized authentication
centralized errors
reusable UI primitives
predictable state flow
```

Avoid:

```text
giant components
duplicate API calls
hardcoded endpoints
scattered tokens
silent catch blocks
fake fallback data
business logic inside presentation components
```

---

# 33. Long-Term Vision

The long-term goal is larger than basic repurposing.

Scriptloom should evolve toward an intelligent content operating system for creators.

Over time, it could understand:

```text
What has this creator talked about?
What ideas recur?
What style do they use?
What content has already been created?
What moments are worth repurposing?
What should be generated from new material?
```

This creates a progression:

```text
Phase 1
Content Repurposing

        ↓

Phase 2
Creator Intelligence

        ↓

Phase 3
Persistent Content Knowledge

        ↓

Phase 4
AI-Assisted Content Operating System
```

Do not prematurely build speculative Phase 4 functionality.

But architecture should avoid unnecessarily blocking that future.

---

# 34. Near-Term Product Goal

The immediate goal is much simpler.

Scriptloom must become excellent at:

```text
Create Project
      ↓
Upload Media
      ↓
Generate Clips / Transcript / Content
      ↓
See Real Progress
      ↓
Review Real Outputs
      ↓
Edit
      ↓
Download / Export
```

Until this experience is excellent, additional product expansion is secondary.

---

# 35. Current Development Reality

The repository has gone through several iterations.

Backend engineering has progressed substantially.

However, frontend development has repeatedly suffered from problems such as:

- UI created before backend contract verification;
- mock data;
- fake loading states;
- obsolete voice-generation design;
- buttons without real actions;
- incorrect endpoint assumptions;
- interfaces reported as integrated before real browser verification;
- frontend/backend schema mismatches;
- protected media loaded without authentication;
- processing state lost on refresh.

These mistakes must not be repeated.

---

# 36. Evidence Over Assumption

When deciding whether something works:

Do not rely on:

- previous walkthrough reports;
- comments;
- task checklists;
- old documentation;
- component names.

Verify against:

1. actual repository code;
2. actual database behavior;
3. actual backend requests;
4. actual worker execution;
5. actual browser behavior.

---

# 37. Product Priority Order

When making engineering decisions, prioritize:

```text
1. Core workflow correctness
2. Backend integration accuracy
3. Security
4. Reliability
5. Data persistence
6. Usability
7. Maintainability
8. Visual quality
9. Additional features
```

Visual polish is important.

But visual polish cannot substitute for functionality.

---

# 38. What Success Looks Like

Imagine a creator opening Scriptloom for the first time.

Within a few minutes they should be able to:

1. understand what Scriptloom does;
2. create an account;
3. create a project;
4. upload a video;
5. see obvious AI tools;
6. click Generate Clips;
7. understand what the system is currently doing;
8. receive actual clips;
9. play them;
10. generate a transcript;
11. generate written content;
12. edit the results;
13. export useful assets.

They should never encounter a fake dashboard pretending work has happened.

They should never wonder where the actual AI tools are.

They should never click a primary button that does nothing.

They should never see fake progress.

---

# 39. Core Product Standard

Every major Scriptloom feature should satisfy this chain:

```text
DISCOVERABLE
      ↓
ACTIONABLE
      ↓
CONNECTED
      ↓
STATE-AWARE
      ↓
PERSISTENT
      ↓
ERROR-SAFE
      ↓
PROFESSIONALLY PRESENTED
```

A feature is incomplete if any major part of that chain is missing.

Examples:

Beautiful Generate Clips button but no backend connection:

**Incomplete.**

Backend processing works but frontend only says "Generating..." indefinitely:

**Incomplete.**

Clips exist but cannot be securely played:

**Incomplete.**

Transcript loads but errors disappear silently:

**Incomplete.**

Everything works but the interface still looks like a voice-generation application:

**Incomplete.**

---

# 40. Final Vision

Scriptloom should eventually make this statement true:

> A creator can give Scriptloom one piece of long-form content, and Scriptloom can understand it, identify its most valuable moments and ideas, transform those into useful assets, preserve useful creator context, and provide a professional workspace for reviewing and exporting the results.

That is the direction of the product.

For the current development stage, focus relentlessly on making the foundational loop real:

> **Upload → Process → Understand → Repurpose → Review → Export**

Everything else is secondary.

---

# INSTRUCTION TO THE ENGINEER / AGENT

After reading this document:

1. Do not immediately change code.
2. Read the accompanying engineering execution specification.
3. Inspect the actual repository.
4. Compare current implementation against this product vision.
5. Preserve backend capabilities that support the vision.
6. remove obsolete frontend concepts that contradict it;
7. identify genuine missing capabilities;
8. implement the core product loop professionally;
9. verify behavior against the real backend;
10. do not claim completion without real end-to-end evidence.

When this document and existing code conflict regarding product direction, use this document to understand the intended product while still respecting actual technical constraints and existing stable backend architecture.

The objective is not to maximize the number of features.

The objective is to make **Scriptloom coherent, useful, reliable, and professional**.