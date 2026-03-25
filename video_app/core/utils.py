import contextlib
import io
import json
import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

from video_app.backend.storage import get_storage
from video_system_settings import load_settings


PROJECT_ROOT = Path(__file__).resolve().parents[2]
VIDEO_EXTENSIONS = {
    ".mp4",
    ".avi",
    ".mkv",
    ".mov",
    ".wmv",
    ".flv",
    ".m4v",
    ".mpg",
    ".mpeg",
    ".rmvb",
    ".webm",
}


class ParameterValidationError(Exception):
    """Raised when request params are invalid."""


def split_keywords(raw_text):
    return [item.strip() for item in re.split(r"[\n,，；;]+", raw_text or "") if item.strip()]


def ensure_directory(path_text, field_name):
    if not path_text:
        raise ParameterValidationError(f"{field_name} cannot be empty")
    path = Path(path_text)
    if not path.exists():
        raise ParameterValidationError(f"{field_name} does not exist: {path}")
    if not path.is_dir():
        raise ParameterValidationError(f"{field_name} is not a directory: {path}")
    return path


def ensure_file(path_text, field_name, required=True):
    if not path_text:
        if required:
            raise ParameterValidationError(f"{field_name} cannot be empty")
        return None
    path = Path(path_text)
    if not path.exists():
        raise ParameterValidationError(f"{field_name} does not exist: {path}")
    if not path.is_file():
        raise ParameterValidationError(f"{field_name} is not a file: {path}")
    return path


def ensure_output_path(path_text, field_name, required=False):
    if not path_text:
        if required:
            raise ParameterValidationError(f"{field_name} cannot be empty")
        return None
    path = Path(path_text)
    if path.parent and not path.parent.exists():
        raise ParameterValidationError(f"{field_name} parent directory does not exist: {path.parent}")
    return path


def capture_logs(func):
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer), contextlib.redirect_stderr(buffer):
        result = func()
    return result, buffer.getvalue()


def query_environment_status():
    statuses = {}
    for package_name in ("PyQt5", "pandas", "openpyxl", "moviepy", "PySide6", "qfluentwidgets", "loguru", "cv2", "pymysql"):
        try:
            __import__(package_name)
            statuses[package_name] = "ok"
        except Exception as exc:
            statuses[package_name] = f"missing: {exc}"
    statuses["ffprobe"] = "ok" if shutil.which("ffprobe") else "missing"
    mediainfo_path = str(load_settings()["tools"]["mediainfo_path"]).strip()
    mediainfo_available = False
    if mediainfo_path:
        mediainfo_available = Path(mediainfo_path).exists()
    if not mediainfo_available:
        mediainfo_available = bool(shutil.which("mediainfo"))
    statuses["mediainfo"] = "ok" if mediainfo_available else "missing"
    statuses["mysql_storage"] = get_storage().status_text()
    return statuses


def format_file_size(size_bytes):
    size = float(size_bytes)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} PB"


def find_video_files(source_dir, extensions=None):
    extensions = {item.lower() for item in (extensions or VIDEO_EXTENSIONS)}
    files = []
    for path in Path(source_dir).rglob("*"):
        if path.is_file() and path.suffix.lower() in extensions:
            files.append(path)
    return sorted(files)


def safe_target_file(target_file):
    candidate = Path(target_file)
    if not candidate.exists():
        return candidate
    counter = 1
    while True:
        new_candidate = candidate.with_name(f"{candidate.stem}_{counter}{candidate.suffix}")
        if not new_candidate.exists():
            return new_candidate
        counter += 1


def remove_empty_directories(source_dir, remove_root=False):
    source = Path(source_dir)
    removed = []
    for current in sorted(source.rglob("*"), reverse=True):
        if current.is_dir():
            try:
                next(current.iterdir())
            except StopIteration:
                current.rmdir()
                removed.append(current)
    if remove_root and source.exists():
        try:
            next(source.iterdir())
        except StopIteration:
            source.rmdir()
            removed.append(source)
    return removed


def ffprobe_json(video_path):
    command = [
        "ffprobe",
        "-v",
        "quiet",
        "-print_format",
        "json",
        "-show_format",
        "-show_streams",
        str(video_path),
    ]
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=20,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or f"ffprobe failed: {video_path}")
    return json.loads(result.stdout)


def get_video_dimensions(video_path):
    try:
        data = ffprobe_json(video_path)
        for stream in data.get("streams", []):
            if stream.get("codec_type") != "video":
                continue
            width = int(stream.get("width", 0) or 0)
            height = int(stream.get("height", 0) or 0)
            rotation = 0
            tags = stream.get("tags") or {}
            side_data = stream.get("side_data_list") or []
            if "rotate" in tags:
                rotation = int(tags.get("rotate", 0) or 0)
            else:
                for item in side_data:
                    if "rotation" in item:
                        rotation = int(item.get("rotation", 0) or 0)
                        break
            if rotation in (90, 270):
                width, height = height, width
            if width > 0 and height > 0:
                return width, height
    except FileNotFoundError:
        raise RuntimeError("ffprobe not found. Please install FFmpeg first.")
    except Exception as exc:
        raise RuntimeError(f"failed to read video dimensions: {video_path} - {exc}")
    raise RuntimeError(f"unable to parse video dimensions: {video_path}")


def get_video_duration_seconds(video_path):
    try:
        data = ffprobe_json(video_path)
        for stream in data.get("streams", []):
            if stream.get("codec_type") == "video" and stream.get("duration"):
                return float(stream["duration"])
        fmt = data.get("format") or {}
        if fmt.get("duration"):
            return float(fmt["duration"])
    except FileNotFoundError:
        raise RuntimeError("ffprobe not found. Please install FFmpeg first.")
    except Exception as exc:
        raise RuntimeError(f"failed to read video duration: {video_path} - {exc}")
    raise RuntimeError(f"unable to parse video duration: {video_path}")


def build_timestamp(pattern):
    return datetime.now().strftime(pattern)


参数校验错误 = ParameterValidationError
拆分关键词 = split_keywords
校验目录 = ensure_directory
校验文件 = ensure_file
校验输出路径 = ensure_output_path
捕获日志 = capture_logs
查询环境状态 = query_environment_status
格式化文件大小 = format_file_size
查找视频文件 = find_video_files
安全目标文件 = safe_target_file
清理空目录 = remove_empty_directories
获取视频尺寸 = get_video_dimensions
获取视频时长秒数 = get_video_duration_seconds
生成时间戳 = build_timestamp
