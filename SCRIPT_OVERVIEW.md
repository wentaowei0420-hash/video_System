# Script Overview

## Root Launchers

- `start_backend.py`
  Starts the HTTP backend.
- `start_frontend.py`
  Starts the integrated desktop launcher.
- `video_system_gui.py`
  Convenience launcher that ensures the backend is ready before opening the frontend.
- `video_system_settings.py`
  Shared local configuration and runtime path management.

## Frontend

- `video_app/frontend/api.py`
  Worker wrapper for async HTTP requests.
- `video_app/frontend/app.py`
  PyQt application bootstrap.
- `video_app/frontend/styles.py`
  Global industrial UI stylesheet.
- `video_app/frontend/widgets.py`
  Reusable cards, path inputs, segmented selectors, chips, steppers, and form controls.
- `video_app/frontend/window.py`
  Main window, module pages, dialogs, progress UI, and state persistence.

## Backend

- `video_app/backend/catalog.py`
  Action catalog definition and environment metadata.
- `video_app/backend/server.py`
  HTTP server, routing, task submission, history, preferences, and path-history APIs.
- `video_app/backend/storage.py`
  MySQL persistence for preferences, logs, and path history.
- `video_app/backend/tasks.py`
  In-memory task tracking and progress state.

## Actions

- `video_app/actions/common.py`
  Shared action helpers.
- `video_app/actions/dispatcher.py`
  Action dispatch entry.
- `video_app/actions/file_management.py`
  File collection, move, rename, and organization actions.
- `video_app/actions/classification.py`
  Aspect ratio and duration classification actions.
- `video_app/actions/analysis.py`
  Statistics, keyword, and Excel-related actions.
- `video_app/actions/automation.py`
  Automation workflows and orchestration.
- `video_app/actions/videofusion_bridge.py`
  VideoFusion source bridge integration.

## Core

- `video_app/core/utils.py`
  Shared utility functions and environment checks.

## Cleaned Redundancy

- removed duplicate package tree: `video_System/`
- removed empty legacy folder: `视频/`
- removed generated `__pycache__/` folders
