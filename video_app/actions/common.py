from video_app.backend.catalog import load_catalog as build_catalog
from video_app.core.utils import query_environment_status


def success_response(message, logs="", data=None):
    return {"success": True, "message": message, "logs": logs, "data": data or {}}


def failure_response(message, logs="", data=None):
    return {"success": False, "message": message, "logs": logs, "data": data or {}}


def load_catalog():
    payload = build_catalog()
    payload["environment"] = query_environment_status()
    return payload


def report_progress(progress, percent, stage, detail=""):
    if not callable(progress):
        return
    try:
        progress(max(0, min(100, int(percent))), str(stage or ""), str(detail or ""))
    except Exception:
        return


def scale_progress(index, total, start=0, end=100):
    total = max(int(total or 0), 0)
    if total <= 0:
        return int(end)
    ratio = max(0.0, min(1.0, float(index) / float(total)))
    return int(start + (end - start) * ratio)


返回成功 = success_response
返回失败 = failure_response
读取功能目录 = load_catalog
上报进度 = report_progress
缩放进度 = scale_progress
