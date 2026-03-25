import atexit
import json
import os
import socket
import subprocess
import sys
import time
import urllib.request
import uuid
from pathlib import Path

from video_system_settings import backend_base_url, load_settings


PROJECT_ROOT = Path(__file__).resolve().parent
_backend_process = None


def _default_backend_host():
    return load_settings()["backend"]["host"]


def _default_backend_port():
    return int(os.getenv("VIDEO_SYSTEM_BACKEND_PORT", load_settings()["backend"]["port"]))


def _build_backend_url(port=None):
    return backend_base_url(port or _default_backend_port())


def _health_url(port=None):
    return f"{_build_backend_url(port)}/health"


def _fetch_health_payload(port=None):
    try:
        with urllib.request.urlopen(_health_url(port), timeout=1.5) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception:
        return None


def _port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.2)
        return sock.connect_ex((_default_backend_host(), int(port))) == 0


def _find_free_port(start_port):
    port = int(start_port)
    while _port_in_use(port):
        port += 1
    return port


def _stop_backend():
    global _backend_process
    if _backend_process is None:
        return
    if _backend_process.poll() is None:
        _backend_process.terminate()
        try:
            _backend_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            _backend_process.kill()
            _backend_process.wait(timeout=5)
    _backend_process = None


def _start_backend_if_needed():
    global _backend_process

    expected_root = str(PROJECT_ROOT)
    preferred_port = _default_backend_port()
    current_payload = _fetch_health_payload(preferred_port)
    if current_payload and current_payload.get("success") and current_payload.get("project_root") == expected_root:
        os.environ["VIDEO_SYSTEM_BACKEND_URL"] = _build_backend_url(preferred_port)
        os.environ["VIDEO_SYSTEM_BACKEND_PORT"] = str(preferred_port)
        return

    chosen_port = preferred_port
    if current_payload and current_payload.get("success"):
        chosen_port = _find_free_port(preferred_port + 1)
    elif _port_in_use(preferred_port):
        chosen_port = _find_free_port(preferred_port + 1)

    backend_script = PROJECT_ROOT / "start_backend.py"
    instance_token = f"launcher-{os.getpid()}-{uuid.uuid4().hex[:8]}"
    backend_url = _build_backend_url(chosen_port)
    launch_env = os.environ.copy()
    launch_env["VIDEO_SYSTEM_PROJECT_ROOT"] = expected_root
    launch_env["VIDEO_SYSTEM_BACKEND_HOST"] = _default_backend_host()
    launch_env["VIDEO_SYSTEM_BACKEND_PORT"] = str(chosen_port)
    launch_env["VIDEO_SYSTEM_BACKEND_URL"] = backend_url
    launch_env["VIDEO_SYSTEM_INSTANCE_TOKEN"] = instance_token
    os.environ.update(launch_env)

    _backend_process = subprocess.Popen(
        [sys.executable, str(backend_script)],
        cwd=str(PROJECT_ROOT),
        env=launch_env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    atexit.register(_stop_backend)

    deadline = time.time() + 20
    while time.time() < deadline:
        payload = _fetch_health_payload(chosen_port)
        if payload and payload.get("success") and payload.get("instance_token") == instance_token:
            return
        if _backend_process.poll() is not None:
            raise RuntimeError("Backend startup failed. Run start_backend.py directly to inspect the error.")
        time.sleep(0.5)

    raise RuntimeError(f"Backend startup timed out. Check whether port {chosen_port} is already in use.")


def main():
    _start_backend_if_needed()
    from video_app.frontend.app import main as frontend_main

    frontend_main()


if __name__ == "__main__":
    main()
