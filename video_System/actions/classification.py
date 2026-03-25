import json
import shutil
from pathlib import Path

from video_system.actions.common import 返回成功
from video_system.core.utils import (
    安全目标文件,
    格式化文件大小,
    捕获日志,
    查找视频文件,
    获取视频尺寸,
    获取视频时长秒数,
    校验目录,
    校验输出路径,
)


def 横竖屏分类(params):
    source = 校验目录(params.get("source_dir"), "源目录")
    landscape_name = (params.get("landscape_name") or "landscape").strip()
    portrait_name = (params.get("portrait_name") or "portrait").strip()
    square_name = (params.get("square_name") or "square").strip()
    copy_files = bool(params.get("copy_files", False))
    dry_run = bool(params.get("dry_run", False))
    report = bool(params.get("report", True))

    def runner():
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
        print(f"扫描目录: {source}")
        print(f"待分类文件数: {len(files)}")
        for file_path in files:
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
            print(f"{file_path.name} -> {category}")
        report_path = ""
        if report:
            report_file = source / "video_classification_report.txt"
            report_file.write_text("\n".join(report_lines), encoding="utf-8")
            report_path = str(report_file)
        return {"stats": stats, "report_path": report_path}

    result, logs = 捕获日志(runner)
    return 返回成功("横竖屏分类已完成", logs, result)


def _duration_strategy(strategy):
    if strategy == "ultra_short":
        return [
            (5, "0-5秒"),
            (10, "5-10秒"),
            (15, "10-15秒"),
            (20, "15-20秒"),
            (25, "20-25秒"),
            (30, "25-30秒"),
            (35, "30-35秒"),
            (40, "35-40秒"),
            (45, "40-45秒"),
            (50, "45-50秒"),
            (55, "50-55秒"),
            (60, "55-60秒"),
        ], "60秒以上"
    return [(15, "0-15秒"), (60, "15-60秒")], "60秒以上"


def _duration_category(seconds, strategy):
    ranges, overflow_label = _duration_strategy(strategy)
    for limit, label in ranges:
        if seconds <= limit:
            return label
    return overflow_label


def _duration_scan(files, strategy):
    results = []
    total_size = 0
    total_duration = 0.0
    for file_path in files:
        size_bytes = file_path.stat().st_size
        seconds = 获取视频时长秒数(file_path)
        category = _duration_category(seconds, strategy)
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
        print(f"{file_path.name} -> {category} | {seconds:.2f}s | {格式化文件大小(size_bytes)}")
    stats = {
        "file_count": len(results),
        "total_size": 格式化文件大小(total_size),
        "total_duration_seconds": round(total_duration, 2),
        "avg_duration_seconds": round(total_duration / len(results), 2) if results else 0,
    }
    return results, stats


def 时长分类(params):
    strategy = params.get("strategy") or "basic"
    source = 校验目录(params.get("source_dir"), "源目录")
    output = 校验输出路径(params.get("output_dir"), "输出目录", required=False)
    batch_size = int(params.get("batch_size", 100))
    move_files = bool(params.get("move_files", True))
    scan_only = bool(params.get("scan_only", False))

    def runner():
        files = 查找视频文件(source, extensions={".mp4"})
        print(f"扫描目录: {source}")
        print(f"待处理文件数: {len(files)}")
        results, stats = _duration_scan(files, strategy)
        if scan_only:
            print(f"统计: {json.dumps(stats, ensure_ascii=False)}")
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
                except Exception as exc:
                    failed_count += 1
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
