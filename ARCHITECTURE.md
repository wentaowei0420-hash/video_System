# Architecture

## Active Runtime

The system now runs from a single active package:

- `video_app/`
- root launchers: `start_backend.py`, `start_frontend.py`, `video_system_gui.py`
- shared settings: `video_system_settings.py`

`video_system_gui.py` is still the integrated launcher. It checks backend health, starts the backend when needed, and avoids stale occupied ports by moving to the next available port.

## Package Layout

### Frontend

- `video_app/frontend/api.py`
- `video_app/frontend/app.py`
- `video_app/frontend/styles.py`
- `video_app/frontend/widgets.py`
- `video_app/frontend/window.py`

### Backend

- `video_app/backend/catalog.py`
- `video_app/backend/server.py`
- `video_app/backend/storage.py`
- `video_app/backend/tasks.py`

### Actions

- `video_app/actions/common.py`
- `video_app/actions/dispatcher.py`
- `video_app/actions/file_management.py`
- `video_app/actions/classification.py`
- `video_app/actions/analysis.py`
- `video_app/actions/automation.py`
- `video_app/actions/videofusion_bridge.py`

### Core

- `video_app/core/utils.py`

## Root Files

- `start_backend.py`
- `start_frontend.py`
- `video_system_gui.py`
- `video_system_settings.py`
- `README.md`
- `ARCHITECTURE.md`
- `SCRIPT_OVERVIEW.md`

## External and Compatibility Layers

- `VideoFusion v1.12.5/`
- `VideoFusion-1.12.5_execode/`
- compatibility shims kept at root for the bridge:
  - `cv2.py`
  - `loguru.py`
  - `qfluentwidgets.py`
  - `typing_extensions.py`
  - `PySide6/`

These shims are still intentional because the current VideoFusion bridge depends on them in this environment.

## Configuration and State

- app settings file: `config/app_config.json`
- runtime output: `runtime/`
- MySQL stores:
  - action preferences
  - run logs
  - path history
- local config stores:
  - backend base URL
  - last opened page
  - last history filter

## Cleanup Status

- removed redundant duplicate package: `video_System/`
- removed empty legacy folder: `视频/`
- cleared generated `__pycache__/` directories

## Launch

```powershell
python D:\pycharm_pro\video_System\start_backend.py
python D:\pycharm_pro\video_System\start_frontend.py
```

Integrated launcher:

```powershell
python D:\pycharm_pro\video_System\video_system_gui.py
```
