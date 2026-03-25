import json
import shutil
import subprocess
import sys
import tempfile
import traceback
from datetime import datetime
from pathlib import Path

from video_app.actions.common import 上报进度, 缩放进度, 返回失败, 返回成功
from video_app.core.utils import (
    安全目标文件,
    参数校验错误,
    捕获日志,
    查找视频文件,
    校验文件,
    校验目录,
)


def 搬运流水线处理(params, progress=None):
    source_output_dir = 校验目录(params.get("source_output_dir"), "产出目录")
    target_dir = 校验目录(params.get("target_dir"), "目标目录")
    temp_dir = 校验目录(params.get("temp_dir"), "临时目录")
    queue_dir = 校验目录(params.get("queue_dir"), "待处理队列目录")

    def runner():
        上报进度(progress, 5, "准备中", "正在清理临时目录。")
        temp_deleted = 0
        temp_files = list(temp_dir.glob("*.mp4"))
        for index, file_path in enumerate(temp_files, start=1):
            file_path.unlink()
            temp_deleted += 1
            上报进度(progress, 缩放进度(index, len(temp_files), 5, 20), "清理临时目录", f"已清理 {index}/{len(temp_files)}")
        print(f"清理临时目录数量: {temp_deleted}")

        上报进度(progress, 24, "处理队列", "正在搬运待处理队列。")
        queue_folders = sorted([item for item in queue_dir.iterdir() if item.is_dir()], key=lambda x: x.name)
        queue_moved = 0
        processed_folder = ""
        if queue_folders:
            first_folder = queue_folders[0]
            processed_folder = first_folder.name
            for file_path in first_folder.iterdir():
                if file_path.is_file():
                    shutil.move(str(file_path), str(temp_dir / file_path.name))
                    queue_moved += 1
            shutil.rmtree(first_folder)
            print(f"已处理队列目录: {first_folder}")
        else:
            print("队列目录中没有待处理子目录")

        output_files = list(source_output_dir.glob("*.mp4"))
        上报进度(progress, 40, "搬运产出", f"共找到 {len(output_files)} 个产出文件。")
        moved_count = 0
        skipped_count = 0
        for index, file_path in enumerate(output_files, start=1):
            safe_target = 安全目标文件(target_dir / file_path.name)
            if safe_target.name != file_path.name and (target_dir / file_path.name).exists():
                skipped_count += 1
            shutil.move(str(file_path), str(safe_target))
            moved_count += 1
            上报进度(progress, 缩放进度(index, len(output_files), 40, 100), "搬运产出", f"已处理 {index}/{len(output_files)}")
            print(f"已搬运产出文件: {safe_target.name}")
        return {
            "temp_deleted": temp_deleted,
            "queue_moved": queue_moved,
            "processed_folder": processed_folder,
            "output_moved": moved_count,
            "output_skipped_conflict": skipped_count,
        }

    result, logs = 捕获日志(runner)
    return 返回成功("搬运流水线处理已完成", logs, result)


def _build_runtime_output_dir(path_text, field_name):
    if not path_text:
        raise 参数校验错误(f"{field_name} 不能为空")
    path = Path(path_text)
    path.mkdir(parents=True, exist_ok=True)
    if not path.is_dir():
        raise 参数校验错误(f"{field_name} 不是目录: {path}")
    return path


def _normalized_path_text(path_text):
    try:
        return str(Path(path_text).resolve()).replace("/", "\\").lower()
    except Exception:
        return str(path_text or "").strip().replace("/", "\\").lower()


def _is_temp_source_dir(input_dir_text, runtime_root, temp_dir_text):
    normalized_input = _normalized_path_text(input_dir_text)
    if not normalized_input:
        return False
    temp_candidates = {
        _normalized_path_text(temp_dir_text),
        _normalized_path_text(runtime_root / "Temp"),
    }
    if normalized_input in temp_candidates:
        return True
    return Path(str(input_dir_text)).name.lower() == "temp"


def _rename_output_files(output_dir, progress=None, start=82, end=90):
    renamed_files = []
    files = sorted(output_dir.glob("*.mp4"))
    for index, file_path in enumerate(files, start=1):
        timestamp = datetime.fromtimestamp(file_path.stat().st_mtime).strftime("%Y-%m-%d %H-%M-%S")
        safe_target = 安全目标文件(file_path.with_name(f"{timestamp} {file_path.name}"))
        if safe_target == file_path:
            renamed_files.append(str(file_path))
            上报进度(progress, 缩放进度(index, len(files), start, end), "整理输出", f"已处理 {index}/{len(files)}")
            continue
        file_path.rename(safe_target)
        renamed_files.append(str(safe_target))
        上报进度(progress, 缩放进度(index, len(files), start, end), "整理输出", f"已处理 {index}/{len(files)}")
        print(f"已给产出文件增加时间戳: {safe_target.name}")
    return renamed_files


def _deliver_output_files(output_dir, target_dir, progress=None, start=90, end=100):
    moved_count = 0
    renamed_count = 0
    delivered_files = []
    files = sorted(output_dir.glob("*.mp4"))
    for index, file_path in enumerate(files, start=1):
        safe_target = 安全目标文件(target_dir / file_path.name)
        if safe_target.name != file_path.name:
            renamed_count += 1
        shutil.move(str(file_path), str(safe_target))
        moved_count += 1
        delivered_files.append(str(safe_target))
        上报进度(progress, 缩放进度(index, len(files), start, end), "交付文件", f"已处理 {index}/{len(files)}")
        print(f"已搬运产出文件: {safe_target.name}")
    return {
        "moved_count": moved_count,
        "renamed_count": renamed_count,
        "delivered_files": delivered_files,
    }


def videofusion_merge_action(params, progress=None):
    project_root = Path(__file__).resolve().parents[2]
    action_dir = Path(__file__).resolve().parent
    bridge_candidates = [
        action_dir / "videofusion_bridge.py",
        action_dir / "VideoFusion桥接.py",
    ]
    bridge_script = next((path for path in bridge_candidates if path.exists()), None)
    if bridge_script is None:
        return 返回失败(
            "未找到 VideoFusion 桥接脚本: "
            + " / ".join(str(path) for path in bridge_candidates)
        )

    上报进度(progress, 5, "准备中", "正在校验 VideoFusion 运行参数。")
    source_root = 校验目录(params.get("source_root"), "VideoFusion 源码目录")
    runtime_root = 校验目录(params.get("runtime_root"), "VideoFusion 运行时目录")
    temp_dir_text = str(params.get("temp_dir") or (runtime_root / "Temp"))
    input_dir_text = str(params.get("input_dir") or "").strip()
    if _is_temp_source_dir(input_dir_text, runtime_root, temp_dir_text):
        return 返回失败("“待合并目录”填写成了临时目录。请改为真正存放待合并视频的文件夹，不要选择 Temp 目录。")
    input_dir = 校验目录(input_dir_text, "待合并目录")
    output_dir = _build_runtime_output_dir(params.get("output_dir"), "输出目录")
    temp_dir = _build_runtime_output_dir(temp_dir_text, "临时目录")

    ffmpeg_candidate = params.get("ffmpeg_file")
    if not ffmpeg_candidate:
        packaged_ffmpeg = runtime_root / "bin" / "ffmpeg.exe"
        source_ffmpeg = source_root / "bin" / "ffmpeg.exe"
        ffmpeg_candidate = str(packaged_ffmpeg if packaged_ffmpeg.exists() else source_ffmpeg)
    ffmpeg_file = 校验文件(ffmpeg_candidate, "FFmpeg 文件", required=True)

    target_dir = None
    if params.get("target_dir"):
        target_dir = _build_runtime_output_dir(params.get("target_dir"), "目标目录")

    queue_dir = None
    if params.get("queue_dir"):
        queue_dir = 校验目录(params.get("queue_dir"), "待处理队列目录")

    input_files = 查找视频文件(input_dir)
    if not input_files:
        return 返回失败(f"待合并目录中没有可用视频文件: {input_dir}")
    上报进度(progress, 12, "扫描完成", f"共找到 {len(input_files)} 个待合并视频。")

    payload = {
        "source_root": str(source_root),
        "runtime_root": str(runtime_root),
        "input_files": [str(path) for path in input_files],
        "output_dir": str(output_dir),
        "temp_dir": str(temp_dir),
        "ffmpeg_file": str(ffmpeg_file),
        "run_mode": params.get("run_mode") or "direct_merge",
        "orientation": params.get("orientation") or "vertical",
        "rotation": params.get("rotation") or "nothing",
        "engine": params.get("engine") or "ffmpeg",
        "merge_video": bool(params.get("merge_video", True)),
        "delete_temp_dir": bool(params.get("delete_temp_dir", True)),
        "video_fps": int(params.get("video_fps", 30)),
        "deband": bool(params.get("deband", False)),
        "deblock": bool(params.get("deblock", False)),
        "shake": bool(params.get("shake", False)),
        "video_sample_frame_number": int(params.get("video_sample_frame_number", 500)),
    }

    bridge_result = {}
    logs = ""
    try:
        with tempfile.TemporaryDirectory(prefix="videofusion_bridge_") as workspace:
            payload_path = Path(workspace) / "payload.json"
            result_path = Path(workspace) / "result.json"
            payload_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
            上报进度(progress, 20, "启动内核", "正在调用 VideoFusion 桥接。")

            completed = subprocess.run(
                [sys.executable, str(bridge_script), "--payload", str(payload_path), "--result", str(result_path)],
                cwd=str(project_root),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            logs = "\n".join(part for part in ((completed.stdout or "").strip(), (completed.stderr or "").strip()) if part)
            if result_path.exists():
                bridge_result = json.loads(result_path.read_text(encoding="utf-8"))
            上报进度(progress, 76, "内核完成", "VideoFusion 内核已返回结果。")
            if completed.returncode != 0 or not bridge_result.get("success", False):
                if bridge_result.get("logs"):
                    logs = "\n".join(part for part in (logs, bridge_result["logs"]) if part)
                return 返回失败(bridge_result.get("message") or "VideoFusion 内核执行失败", logs, bridge_result.get("data"))
    except Exception:
        return 返回失败("VideoFusion 桥接执行失败", traceback.format_exc())

    result_data = bridge_result.get("data", {})
    final_output_dir = Path(result_data.get("output_dir") or output_dir)

    renamed_files = []
    if bool(params.get("rename_output", True)):
        上报进度(progress, 82, "整理输出", "正在为输出文件补充时间戳。")
        renamed_files = _rename_output_files(final_output_dir, progress=progress, start=82, end=90)
        result_data["output_files"] = renamed_files
        result_data["renamed_files"] = renamed_files

    if target_dir and queue_dir:
        上报进度(progress, 90, "流水线交付", "正在执行后续搬运流水线。")
        pipeline_response = 搬运流水线处理(
            {
                "source_output_dir": str(final_output_dir),
                "target_dir": str(target_dir),
                "temp_dir": str(input_dir),
                "queue_dir": str(queue_dir),
            },
            progress=lambda percent, stage, detail: 上报进度(
                progress,
                int(90 + max(0, min(100, percent)) * 10 / 100),
                stage,
                detail,
            ),
        )
        logs = "\n".join(part for part in (logs, pipeline_response.get("logs", "")) if part)
        result_data["pipeline_result"] = pipeline_response.get("data", {})
        if not pipeline_response.get("success"):
            return 返回失败(pipeline_response.get("message") or "搬运流水线处理失败", logs, result_data)
    elif target_dir:
        上报进度(progress, 90, "交付文件", "正在搬运最终输出。")
        result_data["delivery_result"] = _deliver_output_files(final_output_dir, target_dir, progress=progress, start=90, end=100)

    上报进度(progress, 100, "已完成", "VideoFusion 合并任务完成。")
    return 返回成功("VideoFusion 内核合并已完成", logs, result_data)


pipeline_move = 搬运流水线处理
videofusion_merge = videofusion_merge_action
