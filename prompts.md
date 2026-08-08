# Task 1 — Restore the Generate Clips Workflow

## Objective

Restore the complete **Generate Clips** workflow so that a user can successfully generate clips from an uploaded media file.

This task is **only** about the clip-generation pipeline.

Do not redesign the UI.
Do not modify unrelated features.
Do not work on login, landing page, dashboard, transcripts, AI content, or styling.

## Instructions

Before changing any code:

1. Inspect the current implementation.
2. Do not trust previous reports or walkthroughs.
3. Verify the actual codebase and runtime behavior.
4. Identify the root cause(s) preventing clip generation.

Trace the entire workflow:

Project
→ Upload Media
→ Generate Clips button
→ Frontend request
→ FastAPI endpoint
→ ProcessingJob creation
→ Celery task dispatch
→ Worker execution
→ Progress updates
→ Clip persistence
→ Frontend polling
→ Clips display

Verify every step.

## Requirements

The workflow must function end-to-end.

When the user clicks **Generate Clips**:

1. The frontend sends the correct request.
2. The backend accepts the request.
3. A ProcessingJob is created.
4. Celery receives the task.
5. The worker begins processing.
6. The ProcessingJob updates correctly.
7. The frontend reflects the real backend state.
8. Generated clips are saved.
9. Clips appear in the UI.
10. Refreshing the browser preserves state.

Do **not** use:

- fake progress
- mock data
- simulated completion
- placeholder clips

All progress must originate from the backend.

## Verification

Run the application and verify the complete workflow using a real uploaded media file.

Confirm:

- Generate Clips button works.
- Backend endpoint executes.
- Celery receives the task.
- Processing status changes.
- Progress updates appear.
- Clips are generated.
- Clips can be viewed.
- Refresh preserves state.

## Deliverables

After completing the task, provide:

1. Root cause(s).
2. Files modified.
3. Why the bug occurred.
4. How it was fixed.
5. Evidence that the workflow works.
6. Remaining limitations.

## Stop Condition

After this task is complete, STOP.

Do not continue to any other issue.

Wait for the next instruction.
