import argparse
import json
import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from video_app.actions.dispatcher import dispatch_action
from video_app.backend.catalog import load_catalog
from video_app.backend.storage import get_storage
from video_app.backend.tasks import task_manager
from video_app.core.utils import query_environment_status
from video_system_settings import load_settings


PROJECT_ROOT = str(Path(__file__).resolve().parents[2])
PATH_FIELD_TYPES = {
    "dir": "dir",
    "dir_optional": "dir",
    "file": "file",
    "file_optional": "file",
    "save_file": "save_file",
}


def find_action_metadata(action_id):
    catalog = load_catalog()
    for category in catalog.get("categories", []):
        for action in category.get("actions", []):
            if action.get("id") == action_id:
                return category, action
    return None, None


def append_storage_warning(result, warning_text):
    if not warning_text:
        return result
    result = dict(result or {})
    result["logs"] = "\n".join(part for part in (result.get("logs", ""), f"[storage] {warning_text}") if part)
    data = dict(result.get("data", {}) or {})
    data["storage_warning"] = warning_text
    result["data"] = data
    return result


def extract_path_history_entries(action_meta, params):
    entries = []
    if not action_meta:
        return entries
    for field in action_meta.get("fields", []):
        path_kind = PATH_FIELD_TYPES.get(field.get("type"))
        if not path_kind:
            continue
        raw_value = str((params or {}).get(field.get("name"), "") or "").strip()
        if not raw_value:
            continue
        entries.append({"path_kind": path_kind, "path_value": raw_value})
        parent = str(Path(raw_value).parent).strip()
        if path_kind in {"file", "save_file"} and parent not in {"", "."}:
            entries.append({"path_kind": "dir", "path_value": parent})
    return entries


def execute_background_task(task_id, action_id, action_title, action_meta, params, storage_warning=""):
    def progress_callback(percent, stage, detail=""):
        task_manager.update_task(
            task_id,
            status="running",
            progress=min(int(percent), 99),
            message=stage or "执行中",
            detail=detail or "",
        )

    task_manager.update_task(task_id, status="running", progress=1, message="任务已启动", detail="正在准备执行。")
    result = dispatch_action(action_id, params, progress=progress_callback)
    if storage_warning:
        result = append_storage_warning(result, storage_warning)
    try:
        get_storage().save_run_log(action_id, action_title, params, result)
    except Exception as exc:
        result = append_storage_warning(result, f"MySQL run log persistence failed: {exc}")

    current_task = task_manager.get_task(task_id) or {}
    final_progress = 100 if result.get("success") else max(int(current_task.get("progress", 0) or 0), 1)
    task_manager.update_task(
        task_id,
        status="success" if result.get("success") else "failed",
        progress=final_progress,
        message=result.get("message") or ("执行成功" if result.get("success") else "执行失败"),
        detail=result.get("logs", "")[:2000],
        result=result,
    )


class BackendRequestHandler(BaseHTTPRequestHandler):
    server_version = "VideoSystemBackend/4.1"

    def do_GET(self):
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)

        if parsed.path == "/health":
            return self._send_json(
                200,
                {
                    "success": True,
                    "service": "video_system_backend",
                    "environment": query_environment_status(),
                    "project_root": os.getenv("VIDEO_SYSTEM_PROJECT_ROOT", PROJECT_ROOT),
                    "instance_token": os.getenv("VIDEO_SYSTEM_INSTANCE_TOKEN", ""),
                    "backend_port": getattr(self.server, "server_port", None),
                    "backend_pid": os.getpid(),
                },
            )

        if parsed.path == "/catalog":
            return self._send_json(200, {"success": True, "catalog": load_catalog()})

        if parsed.path == "/preferences":
            action_id = (query.get("action_id") or [""])[0].strip()
            if not action_id:
                return self._send_json(400, {"success": False, "message": "missing action_id"})
            try:
                params = get_storage().load_preferences(action_id)
                return self._send_json(200, {"success": True, "data": {"action_id": action_id, "params": params}})
            except Exception as exc:
                return self._send_json(503, {"success": False, "message": f"MySQL unavailable: {exc}"})

        if parsed.path == "/history":
            action_id = (query.get("action_id") or [""])[0].strip() or None
            limit = (query.get("limit") or ["20"])[0]
            try:
                items = get_storage().recent_logs(action_id=action_id, limit=limit)
                return self._send_json(200, {"success": True, "data": {"items": items}})
            except Exception as exc:
                return self._send_json(503, {"success": False, "message": f"MySQL unavailable: {exc}"})

        if parsed.path == "/path-history":
            path_kind = (query.get("kind") or [""])[0].strip() or None
            limit = (query.get("limit") or ["30"])[0]
            try:
                items = get_storage().recent_path_history(path_kind=path_kind, limit=limit)
                return self._send_json(200, {"success": True, "data": {"items": items}})
            except Exception as exc:
                return self._send_json(503, {"success": False, "message": f"MySQL unavailable: {exc}"})

        if parsed.path.startswith("/tasks/"):
            task_id = parsed.path.split("/tasks/", 1)[-1].strip()
            task = task_manager.get_task(task_id)
            if task is None:
                return self._send_json(404, {"success": False, "message": "task not found"})
            return self._send_json(200, {"success": True, "data": task})

        return self._send_json(404, {"success": False, "message": "endpoint not found"})

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(content_length) if content_length > 0 else b"{}"
        try:
            payload = json.loads(raw_body.decode("utf-8"))
        except json.JSONDecodeError:
            return self._send_json(400, {"success": False, "message": "request body must be valid JSON"})

        if self.path == "/preferences":
            action_id = str(payload.get("action_id") or "").strip()
            params = payload.get("params", {})
            if not action_id:
                return self._send_json(400, {"success": False, "message": "missing action_id"})
            try:
                get_storage().save_preferences(action_id, params)
                return self._send_json(200, {"success": True, "message": "preferences saved"})
            except Exception as exc:
                return self._send_json(503, {"success": False, "message": f"MySQL unavailable: {exc}"})

        if self.path == "/path-history":
            items = payload.get("items", [])
            try:
                get_storage().save_path_history(items)
                return self._send_json(200, {"success": True, "message": "path history saved"})
            except Exception as exc:
                return self._send_json(503, {"success": False, "message": f"MySQL unavailable: {exc}"})

        if self.path == "/path-history/delete":
            path_kind = str(payload.get("path_kind") or "").strip()
            path_value = str(payload.get("path_value") or "").strip()
            if not path_kind or not path_value:
                return self._send_json(400, {"success": False, "message": "missing path_kind or path_value"})
            try:
                deleted = get_storage().delete_path_history(path_kind, path_value)
                return self._send_json(200, {"success": True, "message": "path history deleted", "data": {"deleted": deleted}})
            except Exception as exc:
                return self._send_json(503, {"success": False, "message": f"MySQL unavailable: {exc}"})

        if self.path == "/path-history/clear":
            path_kind = str(payload.get("path_kind") or "").strip()
            if not path_kind:
                return self._send_json(400, {"success": False, "message": "missing path_kind"})
            try:
                deleted = get_storage().clear_path_history(path_kind)
                return self._send_json(200, {"success": True, "message": "path history cleared", "data": {"deleted": deleted}})
            except Exception as exc:
                return self._send_json(503, {"success": False, "message": f"MySQL unavailable: {exc}"})

        if self.path != "/run":
            return self._send_json(404, {"success": False, "message": "endpoint not found"})

        action_id = payload.get("action_id")
        params = payload.get("params", {})
        if not action_id:
            return self._send_json(400, {"success": False, "message": "missing action_id"})
        _, action_meta = find_action_metadata(action_id)
        action_title = action_meta.get("title", action_id) if action_meta else str(action_id or "")
        storage_warning = ""
        try:
            store = get_storage()
            store.save_preferences(action_id, params)
            store.save_path_history(extract_path_history_entries(action_meta, params))
        except Exception as exc:
            storage_warning = f"MySQL persistence failed: {exc}"

        task_id = task_manager.create_task(action_id, action_title)
        threading.Thread(
            target=execute_background_task,
            args=(task_id, action_id, action_title, action_meta, params, storage_warning),
            daemon=True,
        ).start()
        return self._send_json(
            200,
            {
                "success": True,
                "message": "task started",
                "data": task_manager.get_task(task_id),
            },
        )

    def log_message(self, format_string, *args):
        return

    def _send_json(self, status_code, payload):
        body = json.dumps(payload, ensure_ascii=False, default=str).encode("utf-8")
        try:
            self.send_response(status_code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionAbortedError, ConnectionResetError, OSError):
            return


def run_backend_server(host=None, port=None):
    settings = load_settings()
    host = host or settings["backend"]["host"]
    port = int(port or settings["backend"]["port"])
    while True:
        try:
            server = ThreadingHTTPServer((host, port), BackendRequestHandler)
            break
        except OSError:
            port += 1
    print(f"video_system backend started: http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("video_system backend stopped")
    finally:
        server.server_close()


def main():
    settings = load_settings()
    parser = argparse.ArgumentParser(description="video_system backend service")
    parser.add_argument("--host", default=settings["backend"]["host"])
    parser.add_argument("--port", type=int, default=int(settings["backend"]["port"]))
    args = parser.parse_args()
    run_backend_server(args.host, args.port)


if __name__ == "__main__":
    main()
