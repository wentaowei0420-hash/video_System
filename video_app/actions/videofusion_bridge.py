import argparse
import json
import os
import sys
import traceback
from pathlib import Path


SUPPORTED_VIDEO_EXTENSIONS = {
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
    ".ts",
}


def _as_bool(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return bool(value)


def _prepare_runtime(project_root: Path, runtime_root: Path, source_root: Path):
    source_root = source_root.resolve()
    project_root = project_root.resolve()
    search_paths = [str(project_root), str(source_root)]
    for path in reversed(search_paths):
        if path not in sys.path:
            sys.path.insert(0, path)
    os.chdir(source_root)


def _collect_input_files(payload):
    files = []
    for item in payload.get("input_files", []):
        path = Path(item)
        if path.exists() and path.is_file() and path.suffix.lower() in SUPPORTED_VIDEO_EXTENSIONS:
            files.append(path)
    return sorted(files)


def _enum_from_value(enum_type, raw_value, default_member):
    if raw_value is None or raw_value == "":
        return default_member
    for member in enum_type:
        if raw_value == member.value or raw_value == member.name or raw_value == member.name.lower():
            return member
    return default_member


def _configure_videofusion(payload):
    from src.config import VideoProcessEngine, cfg
    from src.core import paths as vf_paths

    output_dir = Path(payload["output_dir"])
    temp_dir = Path(payload["temp_dir"])
    ffmpeg_file = Path(payload["ffmpeg_file"])

    output_dir.mkdir(parents=True, exist_ok=True)
    temp_dir.mkdir(parents=True, exist_ok=True)

    engine = VideoProcessEngine.FFmpeg
    if str(payload.get("engine", "ffmpeg")).strip().lower() == "opencv":
        engine = VideoProcessEngine.OpenCV

    cfg.set(cfg.output_dir, str(output_dir))
    cfg.set(cfg.temp_dir, str(temp_dir))
    cfg.set(cfg.ffmpeg_file, str(ffmpeg_file))
    cfg.set(cfg.video_process_engine, engine)
    cfg.set(cfg.merge_video, _as_bool(payload.get("merge_video", True)))
    cfg.set(cfg.delete_temp_dir, _as_bool(payload.get("delete_temp_dir", True)))
    cfg.set(cfg.video_fps, int(payload.get("video_fps", 30)))
    cfg.set(cfg.deband, _as_bool(payload.get("deband", False)))
    cfg.set(cfg.deblock, _as_bool(payload.get("deblock", False)))
    cfg.set(cfg.shake, _as_bool(payload.get("shake", False)))
    cfg.set(cfg.video_sample_frame_number, int(payload.get("video_sample_frame_number", 500)))
    vf_paths.FFMPEG_FILE = ffmpeg_file
    return cfg


def _run_direct_merge(payload, input_files):
    from src.common.ffmpeg_handler import FFmpegHandler
    from src.utils import move_file_to_output_dir

    handler = FFmpegHandler()
    merged_file = handler.merge_videos(input_files)
    output_dir = move_file_to_output_dir([merged_file])
    final_files = sorted(output_dir.glob("*.mp4"))
    return {
        "mode": "direct_merge",
        "output_dir": str(output_dir),
        "output_files": [str(path) for path in final_files],
        "input_count": len(input_files),
    }


def _run_process_then_merge(payload, input_files):
    import cv2
    from src.common.program_coordinator import ProgramCoordinator
    from src.core.enums import Orientation, Rotation

    if not hasattr(cv2, "VideoCapture"):
        raise RuntimeError("当前环境仅启用了 VideoFusion 直接合并模式；预处理后合并还需要完整的 OpenCV 运行依赖。")

    orientation = _enum_from_value(
        Orientation,
        str(payload.get("orientation", "vertical")).strip().lower(),
        Orientation.VERTICAL,
    )
    rotation = _enum_from_value(
        Rotation,
        str(payload.get("rotation", "nothing")).strip().lower(),
        Rotation.NOTHING,
    )

    original_startfile = getattr(os, "startfile", None)
    try:
        os.startfile = lambda *args, **kwargs: None
        output_dir = ProgramCoordinator().process(input_files, orientation, rotation)
    finally:
        if original_startfile is not None:
            os.startfile = original_startfile
        else:
            delattr(os, "startfile")

    if output_dir is None:
        raise RuntimeError("VideoFusion 处理被中断，未生成输出目录。")
    output_dir = Path(output_dir)
    final_files = sorted(output_dir.glob("*.mp4"))
    return {
        "mode": "process_then_merge",
        "output_dir": str(output_dir),
        "output_files": [str(path) for path in final_files],
        "input_count": len(input_files),
    }


def run_bridge(payload):
    project_root = Path(__file__).resolve().parents[2]
    runtime_root = Path(payload["runtime_root"])
    source_root = Path(payload["source_root"])
    _prepare_runtime(project_root, runtime_root, source_root)

    cfg = _configure_videofusion(payload)
    input_files = _collect_input_files(payload)
    if not input_files:
        raise RuntimeError("待处理目录中没有可供 VideoFusion 使用的视频文件。")

    ffmpeg_file = Path(payload["ffmpeg_file"])
    if not ffmpeg_file.exists():
        raise RuntimeError(f"FFmpeg 文件不存在: {ffmpeg_file}")

    mode = str(payload.get("run_mode", "direct_merge")).strip().lower()
    result = _run_direct_merge(payload, input_files) if mode == "direct_merge" else _run_process_then_merge(payload, input_files)
    result["config_snapshot"] = {
        "output_dir": cfg.get(cfg.output_dir),
        "temp_dir": cfg.get(cfg.temp_dir),
        "ffmpeg_file": cfg.get(cfg.ffmpeg_file),
        "engine": getattr(cfg.get(cfg.video_process_engine), "name", str(cfg.get(cfg.video_process_engine))),
        "merge_video": cfg.get(cfg.merge_video),
        "video_fps": cfg.get(cfg.video_fps),
        "deband": cfg.get(cfg.deband),
        "deblock": cfg.get(cfg.deblock),
        "shake": cfg.get(cfg.shake),
        "video_sample_frame_number": cfg.get(cfg.video_sample_frame_number),
    }
    return result


def main():
    parser = argparse.ArgumentParser(description="VideoFusion source bridge")
    parser.add_argument("--payload", required=True)
    parser.add_argument("--result", required=True)
    args = parser.parse_args()

    payload_path = Path(args.payload)
    result_path = Path(args.result)
    payload = json.loads(payload_path.read_text(encoding="utf-8"))

    try:
        result = {"success": True, "message": "VideoFusion bridge finished", "data": run_bridge(payload)}
    except Exception as exc:
        result = {
            "success": False,
            "message": str(exc),
            "logs": traceback.format_exc(),
            "data": {},
        }

    result_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
