import shutil
from datetime import datetime

from video_app.actions.common import 上报进度, 缩放进度, 返回成功
from video_app.core.utils import (
    安全目标文件,
    参数校验错误,
    捕获日志,
    查找视频文件,
    校验目录,
    校验输出路径,
    清理空目录,
)


def 收集文件(params, progress=None):
    source = 校验目录(params.get("source_dir"), "源目录")
    target = 校验输出路径(params.get("target_dir"), "目标目录", required=False)
    keep_structure = bool(params.get("keep_structure", False))
    clean_empty = bool(params.get("clean_empty", False))

    def runner():
        上报进度(progress, 5, "准备中", "正在校验目录并扫描文件。")
        target_dir = target if target else source.parent / f"{source.name}_collected"
        target_dir.mkdir(parents=True, exist_ok=True)
        files = 查找视频文件(source, extensions={".mp4"})
        上报进度(progress, 12, "扫描完成", f"共找到 {len(files)} 个 MP4 文件。")
        print(f"扫描目录: {source}")
        print(f"目标目录: {target_dir}")
        print(f"找到 MP4 数量: {len(files)}")
        moved = 0
        renamed = 0
        for index, file_path in enumerate(files, start=1):
            rel_path = file_path.relative_to(source)
            if keep_structure:
                target_file = target_dir / rel_path
                target_file.parent.mkdir(parents=True, exist_ok=True)
            else:
                target_file = target_dir / file_path.name
            safe_target = 安全目标文件(target_file)
            if safe_target != target_file:
                renamed += 1
            safe_target.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(file_path), str(safe_target))
            moved += 1
            上报进度(progress, 缩放进度(index, len(files), 12, 86), "搬运文件", f"已处理 {index}/{len(files)}")
            if index % 20 == 0 or index == len(files):
                print(f"已处理 {index}/{len(files)}")
        removed_dirs = []
        if clean_empty:
            上报进度(progress, 92, "清理空目录", "正在清理空目录。")
            removed_dirs = 清理空目录(source, remove_root=True)
            print(f"清理空目录数量: {len(removed_dirs)}")
        上报进度(progress, 100, "已完成", "文件整理完成。")
        return {
            "target_path": str(target_dir),
            "file_count": len(files),
            "moved_count": moved,
            "renamed_count": renamed,
            "removed_dir_count": len(removed_dirs),
        }

    result, logs = 捕获日志(runner)
    return 返回成功("收集 / 清理 MP4 已完成", logs, result)


def 按组搬运(params, progress=None):
    source = 校验目录(params.get("source_dir"), "源目录")
    target = 校验输出路径(params.get("target_dir"), "目标目录", required=False)
    group_size = int(params.get("group_size", 88))
    if group_size <= 0:
        raise 参数校验错误("每组数量必须大于 0")

    def runner():
        上报进度(progress, 5, "准备中", "正在扫描待分组文件。")
        target_dir = target if target else source.parent / f"{source.name}_grouped"
        target_dir.mkdir(parents=True, exist_ok=True)
        files = 查找视频文件(source, extensions={".mp4"})
        上报进度(progress, 12, "扫描完成", f"共找到 {len(files)} 个 MP4 文件。")
        print(f"扫描目录: {source}")
        print(f"目标目录: {target_dir}")
        print(f"找到 MP4 数量: {len(files)}")
        moved = 0
        group_count = 0
        for start in range(0, len(files), group_size):
            group_count += 1
            group_dir = target_dir / f"group_{group_count:03d}"
            group_dir.mkdir(parents=True, exist_ok=True)
            for file_path in files[start : start + group_size]:
                safe_target = 安全目标文件(group_dir / file_path.name)
                shutil.move(str(file_path), str(safe_target))
                moved += 1
                上报进度(progress, 缩放进度(moved, len(files), 12, 94), "按组搬运", f"已处理 {moved}/{len(files)}")
            print(f"已完成分组 {group_count}: {group_dir}")
        上报进度(progress, 100, "已完成", "按组搬运完成。")
        return {
            "target_path": str(target_dir),
            "file_count": len(files),
            "group_count": group_count,
            "moved_count": moved,
        }

    result, logs = 捕获日志(runner)
    return 返回成功("按组搬运已完成", logs, result)


def 扁平搬运(params, progress=None):
    source = 校验目录(params.get("source_dir"), "源目录")
    target = 校验目录(params.get("target_dir"), "目标目录")

    def runner():
        上报进度(progress, 5, "准备中", "正在扫描待搬运文件。")
        files = 查找视频文件(source, extensions={".mp4"})
        上报进度(progress, 12, "扫描完成", f"共找到 {len(files)} 个 MP4 文件。")
        print(f"扫描目录: {source}")
        print(f"目标目录: {target}")
        print(f"找到 MP4 数量: {len(files)}")
        moved = 0
        renamed = 0
        for index, file_path in enumerate(files, start=1):
            safe_target = 安全目标文件(target / file_path.name)
            if safe_target.name != file_path.name:
                renamed += 1
            shutil.move(str(file_path), str(safe_target))
            moved += 1
            上报进度(progress, 缩放进度(index, len(files), 12, 100), "扁平搬运", f"已处理 {index}/{len(files)}")
            print(f"已搬运: {file_path.name} -> {safe_target.name}")
        return {"file_count": len(files), "moved_count": moved, "renamed_count": renamed}

    result, logs = 捕获日志(runner)
    return 返回成功("扁平搬运已完成", logs, result)


def 父目录前缀重命名(params, progress=None):
    target = 校验目录(params.get("target_dir"), "目标目录")

    def runner():
        files = 查找视频文件(target, extensions={".mp4"})
        上报进度(progress, 8, "准备中", f"共找到 {len(files)} 个待重命名文件。")
        success_count = 0
        skipped_count = 0
        failed_count = 0
        for index, file_path in enumerate(files, start=1):
            parent_name = file_path.parent.name
            expected_name = f"{parent_name}_{file_path.name}"
            if file_path.name.startswith(f"{parent_name}_"):
                skipped_count += 1
                continue
            safe_target = 安全目标文件(file_path.with_name(expected_name))
            try:
                file_path.rename(safe_target)
                success_count += 1
                print(f"已重命名: {file_path.name} -> {safe_target.name}")
            except Exception as exc:
                failed_count += 1
                print(f"重命名失败: {file_path.name} - {exc}")
            上报进度(progress, 缩放进度(index, len(files), 8, 100), "重命名文件", f"已处理 {index}/{len(files)}")
        return {
            "success_count": success_count,
            "skipped_count": skipped_count,
            "failed_count": failed_count,
        }

    result, logs = 捕获日志(runner)
    return 返回成功("父目录前缀重命名已完成", logs, result)


def 时间戳重命名(params, progress=None):
    target = 校验目录(params.get("target_dir"), "目标目录")
    pattern = params.get("pattern") or "%Y-%m-%d %H-%M-%S"

    def runner():
        files = [file_path for file_path in target.iterdir() if file_path.is_file() and file_path.suffix.lower() == ".mp4"]
        上报进度(progress, 8, "准备中", f"共找到 {len(files)} 个待重命名文件。")
        renamed_count = 0
        skipped_count = 0
        for index, file_path in enumerate(files, start=1):
            timestamp = datetime.fromtimestamp(file_path.stat().st_mtime).strftime(pattern.replace(":", "-"))
            if file_path.name.startswith(timestamp):
                skipped_count += 1
                上报进度(progress, 缩放进度(index, len(files), 8, 100), "重命名文件", f"已处理 {index}/{len(files)}")
                continue
            safe_target = 安全目标文件(file_path.with_name(f"{timestamp} {file_path.name}"))
            file_path.rename(safe_target)
            renamed_count += 1
            print(f"已重命名: {safe_target.name}")
            上报进度(progress, 缩放进度(index, len(files), 8, 100), "重命名文件", f"已处理 {index}/{len(files)}")
        return {"renamed_count": renamed_count, "skipped_count": skipped_count}

    result, logs = 捕获日志(runner)
    return 返回成功("时间戳重命名已完成", logs, result)


collect_files = 收集文件
group_move = 按组搬运
flat_move = 扁平搬运
parent_prefix_rename = 父目录前缀重命名
timestamp_rename = 时间戳重命名
