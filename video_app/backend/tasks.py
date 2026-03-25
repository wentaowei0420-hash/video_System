import threading
import uuid
from datetime import datetime


class TaskManager:
    def __init__(self):
        self._lock = threading.RLock()
        self._tasks = {}

    def create_task(self, action_id, action_title):
        task_id = uuid.uuid4().hex
        task = {
            "task_id": task_id,
            "action_id": action_id,
            "action_title": action_title,
            "status": "queued",
            "progress": 0,
            "message": "任务已创建",
            "detail": "",
            "result": None,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "finished_at": None,
        }
        with self._lock:
            self._tasks[task_id] = task
        return task_id

    def update_task(self, task_id, *, status=None, progress=None, message=None, detail=None, result=None):
        with self._lock:
            task = self._tasks.get(task_id)
            if task is None:
                return None
            if status is not None:
                task["status"] = status
            if progress is not None:
                task["progress"] = max(0, min(100, int(progress)))
            if message is not None:
                task["message"] = str(message)
            if detail is not None:
                task["detail"] = str(detail)
            if result is not None:
                task["result"] = result
            task["updated_at"] = datetime.now()
            if task["status"] in {"success", "failed"}:
                task["finished_at"] = datetime.now()
        return self.get_task(task_id)

    def get_task(self, task_id):
        with self._lock:
            task = self._tasks.get(task_id)
            if task is None:
                return None
            return dict(task)


task_manager = TaskManager()
