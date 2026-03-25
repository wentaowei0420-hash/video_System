import json
import os
from functools import lru_cache
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
CONFIG_DIR = PROJECT_ROOT / "config"
CONFIG_FILE = CONFIG_DIR / "app_config.json"
RUNTIME_DIR = PROJECT_ROOT / "runtime"


DEFAULT_CONFIG = {
    "backend": {
        "host": "127.0.0.1",
        "port": 8766,
    },
    "database": {
        "host": "127.0.0.1",
        "port": 3306,
        "user": "root",
        "password": "123456",
        "name": "video_system",
        "charset": "utf8mb4",
    },
    "tools": {
        "mediainfo_path": "",
    },
    "videofusion": {
        "source_dir": "VideoFusion-1.12.5_execode",
        "runtime_dir": "VideoFusion v1.12.5",
        "temp_dir": "runtime/videofusion/temp",
        "workspace_dir": "runtime/videofusion/workspace",
        "output_dir": "runtime/videofusion/output",
        "ffmpeg_file": "VideoFusion v1.12.5/bin/ffmpeg.exe",
    },
}


def _read_env(name, default):
    value = os.getenv(name)
    if value is None:
        return default
    if isinstance(value, str) and value.strip() == "":
        return default
    return value


def resolve_path(value):
    path = Path(value)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path.resolve()


def _merge_dict(base, updates):
    result = dict(base)
    for key, value in (updates or {}).items():
        if isinstance(result.get(key), dict) and isinstance(value, dict):
            result[key] = _merge_dict(result[key], value)
        else:
            result[key] = value
    return result


def _coerce_int(value, default):
    try:
        return int(value)
    except Exception:
        return int(default)


def _ensure_config_file():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if not CONFIG_FILE.exists():
        CONFIG_FILE.write_text(json.dumps(DEFAULT_CONFIG, ensure_ascii=False, indent=2), encoding="utf-8")


@lru_cache(maxsize=1)
def load_settings():
    _ensure_config_file()
    data = DEFAULT_CONFIG
    try:
        user_data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        if isinstance(user_data, dict):
            data = _merge_dict(DEFAULT_CONFIG, user_data)
    except Exception:
        data = DEFAULT_CONFIG

    backend = data["backend"]
    database = data["database"]
    tools = data["tools"]
    videofusion = data["videofusion"]

    return {
        "project_root": PROJECT_ROOT,
        "runtime_dir": RUNTIME_DIR,
        "config_file": CONFIG_FILE,
        "backend": {
            "host": _read_env("VIDEO_SYSTEM_BACKEND_HOST", backend.get("host", "127.0.0.1")),
            "port": _coerce_int(_read_env("VIDEO_SYSTEM_BACKEND_PORT", backend.get("port", 8766)), backend.get("port", 8766)),
        },
        "database": {
            "host": _read_env("VIDEO_SYSTEM_DB_HOST", database.get("host", "127.0.0.1")),
            "port": _coerce_int(_read_env("VIDEO_SYSTEM_DB_PORT", database.get("port", 3306)), database.get("port", 3306)),
            "user": _read_env("VIDEO_SYSTEM_DB_USER", database.get("user", "root")),
            "password": _read_env("VIDEO_SYSTEM_DB_PASSWORD", database.get("password", "123456")),
            "name": _read_env("VIDEO_SYSTEM_DB_NAME", database.get("name", "video_system")),
            "charset": _read_env("VIDEO_SYSTEM_DB_CHARSET", database.get("charset", "utf8mb4")),
        },
        "tools": {
            "mediainfo_path": _read_env("MEDIAINFO_PATH", tools.get("mediainfo_path", "")),
        },
        "videofusion": {
            "source_dir": resolve_path(videofusion.get("source_dir", "VideoFusion-1.12.5_execode")),
            "runtime_dir": resolve_path(videofusion.get("runtime_dir", "VideoFusion v1.12.5")),
            "temp_dir": resolve_path(videofusion.get("temp_dir", "runtime/videofusion/temp")),
            "workspace_dir": resolve_path(videofusion.get("workspace_dir", "runtime/videofusion/workspace")),
            "output_dir": resolve_path(videofusion.get("output_dir", "runtime/videofusion/output")),
            "ffmpeg_file": resolve_path(videofusion.get("ffmpeg_file", "VideoFusion v1.12.5/bin/ffmpeg.exe")),
        },
    }


def ensure_runtime_directories():
    settings = load_settings()
    Path(settings["runtime_dir"]).mkdir(parents=True, exist_ok=True)
    for key in ("temp_dir", "workspace_dir", "output_dir"):
        Path(settings["videofusion"][key]).mkdir(parents=True, exist_ok=True)


def backend_base_url(port=None):
    settings = load_settings()
    host = settings["backend"]["host"]
    active_port = int(port or settings["backend"]["port"])
    return f"http://{host}:{active_port}"
