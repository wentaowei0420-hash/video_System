from pathlib import Path


项目根目录 = Path(__file__).resolve().parents[2]
VIDEOFUSION源码目录 = 项目根目录 / "VideoFusion-1.12.5_execode"
VIDEOFUSION运行时目录 = 项目根目录 / "VideoFusion v1.12.5"
VIDEOFUSION默认FFMPEG = VIDEOFUSION运行时目录 / "bin" / "ffmpeg.exe"
VIDEOFUSION默认临时目录 = VIDEOFUSION运行时目录 / "Temp"


旧脚本清单 = [
    {"file": "group_mp4_files.py", "module": "文件整理", "summary": "旧版 MP4 收集脚本，已迁移。"},
    {"file": "group_and_move_mp4_files.py", "module": "文件整理", "summary": "旧版分组搬运脚本，已迁移。"},
    {"file": "vevt视频管理脚本.py", "module": "文件整理", "summary": "旧版搬运和重命名脚本，已迁移。"},
    {"file": "time.py", "module": "文件整理", "summary": "旧版时间戳重命名脚本，已迁移。"},
    {"file": "python video_sorter.py", "module": "分类处理", "summary": "旧版横竖屏分类脚本，已迁移。"},
    {"file": "MP4_manage.py", "module": "分类处理", "summary": "旧版三档时长分类脚本，已迁移。"},
    {"file": "分类脚本副本.py", "module": "分类处理", "summary": "旧版三档分类副本脚本，已迁移。"},
    {"file": "超短视频分类脚本.py", "module": "分类处理", "summary": "旧版超短视频细分脚本，已迁移。"},
    {"file": "视频监测脚本.py", "module": "统计分析", "summary": "旧版 UP 主统计分析脚本，已迁移。"},
    {"file": "vevt关键词检索模块.py", "module": "统计分析", "summary": "旧版关键词整理脚本，已迁移。"},
    {"file": "wangyepaqv.py", "module": "统计分析", "summary": "旧版 Excel 映射重命名脚本，已迁移。"},
    {"file": "move.py", "module": "自动化入口", "summary": "旧版自动搬运脚本，已迁移。"},
    {"file": "自动合并视频脚本.py", "module": "自动化入口", "summary": "旧版外部合并自动化脚本，已迁移。"},
    {"file": "rename.py", "module": "占位", "summary": "空文件。"},
]


正式文件清单 = [
    {"file": "video_system_gui.py", "role": "兼容启动", "summary": "旧启动名兼容壳，自动拉起后端并进入新前端。"},
    {"file": "启动_视频系统后端.py", "role": "启动入口", "summary": "推荐的后端启动脚本。"},
    {"file": "启动_视频系统前端.py", "role": "启动入口", "summary": "推荐的前端启动脚本。"},
    {"file": "视频系统\\前端\\window.py", "role": "前端主窗口", "summary": "主界面布局和页面导航。"},
    {"file": "视频系统\\前端\\widgets.py", "role": "前端组件", "summary": "路径输入、状态卡和动作表单组件。"},
    {"file": "视频系统\\前端\\api.py", "role": "前端请求", "summary": "异步 HTTP 请求工作线程。"},
    {"file": "视频系统\\动作\\文件整理.py", "role": "动作模块", "summary": "文件整理相关动作实现。"},
    {"file": "视频系统\\动作\\分类处理.py", "role": "动作模块", "summary": "横竖屏和时长分类实现。"},
    {"file": "视频系统\\动作\\统计分析.py", "role": "动作模块", "summary": "统计、关键词和 Excel 映射实现。"},
    {"file": "视频系统\\动作\\自动化.py", "role": "动作模块", "summary": "流水线和 VideoFusion 合并实现。"},
    {"file": "视频系统\\动作\\VideoFusion桥接.py", "role": "桥接模块", "summary": "直接调用 VideoFusion 源码能力。"},
]


动作目录 = [
    {
        "id": "file_management",
        "title": "文件整理",
        "description": "统一处理 MP4 收集、搬运、重命名和归档整理任务。",
        "actions": [
            {
                "id": "collect_files",
                "title": "收集 / 清理 MP4",
                "description": "递归收集 MP4；可选保留目录结构，并可在完成后清理空目录。",
                "fields": [
                    {"name": "source_dir", "label": "源目录", "type": "dir", "required": True},
                    {"name": "target_dir", "label": "目标目录", "type": "dir_optional"},
                    {"name": "keep_structure", "label": "保留原始目录结构", "type": "bool", "default": False},
                    {"name": "clean_empty", "label": "收集后清理空目录", "type": "bool", "default": False},
                ],
            },
            {
                "id": "group_move",
                "title": "按组搬运 MP4",
                "description": "将 MP4 按固定数量分组搬运到 group_001 这类目录。",
                "fields": [
                    {"name": "source_dir", "label": "源目录", "type": "dir", "required": True},
                    {"name": "target_dir", "label": "目标目录", "type": "dir_optional"},
                    {"name": "group_size", "label": "每组数量", "type": "int", "default": 88, "min": 1, "max": 100000},
                ],
            },
            {
                "id": "flat_move",
                "title": "扁平搬运 MP4",
                "description": "递归搜集源目录中的 MP4，并直接移动到目标目录。",
                "fields": [
                    {"name": "source_dir", "label": "源目录", "type": "dir", "required": True},
                    {"name": "target_dir", "label": "目标目录", "type": "dir", "required": True},
                ],
            },
            {
                "id": "parent_prefix_rename",
                "title": "父目录前缀重命名",
                "description": "把父目录名加到 MP4 文件名前，便于区分来源。",
                "fields": [
                    {"name": "target_dir", "label": "目标目录", "type": "dir", "required": True},
                ],
            },
            {
                "id": "timestamp_rename",
                "title": "时间戳重命名",
                "description": "按文件修改时间给视频添加时间戳前缀。",
                "fields": [
                    {"name": "target_dir", "label": "目标目录", "type": "dir", "required": True},
                    {"name": "pattern", "label": "时间格式", "type": "text", "default": "%Y-%m-%d %H-%M-%S"},
                ],
            },
        ],
    },
    {
        "id": "classification",
        "title": "分类处理",
        "description": "统一横竖屏分类与时长分类能力。",
        "actions": [
            {
                "id": "aspect_sort",
                "title": "横竖屏分类",
                "description": "按画幅把视频分到 landscape / portrait / square 目录。",
                "fields": [
                    {"name": "source_dir", "label": "源目录", "type": "dir", "required": True},
                    {"name": "landscape_name", "label": "横屏目录名", "type": "text", "default": "landscape"},
                    {"name": "portrait_name", "label": "竖屏目录名", "type": "text", "default": "portrait"},
                    {"name": "square_name", "label": "方屏目录名", "type": "text", "default": "square"},
                    {"name": "copy_files", "label": "复制而不是移动", "type": "bool", "default": False},
                    {"name": "dry_run", "label": "只分析不落盘", "type": "bool", "default": False},
                    {"name": "report", "label": "生成分类报告", "type": "bool", "default": True},
                ],
            },
            {
                "id": "duration_sort",
                "title": "时长分类",
                "description": "按时长区间对视频做扫描、统计和分类搬运，可在页面中配置起止时长和分段数量。",
                "fields": [
                    {
                        "name": "strategy",
                        "label": "分类策略",
                        "type": "select",
                        "default": "basic",
                        "options": [
                            {"label": "三档分类", "value": "basic"},
                            {"label": "三档副本", "value": "basic_copy"},
                            {"label": "超短多档", "value": "ultra_short"},
                            {"label": "自定义区间", "value": "custom"},
                        ],
                    },
                    {"name": "source_dir", "label": "源目录", "type": "dir", "required": True},
                    {"name": "output_dir", "label": "输出目录", "type": "dir_optional"},
                    {
                        "name": "range_start_seconds",
                        "label": "起始时长(秒)",
                        "type": "int",
                        "default": 0,
                        "min": 0,
                        "max": 86400,
                    },
                    {
                        "name": "range_end_seconds",
                        "label": "结束时长(秒)",
                        "type": "int",
                        "default": 60,
                        "min": 1,
                        "max": 86400,
                    },
                    {
                        "name": "segment_count",
                        "label": "分段数量",
                        "type": "int",
                        "default": 4,
                        "min": 1,
                        "max": 100,
                    },
                    {"name": "batch_size", "label": "批次大小", "type": "int", "default": 100, "min": 1, "max": 100000},
                    {"name": "move_files", "label": "移动文件", "type": "bool", "default": True},
                    {"name": "scan_only", "label": "只扫描不搬运", "type": "bool", "default": False},
                ],
            },
        ],
    },
    {
        "id": "analysis",
        "title": "统计分析",
        "description": "统一检索、报表和 Excel 映射重命名能力。",
        "actions": [
            {
                "id": "stats_analysis",
                "title": "UP 主统计分析",
                "description": "从文件名解析 UP 主、发布日期、时长，并导出 Excel 统计。",
                "fields": [
                    {"name": "source_dir", "label": "分析目录", "type": "dir", "required": True},
                    {"name": "output_excel", "label": "输出 Excel", "type": "save_file"},
                ],
            },
            {
                "id": "keyword_sort",
                "title": "关键词整理",
                "description": "按关键词检索文件名并把匹配视频移动到目标目录。",
                "fields": [
                    {"name": "source_dir", "label": "源目录", "type": "dir", "required": True},
                    {"name": "target_dir", "label": "目标目录", "type": "dir", "required": True},
                    {"name": "keywords", "label": "关键词", "type": "textarea", "required": True},
                ],
            },
            {
                "id": "excel_rename",
                "title": "Excel 映射重命名",
                "description": "按 Excel 映射表重命名 MP4，并输出处理报告。",
                "fields": [
                    {"name": "folder_path", "label": "视频目录", "type": "dir", "required": True},
                    {"name": "mapping_file", "label": "映射 Excel", "type": "file_optional"},
                    {"name": "output_excel", "label": "输出报告 Excel", "type": "save_file", "required": True},
                    {"name": "actually_rename", "label": "实际重命名文件", "type": "bool", "default": False},
                    {"name": "backup_original", "label": "备份原文件", "type": "bool", "default": False},
                ],
            },
        ],
    },
    {
        "id": "automation",
        "title": "自动化入口",
        "description": "将原先的自动化脚本改为统一的配置化任务入口。",
        "actions": [
            {
                "id": "pipeline_move",
                "title": "搬运流水线处理",
                "description": "清理临时目录、取出队列中的首个子目录、搬运产出文件到目标目录。",
                "fields": [
                    {"name": "source_output_dir", "label": "产出目录", "type": "dir", "required": True},
                    {"name": "target_dir", "label": "目标目录", "type": "dir", "required": True},
                    {"name": "temp_dir", "label": "临时目录", "type": "dir", "required": True},
                    {"name": "queue_dir", "label": "待处理队列目录", "type": "dir", "required": True},
                ],
            },
            {
                "id": "videofusion_merge",
                "title": "VideoFusion 内核合并",
                "description": "直接调用 VideoFusion 源码内核，可视化写入配置后执行合并，不再依赖 EXE 桌面点击。",
                "fields": [
                    {"name": "source_root", "label": "VideoFusion 源码目录", "type": "dir", "required": True, "default": str(VIDEOFUSION源码目录)},
                    {"name": "runtime_root", "label": "VideoFusion 运行时目录", "type": "dir", "required": True, "default": str(VIDEOFUSION运行时目录)},
                    {"name": "input_dir", "label": "待合并目录", "type": "dir", "required": True},
                    {"name": "output_dir", "label": "输出目录", "type": "dir", "required": True},
                    {"name": "temp_dir", "label": "临时目录", "type": "dir_optional", "default": str(VIDEOFUSION默认临时目录)},
                    {"name": "ffmpeg_file", "label": "FFmpeg 文件", "type": "file_optional", "default": str(VIDEOFUSION默认FFMPEG)},
                    {
                        "name": "run_mode",
                        "label": "执行模式",
                        "type": "select",
                        "default": "direct_merge",
                        "options": [
                            {"label": "直接合并", "value": "direct_merge"},
                            {"label": "预处理后合并", "value": "process_then_merge"},
                        ],
                    },
                    {
                        "name": "orientation",
                        "label": "目标朝向",
                        "type": "select",
                        "default": "vertical",
                        "options": [
                            {"label": "竖屏", "value": "vertical"},
                            {"label": "横屏", "value": "horizontal"},
                        ],
                    },
                    {
                        "name": "rotation",
                        "label": "旋转方式",
                        "type": "select",
                        "default": "nothing",
                        "options": [
                            {"label": "不旋转", "value": "nothing"},
                            {"label": "顺时针 90°", "value": "clockwise"},
                            {"label": "逆时针 90°", "value": "counterclockwise"},
                            {"label": "上下颠倒", "value": "upside_down"},
                        ],
                    },
                    {
                        "name": "engine",
                        "label": "处理引擎",
                        "type": "select",
                        "default": "ffmpeg",
                        "options": [
                            {"label": "FFmpeg", "value": "ffmpeg"},
                            {"label": "OpenCV", "value": "opencv"},
                        ],
                    },
                    {"name": "merge_video", "label": "处理后合并为单文件", "type": "bool", "default": True},
                    {"name": "delete_temp_dir", "label": "完成后清理临时目录", "type": "bool", "default": True},
                    {"name": "video_fps", "label": "输出帧率", "type": "int", "default": 30, "min": 1, "max": 144},
                    {"name": "deband", "label": "视频去色带", "type": "bool", "default": False},
                    {"name": "deblock", "label": "视频去色块", "type": "bool", "default": False},
                    {"name": "shake", "label": "视频去抖动", "type": "bool", "default": False},
                    {"name": "video_sample_frame_number", "label": "去黑边采样帧数", "type": "int", "default": 500, "min": 100, "max": 2000},
                    {"name": "target_dir", "label": "目标目录", "type": "dir_optional"},
                    {"name": "queue_dir", "label": "待处理队列目录", "type": "dir_optional"},
                    {"name": "rename_output", "label": "结果加时间戳", "type": "bool", "default": True},
                ],
            },
        ],
    },
]


def 构建功能目录():
    return {
        "app": {
            "name": "视频系统后端服务",
            "version": "3.2.0",
            "architecture": "前后端分离 + 分层包结构",
        },
        "official_files": 正式文件清单,
        "legacy_scripts": 旧脚本清单,
        "categories": 动作目录,
    }


from copy import deepcopy

from video_app.core.utils import query_environment_status
from video_system_settings import load_settings


def load_catalog():
    payload = deepcopy(构建功能目录())
    settings = load_settings()
    payload["environment"] = query_environment_status()
    app = payload.setdefault("app", {})
    app["name"] = "video_system_backend"
    app["version"] = "4.1.0"
    app["architecture"] = "frontend + backend + action modules"
    payload["official_files"] = [
        {"file": "start_backend.py", "role": "Startup", "summary": "Backend startup entry."},
        {"file": "start_frontend.py", "role": "Startup", "summary": "Frontend startup entry."},
        {"file": "video_system_gui.py", "role": "Launcher", "summary": "Auto-start launcher for the frontend and backend."},
        {"file": "video_system/backend/server.py", "role": "Backend server", "summary": "HTTP endpoints and request handling."},
        {"file": "video_system/backend/storage.py", "role": "Storage", "summary": "MySQL-backed preferences and run logs."},
        {"file": "video_system/backend/catalog.py", "role": "Catalog", "summary": "Action metadata and UI schema."},
        {"file": "video_system/actions/dispatcher.py", "role": "Dispatcher", "summary": "Action routing."},
        {"file": "video_system/frontend/window.py", "role": "Frontend window", "summary": "Main desktop window."},
        {"file": "video_system_settings.py", "role": "Config", "summary": "Project-wide settings and runtime defaults."},
    ]
    payload["legacy_scripts"] = []
    for category in payload.get("categories", []):
        if category.get("id") != "automation":
            continue
        for action in category.get("actions", []):
            if action.get("id") != "videofusion_merge":
                continue
            for field in action.get("fields", []):
                name = field.get("name")
                if name == "source_root":
                    field["default"] = str(settings["videofusion"]["source_dir"])
                elif name == "runtime_root":
                    field["default"] = str(settings["videofusion"]["runtime_dir"])
                elif name == "temp_dir":
                    field["default"] = str(settings["videofusion"]["temp_dir"])
                elif name == "output_dir":
                    field["default"] = str(settings["videofusion"]["output_dir"])
                elif name == "ffmpeg_file":
                    field["default"] = str(settings["videofusion"]["ffmpeg_file"])
    return payload
