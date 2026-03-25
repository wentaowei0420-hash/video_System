import json
import urllib.error
import urllib.request

from PyQt5.QtCore import QObject, pyqtSignal


class ApiWorker(QObject):
    finished = pyqtSignal(dict)
    failed = pyqtSignal(str)

    def __init__(self, method, url, payload=None):
        super().__init__()
        self.method = method
        self.url = url
        self.payload = payload

    def run(self):
        try:
            body = None
            headers = {}
            if self.payload is not None:
                body = json.dumps(self.payload, ensure_ascii=False).encode("utf-8")
                headers["Content-Type"] = "application/json; charset=utf-8"
            request = urllib.request.Request(self.url, data=body, method=self.method, headers=headers)
            with urllib.request.urlopen(request, timeout=3600) as response:
                payload = json.loads(response.read().decode("utf-8"))
            self.finished.emit(payload)
        except urllib.error.HTTPError as exc:
            try:
                payload = json.loads(exc.read().decode("utf-8"))
                self.finished.emit(payload)
            except Exception:
                self.failed.emit(f"HTTP {exc.code}: {exc.reason}")
        except Exception as exc:
            self.failed.emit(str(exc))
