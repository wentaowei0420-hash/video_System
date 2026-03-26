import json
import shutil
from pathlib import Path

from video_app.actions.common import 上报进度, 缩放进度, 返回成功
from video_app.core.utils import (
    安全目标文件,
    格式化文件大小,
    捕获日志,
    查找视频文件,
    获取视频尺寸,
    获取视频时长秒数,
    校验目录,
    校验输出路径,
)


def 横竖屏分类(params, progress=None):
    source = 校验目录(params.get("source_dir"), "源目录")
    landscape_name = (params.get("landscape_name") or "landscape").strip()
    portrait_name = (params.get("portrait_name") or "portrait").strip()
    square_name = (params.get("square_name") or "square").strip()
    copy_files = bool(params.get("copy_files", False))
    dry_run = bool(params.get("dry_run", False))
    report = bool(params.get("report", True))

    def runner():
        上报进度(progress, 5, "准备中", "正在扫描待分类视频。")
        categories = {
            "landscape": source / landscape_name,
            "portrait": source / portrait_name,
            "square": source / square_name,
        }
        if not dry_run:
            for directory in categories.values():
                directory.mkdir(parents=True, exist_ok=True)

        stats = {"landscape": 0, "portrait": 0, "square": 0, "unknown": 0}
        report_lines = ["视频画幅分类报告", "=" * 60, ""]
        files = [item for item in source.iterdir() if item.is_file() and item.suffix.lower() == ".mp4"]
        上报进度(progress, 12, "扫描完成", f"共找到 {len(files)} 个视频。")
        print(f"扫描目录: {source}")
        print(f"待分类文件数: {len(files)}")
        for index, file_path in enumerate(files, start=1):
            width, height = 获取视频尺寸(file_path)
            ratio = width / height if height else 0
            if abs(ratio - 1.0) < 0.05:
                category = "square"
            elif ratio > 1.0:
                category = "landscape"
            else:
                category = "portrait"
            stats[category] += 1
            report_lines.append(f"{file_path.name}\t{width}x{height}\t{category}")
            if not dry_run:
                target_dir = categories[category]
                target_file = 安全目标文件(target_dir / file_path.name)
                if copy_files:
                    shutil.copy2(str(file_path), str(target_file))
                else:
                    shutil.move(str(file_path), str(target_file))
            上报进度(progress, 缩放进度(index, len(files), 12, 92), "分类视频", f"已处理 {index}/{len(files)}")
            print(f"{file_path.name} -> {category}")
        report_path = ""
        if report:
            上报进度(progress, 96, "生成报告", "正在输出分类报告。")
            report_file = source / "video_classification_report.txt"
            report_file.write_text("\n".join(report_lines), encoding="utf-8")
            report_path = str(report_file)
        上报进度(progress, 100, "已完成", "横竖屏分类完成。")
        return {"stats": stats, "report_path": report_path}

    result, logs = 捕获日志(runner)
    return 返回成功("横竖屏分类已完成", logs, result)


def _format_duration_value(value):
    value = float(value or 0)
    if abs(value - round(value)) < 1e-6:
        return str(int(round(value)))
    return f"{value:.1f}".rstrip("0").rstrip(".")


def _build_duration_segments(start_seconds, end_seconds, segment_count):
    start_seconds = float(start_seconds or 0)
    end_seconds = float(end_seconds or 0)
    segment_count = int(segment_count or 0)
    if start_seconds < 0:
        raise ValueError("起始时长不能小于 0 秒。")
    if end_seconds <= start_seconds:
        raise ValueError("结束时长必须大于起始时长。")
    if segment_count < 1:
        raise ValueError("分段数量必须至少为 1。")

    span = (end_seconds - start_seconds) / float(segment_count)
    segments = []
    current_start = start_seconds
    for index in range(segment_count):
        current_end = end_seconds if index == segment_count - 1 else start_seconds + span * (index + 1)
        label = f"{_format_duration_value(current_start)}-{_format_duration_value(current_end)}秒"
        segments.append(
            {
                "start": current_start,
                "end": current_end,
                "label": label,
            }
        )
        current_start = current_end
    return {
        "segments": segments,
        "underflow_label": f"{_format_duration_value(start_seconds)}秒以下" if start_seconds > 0 else "",
        "overflow_label": f"{_format_duration_value(end_seconds)}秒以上",
        "start_seconds": start_seconds,
        "end_seconds": end_seconds,
        "segment_count": segment_count,
    }


def _duration_strategy(strategy, params=None):
    strategy = str(strategy or "basic").strip()
    if strategy == "ultra_short":
        return _build_duration_segments(0, 60, 12)
    if strategy == "custom":
        return _build_duration_segments(
            params.get("range_start_seconds", 0),
            params.get("range_end_seconds", 60),
            params.get("segment_count", 4),
        )
    return {
        "segments": [
            {"start": 0, "end": 15, "label": "0-15秒"},
            {"start": 15, "end": 60, "label": "15-60秒"},
        ],
        "underflow_label": "",
        "overflow_label": "60秒以上",
        "start_seconds": 0,
        "end_seconds": 60,
        "segment_count": 2,
    }


def _duration_category(seconds, strategy, params=None):
    config = _duration_strategy(strategy, params=params or {})
    normalized_seconds = float(seconds or 0)
    underflow_label = str(config.get("underflow_label") or "").strip()
    segments = list(config.get("segments") or [])

    if underflow_label and segments and normalized_seconds < float(segments[0]["start"]):
        return underflow_label

    for index, segment in enumerate(segments):
        start = float(segment["start"])
        end = float(segment["end"])
        is_last = index == len(segments) - 1
        if start <= normalized_seconds < end or (is_last and normalized_seconds <= end):
            return segment["label"]
    return config.get("overflow_label") or "未分类"


def _duration_scan(files, strategy, params=None, progress=None):
    results = []
    total_size = 0
    total_duration = 0.0
    for index, file_path in enumerate(files, start=1):
        size_bytes = file_path.stat().st_size
        seconds = 获取视频时长秒数(file_path)
        category = _duration_category(seconds, strategy, params=params or {})
        item = {
            "name": file_path.name,
            "path": str(file_path),
            "size_bytes": size_bytes,
            "size_text": 格式化文件大小(size_bytes),
            "duration_seconds": round(seconds, 2),
            "category": category,
        }
        results.append(item)
        total_size += size_bytes
        total_duration += seconds
        上报进度(progress, 缩放进度(index, len(files), 14, 58), "分析时长", f"已分析 {index}/{len(files)}")
        print(f"{file_path.name} -> {category} | {seconds:.2f}s | {格式化文件大小(size_bytes)}")
    stats = {
        "file_count": len(results),
        "total_size": 格式化文件大小(total_size),
        "total_duration_seconds": round(total_duration, 2),
        "avg_duration_seconds": round(total_duration / len(results), 2) if results else 0,
    }
    return results, stats


def 时长分类(params, progress=None):
    strategy = params.get("strategy") or "basic"
    source = 校验目录(params.get("source_dir"), "源目录")
    output = 校验输出路径(params.get("output_dir"), "输出目录", required=False)
    batch_size = int(params.get("batch_size", 100))
    move_files = bool(params.get("move_files", True))
    scan_only = bool(params.get("scan_only", False))

    def runner():
        上报进度(progress, 5, "准备中", "正在扫描待处理视频。")
        files = 查找视频文件(source, extensions={".mp4"})
        上报进度(progress, 12, "扫描完成", f"共找到 {len(files)} 个视频。")
        print(f"扫描目录: {source}")
        print(f"待处理文件数: {len(files)}")
        duration_config = _duration_strategy(strategy, params=params)
        print(
            "时长分段配置: "
            + json.dumps(
                {
                    "strategy": strategy,
                    "start_seconds": duration_config.get("start_seconds"),
                    "end_seconds": duration_config.get("end_seconds"),
                    "segment_count": duration_config.get("segment_count"),
                    "segments": [segment["label"] for segment in duration_config.get("segments", [])],
                    "underflow_label": duration_config.get("underflow_label", ""),
                    "overflow_label": duration_config.get("overflow_label", ""),
                },
                ensure_ascii=False,
            )
        )
        results, stats = _duration_scan(files, strategy, params=params, progress=progress)
        stats["duration_config"] = {
            "strategy": strategy,
            "start_seconds": duration_config.get("start_seconds"),
            "end_seconds": duration_config.get("end_seconds"),
            "segment_count": duration_config.get("segment_count"),
            "segments": [segment["label"] for segment in duration_config.get("segments", [])],
            "underflow_label": duration_config.get("underflow_label", ""),
            "overflow_label": duration_config.get("overflow_label", ""),
        }
        if scan_only:
            print(f"统计: {json.dumps(stats, ensure_ascii=False)}")
            上报进度(progress, 100, "已完成", "时长分析完成。")
            return {"stats": stats, "result_count": len(results)}

        output_dir = output if output else source
        moved_count = 0
        failed_count = 0
        processed_batches = 0
        for start in range(0, len(results), batch_size):
            processed_batches += 1
            batch = results[start : start + batch_size]
            print(f"开始处理第 {processed_batches} 批，共 {len(batch)} 个文件")
            for item in batch:
                try:
                    source_path = Path(item["path"])
                    target_dir = output_dir / item["category"]
                    target_dir.mkdir(parents=True, exist_ok=True)
                    safe_target = 安全目标文件(target_dir / source_path.name)
                    if move_files:
                        shutil.move(str(source_path), str(safe_target))
                    else:
                        shutil.copy2(str(source_path), str(safe_target))
                    moved_count += 1
                    上报进度(progress, 缩放进度(moved_count + failed_count, len(results), 58, 100), "归类文件", f"已处理 {moved_count + failed_count}/{len(results)}")
                except Exception as exc:
                    failed_count += 1
                    上报进度(progress, 缩放进度(moved_count + failed_count, len(results), 58, 100), "归类文件", f"已处理 {moved_count + failed_count}/{len(results)}")
                    print(f"处理失败: {item['name']} - {exc}")
        return {
            "stats": stats,
            "processed_batches": processed_batches,
            "moved_count": moved_count,
            "failed_count": failed_count,
        }

    result, logs = 捕获日志(runner)
    return 返回成功("时长分类已完成", logs, result)


aspect_sort = 横竖屏分类
duration_sort = 时长分类
