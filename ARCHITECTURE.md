# Architecture

## Overview

The active application code now runs from the English package:

- `video_app/`
- Root launchers: `start_backend.py`, `start_frontend.py`, `video_system_gui.py`
- Shared settings: `video_system_settings.py`

`video_system_gui.py` remains the convenience launcher. It checks the backend health first and, when `8766` is occupied by a stale instance, it automatically starts the current backend on the next available port.

## Structure

### Active Package

- `video_app/frontend`
  - `api.py`
  - `app.py`
  - `styles.py`
  - `widgets.py`
  - `window.py`
- `video_app/backend`
  - `catalog.py`
  - `server.py`
  - `storage.py`
- `video_app/actions`
  - `common.py`
  - `dispatcher.py`
  - `file_management.py`
  - `classification.py`
  - `analysis.py`
  - `automation.py`
  - `videofusion_bridge.py`
- `video_app/core`
  - `utils.py`

### Root Files

- `start_backend.py`
- `start_frontend.py`
- `video_system_gui.py`
- `video_system_settings.py`

### External Dependencies

- `VideoFusion v1.12.5/`
- `VideoFusion-1.12.5_execode/`
- Root compatibility shims:
  - `cv2.py`
  - `loguru.py`
  - `qfluentwidgets.py`
  - `typing_extensions.py`
  - `PySide6/`

These compatibility shims are still intentional because the current environment does not provide those packages natively, and the VideoFusion bridge still depends on them.

## Notes

- The old `video_System/` directory may still exist on disk as a locked legacy folder, but it is no longer the active runtime package.
- The removed Chinese package is no longer part of the launch path.
- Backend defaults come from `config/app_config.json`.

## Launch

```powershell
python D:\pycharm_pro\video_System\start_backend.py
python D:\pycharm_pro\video_System\start_frontend.py
```

Or start the whole system with the launcher:

```powershell
python D:\pycharm_pro\video_System\video_system_gui.py
```
