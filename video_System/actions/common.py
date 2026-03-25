from video_system.backend.catalog import load_catalog as build_catalog
from video_system.core.utils import query_environment_status


def success_response(message, logs="", data=None):
    return {"success": True, "message": message, "logs": logs, "data": data or {}}


def failure_response(message, logs="", data=None):
    return {"success": False, "message": message, "logs": logs, "data": data or {}}


def load_catalog():
    payload = build_catalog()
    payload["environment"] = query_environment_status()
    return payload


返回成功 = success_response
返回失败 = failure_response
读取功能目录 = load_catalog
