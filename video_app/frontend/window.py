import json
import urllib.parse
import urllib.request
from datetime import datetime

from PyQt5.QtCore import QSize, QThread, QTimer, Qt
from PyQt5.QtWidgets import (
    QComboBox,
    QDialog,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QStatusBar,
    QStyle,
    QVBoxLayout,
    QWidget,
)

from video_app.frontend.api import ApiWorker
from video_app.frontend.styles import APP_STYLESHEET, APP_TITLE, DEFAULT_BASE_URL
from video_app.frontend.widgets import 信息卡片, 动作卡片, 功能入口卡片


class 功能窗口(QDialog):
    def __init__(self, category_title, action_meta, submit_handler, parent=None):
        super().__init__(parent)
        self.action_meta = action_meta
        self.submit_handler = submit_handler

        self.setWindowTitle(f"{action_meta.get('title', '未命名功能')} - {category_title}")
        self.resize(980, 760)
        self.setMinimumSize(920, 680)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        intro = QFrame()
        intro.setObjectName("dialogHeader")
        intro_layout = QVBoxLayout(intro)
        intro_layout.setContentsMargins(22, 20, 22, 18)
        intro_layout.setSpacing(8)

        title_row = QHBoxLayout()
        title_row.setContentsMargins(0, 0, 0, 0)
        title_row.setSpacing(10)
        title_icon = QLabel()
        title_icon.setObjectName("sectionIconBadge")
        title_icon.setPixmap(self.style().standardIcon(QStyle.SP_ComputerIcon).pixmap(16, 16))
        title_icon.setAlignment(Qt.AlignCenter)
        title = QLabel(action_meta.get("title", "未命名功能"))
        title.setObjectName("sectionTitle")
        title_row.addWidget(title_icon, 0, Qt.AlignVCenter)
        title_row.addWidget(title, 0, Qt.AlignVCenter)
        title_row.addStretch(1)
        desc = QLabel(action_meta.get("description", ""))
        desc.setWordWrap(True)
        desc.setObjectName("mutedLabel")
        meta_row = QHBoxLayout()
        module_badge = QLabel(category_title)
        module_badge.setObjectName("softBadge")
        action_badge = QLabel(action_meta.get("id", "-"))
        action_badge.setObjectName("codeBadge")
        meta_row.addWidget(module_badge, alignment=Qt.AlignLeft)
        meta_row.addWidget(action_badge, alignment=Qt.AlignLeft)
        meta_row.addStretch(1)
        intro_layout.addLayout(title_row)
        intro_layout.addWidget(desc)
        intro_layout.addLayout(meta_row)
        layout.addWidget(intro)

        self.action_card = 动作卡片(action_meta, show_description=False)
        self.action_card.submitted.connect(submit_handler)

        scroll_container = QWidget()
        scroll_layout = QVBoxLayout(scroll_container)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.addWidget(self.action_card)
        scroll_layout.addStretch(1)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(scroll_container)
        layout.addWidget(scroll, 1)


class 主窗口(QMainWindow):
    def __init__(self, auto_fetch=True):
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.resize(1580, 980)

        self.current_thread = None
        self.current_worker = None
        self.pending_label = ""
        self.catalog_data = None
        self.page_lookup = {}
        self.module_buttons = {}
        self.action_registry = {}
        self.action_windows = {}
        self.current_page_key = "overview"
        self.environment_status = {}
        self.history_items = []
        self.monitor_grid_layout = None
        self.monitor_summary_label = None
        self.monitor_update_label = None
        self.monitor_total_value_label = None
        self.monitor_ok_value_label = None
        self.monitor_issue_value_label = None
        self.history_list_layout = None
        self.history_summary_label = None
        self.history_update_label = None
        self.history_filter_combo = None
        self.pending_request_path = ""
        self.pending_action_window = None

        self.monitor_refresh_timer = QTimer(self)
        self.monitor_refresh_timer.setInterval(15000)
        self.monitor_refresh_timer.timeout.connect(self._refresh_monitor_if_visible)
        self.monitor_refresh_timer.start()

        self._build_ui()
        self._apply_styles()
        if auto_fetch:
            self.fetch_catalog()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(14)

        root.addWidget(self._build_header())

        content_panel = QFrame()
        content_panel.setObjectName("contentPanel")
        content_layout = QVBoxLayout(content_panel)
        content_layout.setContentsMargins(14, 14, 14, 14)
        content_layout.setSpacing(14)

        self.module_nav_frame = QFrame()
        self.module_nav_frame.setObjectName("moduleNavFrame")
        self.module_nav_layout = QHBoxLayout(self.module_nav_frame)
        self.module_nav_layout.setContentsMargins(10, 10, 10, 10)
        self.module_nav_layout.setSpacing(10)
        self.module_nav_layout.addStretch(1)

        self.page_stack = QStackedWidget()
        content_layout.addWidget(self.module_nav_frame)
        content_layout.addWidget(self.page_stack, 1)
        root.addWidget(content_panel, 1)

        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        self.status_message = QLabel("未连接后端")
        status_bar.addPermanentWidget(self.status_message)

    def _build_header(self):
        frame = QFrame()
        frame.setObjectName("headerFrame")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(22, 20, 22, 18)
        layout.setSpacing(14)

        top_row = QHBoxLayout()
        title_block = QVBoxLayout()
        title_row = QHBoxLayout()
        title_row.setContentsMargins(0, 0, 0, 0)
        title_row.setSpacing(10)
        title_icon = QLabel()
        title_icon.setObjectName("heroIconBadge")
        title_icon.setPixmap(self.style().standardIcon(QStyle.SP_DesktopIcon).pixmap(18, 18))
        title = QLabel(APP_TITLE)
        title.setObjectName("headerTitle")
        subtitle = QLabel("视频处理控制台")
        subtitle.setObjectName("headerSubtitle")
        subtitle.setWordWrap(True)
        title_row.addWidget(title_icon, 0, Qt.AlignVCenter)
        title_row.addWidget(title, 0, Qt.AlignVCenter)
        title_row.addStretch(1)
        title_block.addLayout(title_row)
        title_block.addWidget(subtitle)
        top_row.addLayout(title_block, 1)

        self.health_badge = QLabel("未连接")
        self.health_badge.setObjectName("badgeOffline")
        top_row.addWidget(self.health_badge, alignment=Qt.AlignTop)
        layout.addLayout(top_row)

        controls = QHBoxLayout()
        controls.setSpacing(10)
        address_label = QLabel("后端地址")
        address_label.setObjectName("toolbarLabel")
        controls.addWidget(address_label)
        self.base_url_edit = QLineEdit(DEFAULT_BASE_URL)
        self.base_url_edit.setMinimumWidth(360)
        self.base_url_edit.setFixedHeight(42)
        refresh_button = QPushButton("加载目录")
        refresh_button.setObjectName("primaryButton")
        refresh_button.setFixedHeight(42)
        self._set_button_icon(refresh_button, QStyle.SP_BrowserReload)
        refresh_button.clicked.connect(self.fetch_catalog)
        health_button = QPushButton("检查连接")
        health_button.setFixedHeight(42)
        self._set_button_icon(health_button, QStyle.SP_DialogApplyButton)
        health_button.clicked.connect(self.check_health)
        controls.addWidget(self.base_url_edit)
        controls.addWidget(refresh_button)
        controls.addWidget(health_button)
        controls.addStretch(1)
        layout.addLayout(controls)

        return frame

    def _register_page(self, page_key, widget):
        page_index = self.page_stack.addWidget(widget)
        self.page_lookup[page_key] = page_index

    def _clear_module_buttons(self):
        self.module_buttons = {}
        while self.module_nav_layout.count():
            item = self.module_nav_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self.module_nav_layout.addStretch(1)

    def _set_active_module_button(self, page_key):
        for key, button in self.module_buttons.items():
            button.setChecked(key == page_key)

    def _add_sidebar_page(self, page_key, title, widget):
        button = QPushButton(title)
        button.setObjectName("moduleButton")
        button.setCheckable(True)
        button.setMinimumHeight(42)
        self._set_button_icon(button, self._module_icon_enum(page_key, title), size=14)
        button.clicked.connect(lambda _, key=page_key: self.navigate_to_page(key))
        self.module_buttons[page_key] = button
        self.module_nav_layout.insertWidget(self.module_nav_layout.count() - 1, button)
        self._register_page(page_key, widget)

    def navigate_to_page(self, page_key, sidebar_key=None):
        page_index = self.page_lookup.get(page_key)
        if page_index is None:
            return

        self.current_page_key = page_key
        self.page_stack.setCurrentIndex(page_index)
        target_key = sidebar_key if sidebar_key is not None else page_key
        self._set_active_module_button(target_key)
        if page_key == "monitor":
            self.refresh_monitor_status(silent=True)
        elif page_key == "history":
            self.refresh_history(silent=True)

    def open_action_window(self, action_key):
        record = self.action_registry.get(action_key)
        if record is None:
            return

        existing = self.action_windows.get(action_key)
        if existing is not None:
            existing.show()
            existing.raise_()
            existing.activateWindow()
            return

        window = 功能窗口(record["category_title"], record["action"], self.run_action, self)
        self._install_action_progress(window)
        window.action_card.submitted.disconnect()
        window.action_card.submitted.connect(
            lambda action_id, params, title, current_window=window: self._submit_action_from_window(
                current_window, action_id, params, title
            )
        )
        window.action_card.pathRecorded.connect(self.save_path_history_items)
        window.action_card.pathRefreshRequested.connect(
            lambda field_name, path_kind, current_window=window: self.refresh_action_window_paths(current_window)
        )
        window.action_card.pathDeleteRequested.connect(
            lambda field_name, path_kind, path_value, current_window=window: self.delete_path_history_item(
                current_window,
                field_name,
                path_kind,
                path_value,
            )
        )
        window.action_card.pathClearRequested.connect(
            lambda field_name, path_kind, current_window=window: self.clear_path_history_items(
                current_window,
                field_name,
                path_kind,
            )
        )
        path_history = self.fetch_path_history()
        if path_history:
            window.action_card.apply_path_history(path_history)
        saved_params = self.fetch_action_preferences(record["action"].get("id"))
        if saved_params:
            window.action_card.apply_params(saved_params)
        window.setAttribute(Qt.WA_DeleteOnClose, True)
        window.destroyed.connect(lambda *_: self.action_windows.pop(action_key, None))
        self.action_windows[action_key] = window
        window.show()

    def _install_action_progress(self, window):
        panel = QFrame()
        panel.setObjectName("taskProgressPanel")
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(16, 14, 16, 14)
        panel_layout.setSpacing(10)

        header_row = QHBoxLayout()
        title_label = QLabel("任务进度")
        title_label.setObjectName("fieldLabel")
        status_label = QLabel("待执行")
        status_label.setObjectName("softBadge")
        header_row.addWidget(title_label)
        header_row.addStretch(1)
        header_row.addWidget(status_label)

        battery_row = QHBoxLayout()
        battery_row.setSpacing(10)
        progress_bar = QProgressBar()
        progress_bar.setRange(0, 100)
        progress_bar.setValue(0)
        progress_bar.setTextVisible(False)
        progress_bar.setFixedHeight(18)
        progress_bar.setFormat("%p%")
        progress_cap = QFrame()
        progress_cap.setFixedSize(10, 18)
        progress_cap.setObjectName("taskProgressCap")
        percent_label = QLabel("0%")
        percent_label.setObjectName("monitorMeta")
        battery_row.addWidget(progress_bar, 1)
        battery_row.addWidget(progress_cap)
        battery_row.addWidget(percent_label)

        hint_label = QLabel("点击执行任务后，将自动更新当前任务状态。")
        hint_label.setObjectName("mutedLabel")

        panel_layout.addLayout(header_row)
        panel_layout.addLayout(battery_row)
        panel_layout.addWidget(hint_label)

        window.layout().insertWidget(1, panel)

        window.progress_panel = panel
        window.progress_bar = progress_bar
        window.progress_cap = progress_cap
        window.progress_status_label = status_label
        window.progress_percent_label = percent_label
        window.progress_hint_label = hint_label
        window.progress_value = 0
        window.current_task_id = ""
        window.task_poll_timer = QTimer(window)
        window.task_poll_timer.setInterval(900)
        window.task_poll_timer.timeout.connect(lambda current_window=window: self._poll_task_status(current_window))
        window.destroyed.connect(lambda *_, current_window=window: self._clear_pending_action_window(current_window))
        self._set_action_progress_state(window, "idle", 0, "待执行", "点击执行任务后，将自动更新当前任务状态。")

    def _clear_pending_action_window(self, window):
        if self.pending_action_window is window:
            self.pending_action_window = None
        if hasattr(window, "task_poll_timer") and window.task_poll_timer is not None:
            window.task_poll_timer.stop()

    def _progress_stylesheet(self, state):
        chunk_color = "#94a3b8"
        border_color = "#d5deea"
        background_color = "#eef2f7"
        cap_color = "#cbd5e1"
        if state == "running":
            chunk_color = "#22c55e"
            border_color = "#86efac"
            background_color = "#effff5"
            cap_color = "#16a34a"
        elif state == "success":
            chunk_color = "#16a34a"
            border_color = "#86efac"
            background_color = "#f0fdf4"
            cap_color = "#15803d"
        elif state == "failed":
            chunk_color = "#ef4444"
            border_color = "#fca5a5"
            background_color = "#fef2f2"
            cap_color = "#dc2626"
        return (
            "QProgressBar {"
            f"background: {background_color};"
            f"border: 1px solid {border_color};"
            "border-radius: 9px;"
            "padding: 1px;"
            "}"
            "QProgressBar::chunk {"
            f"background: {chunk_color};"
            "border-radius: 7px;"
            "margin: 1px;"
            "}"
        ), (
            f"background: {cap_color};"
            f"border: 1px solid {border_color};"
            "border-radius: 4px;"
        )

    def _set_action_progress_state(self, window, state, value, status_text, hint_text):
        value = max(0, min(100, int(value)))
        progress_stylesheet, cap_stylesheet = self._progress_stylesheet(state)
        window.progress_value = value
        window.progress_bar.setValue(value)
        window.progress_bar.setStyleSheet(progress_stylesheet)
        window.progress_cap.setStyleSheet(cap_stylesheet)
        window.progress_status_label.setText(status_text)
        window.progress_status_label.setObjectName("codeBadge" if state == "failed" else "softBadge")
        window.progress_status_label.style().unpolish(window.progress_status_label)
        window.progress_status_label.style().polish(window.progress_status_label)
        window.progress_percent_label.setText(f"{value}%")
        window.progress_hint_label.setText(hint_text)

    def _submit_action_from_window(self, window, action_id, params, title):
        started = self.run_action(action_id, params, title, source_window=window)
        if started:
            window.action_card.setEnabled(False)
            window.action_card.set_submitting(True)
            window.current_task_id = ""
            self._set_action_progress_state(window, "running", 2, "已提交", f"任务已提交：{title}")
        else:
            self._set_action_progress_state(window, "failed", 0, "未开始", "当前已有任务在执行，请稍后再试。")

    def _finish_action_progress(self, success, message="", window=None, value=100):
        window = window or self.pending_action_window
        if window is None:
            return
        if hasattr(window, "task_poll_timer") and window.task_poll_timer is not None:
            window.task_poll_timer.stop()
        if hasattr(window, "action_card") and window.action_card is not None:
            window.action_card.setEnabled(True)
            window.action_card.set_submitting(False)
        status_text = "执行完成" if success else "执行失败"
        hint_text = message or ("任务已完成。" if success else "任务执行失败。")
        self._set_action_progress_state(window, "success" if success else "failed", value, status_text, hint_text)
        if success:
            window.current_task_id = ""

    def _fetch_json_direct(self, path, timeout=3):
        base_url = self.base_url_edit.text().strip().rstrip("/")
        if not base_url:
            return {}
        url = base_url + path
        with urllib.request.urlopen(url, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))

    def _start_task_polling(self, window, task_payload):
        task_id = str((task_payload or {}).get("task_id") or "")
        if not task_id:
            self._finish_action_progress(False, "后端未返回 task_id。", window=window, value=0)
            return
        window.current_task_id = task_id
        self._apply_task_status(window, task_payload)
        if hasattr(window, "task_poll_timer") and window.task_poll_timer is not None:
            window.task_poll_timer.start()
        self._poll_task_status(window)

    def _apply_task_status(self, window, task_payload):
        status = str((task_payload or {}).get("status") or "queued").strip().lower()
        progress = int((task_payload or {}).get("progress") or 0)
        message = str((task_payload or {}).get("message") or "").strip()
        detail = str((task_payload or {}).get("detail") or "").strip()
        hint_text = detail or message or "任务正在运行。"
        if status in {"queued", "running"}:
            status_text = "排队中" if status == "queued" else "执行中"
            self._set_action_progress_state(window, "running", progress, status_text, hint_text)
            return
        if status == "success":
            result = (task_payload or {}).get("result") or {}
            self._finish_action_progress(True, result.get("message") or hint_text, window=window, value=progress or 100)
            return
        if status == "failed":
            result = (task_payload or {}).get("result") or {}
            failure_message = result.get("message") or hint_text or "任务执行失败。"
            self._finish_action_progress(False, failure_message, window=window, value=progress)
            window.current_task_id = ""
            QMessageBox.warning(window, "执行失败", failure_message)
            return
        self._set_action_progress_state(window, "running", progress, "执行中", hint_text)

    def _poll_task_status(self, window):
        task_id = str(getattr(window, "current_task_id", "") or "").strip()
        if not task_id:
            return
        try:
            payload = self._fetch_json_direct(f"/tasks/{task_id}", timeout=2)
        except Exception:
            self._set_action_progress_state(
                window,
                "running",
                getattr(window, "progress_value", 0),
                "执行中",
                "状态刷新失败，正在重试。",
            )
            return
        if not payload.get("success"):
            self._finish_action_progress(False, payload.get("message", "任务状态查询失败"), window=window, value=getattr(window, "progress_value", 0))
            window.current_task_id = ""
            return
        self._apply_task_status(window, payload.get("data", {}))

    def append_log(self, text):
        return

    def fetch_action_preferences(self, action_id):
        base_url = self.base_url_edit.text().strip().rstrip("/")
        if not base_url or not action_id:
            return {}
        url = f"{base_url}/preferences?{urllib.parse.urlencode({'action_id': action_id})}"
        try:
            with urllib.request.urlopen(url, timeout=3) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except Exception:
            return {}
        if not payload.get("success"):
            return {}
        return payload.get("data", {}).get("params", {})

    def fetch_path_history(self, limit=40):
        base_url = self.base_url_edit.text().strip().rstrip("/")
        if not base_url:
            return []
        url = f"{base_url}/path-history?{urllib.parse.urlencode({'limit': limit})}"
        try:
            with urllib.request.urlopen(url, timeout=3) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except Exception:
            return []
        if not payload.get("success"):
            return []
        return payload.get("data", {}).get("items", [])

    def save_path_history_items(self, items):
        base_url = self.base_url_edit.text().strip().rstrip("/")
        if not base_url or not items:
            return
        body = json.dumps({"items": items}, ensure_ascii=False).encode("utf-8")
        request = urllib.request.Request(
            base_url + "/path-history",
            data=body,
            method="POST",
            headers={"Content-Type": "application/json; charset=utf-8"},
        )
        try:
            with urllib.request.urlopen(request, timeout=3):
                return
        except Exception:
            return

    def refresh_action_window_paths(self, window):
        if window is None or not hasattr(window, "action_card"):
            return
        path_history = self.fetch_path_history()
        window.action_card.apply_path_history(path_history)
        window.action_card.update()
        window.update()
        self.status_message.setText("路径历史已刷新")

    def delete_path_history_item(self, window, field_name, path_kind, path_value):
        base_url = self.base_url_edit.text().strip().rstrip("/")
        normalized_value = str(path_value or "").strip()
        normalized_kind = str(path_kind or "").strip()
        if not base_url or not normalized_value or not normalized_kind:
            return
        body = json.dumps(
            {"path_kind": normalized_kind, "path_value": normalized_value},
            ensure_ascii=False,
        ).encode("utf-8")
        request = urllib.request.Request(
            base_url + "/path-history/delete",
            data=body,
            method="POST",
            headers={"Content-Type": "application/json; charset=utf-8"},
        )
        try:
            with urllib.request.urlopen(request, timeout=3) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            QMessageBox.warning(window, "删除失败", str(exc))
            return
        if not payload.get("success"):
            QMessageBox.warning(window, "删除失败", payload.get("message", "无法删除历史路径"))
            return
        window.action_card.remove_path_history_value(field_name, normalized_value, clear_current=True)
        self.refresh_action_window_paths(window)
        self.status_message.setText("路径历史已删除")

    def clear_path_history_items(self, window, field_name, path_kind):
        base_url = self.base_url_edit.text().strip().rstrip("/")
        normalized_kind = str(path_kind or "").strip()
        if not base_url or not normalized_kind:
            return
        reply = QMessageBox.question(
            window,
            "清空历史路径",
            f"确定清空当前类型的全部历史路径吗？\n类型：{normalized_kind}",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return
        body = json.dumps({"path_kind": normalized_kind}, ensure_ascii=False).encode("utf-8")
        request = urllib.request.Request(
            base_url + "/path-history/clear",
            data=body,
            method="POST",
            headers={"Content-Type": "application/json; charset=utf-8"},
        )
        try:
            with urllib.request.urlopen(request, timeout=3) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            QMessageBox.warning(window, "清空失败", str(exc))
            return
        if not payload.get("success"):
            QMessageBox.warning(window, "清空失败", payload.get("message", "无法清空历史路径"))
            return
        window.action_card.clear_path_history(field_name)
        self.refresh_action_window_paths(window)
        self.status_message.setText("当前类型历史路径已清空")

    def request(self, method, path, payload=None, label="请求", quiet_if_busy=False, source_window=None):
        if self.current_thread is not None:
            if not quiet_if_busy:
                QMessageBox.warning(self, "任务进行中", "当前已有请求在执行，请稍后再试。")
            return False

        base_url = self.base_url_edit.text().strip().rstrip("/")
        if not base_url:
            if not quiet_if_busy:
                QMessageBox.warning(self, "地址错误", "请先填写后端地址。")
            return False

        self.pending_label = label
        self.pending_request_path = path
        self.pending_action_window = source_window
        self.status_message.setText(label)
        self.append_log(f"\n===== {label} =====")

        self.current_thread = QThread(self)
        self.current_worker = ApiWorker(method, base_url + path, payload)
        self.current_worker.moveToThread(self.current_thread)
        self.current_thread.started.connect(self.current_worker.run)
        self.current_worker.finished.connect(self.on_response)
        self.current_worker.failed.connect(self.on_error)
        self.current_worker.finished.connect(lambda *_: self.current_thread.quit())
        self.current_worker.failed.connect(lambda *_: self.current_thread.quit())
        self.current_thread.finished.connect(self.cleanup_request)
        self.current_thread.start()
        return True

    def cleanup_request(self):
        if self.current_worker is not None:
            self.current_worker.deleteLater()
        if self.current_thread is not None:
            self.current_thread.deleteLater()
        self.current_worker = None
        self.current_thread = None
        self.pending_label = ""
        self.pending_request_path = ""
        self.pending_action_window = None

    def closeEvent(self, event):
        if self.current_thread is not None:
            self.current_thread.quit()
            self.current_thread.wait(3000)
        super().closeEvent(event)

    def check_health(self):
        self.request("GET", "/health", label="检查后端连接")

    def refresh_monitor_status(self, silent=False):
        self.request("GET", "/health", label="刷新状态监控", quiet_if_busy=silent)

    def fetch_catalog(self):
        self.request("GET", "/catalog", label="加载功能目录")

    def _refresh_monitor_if_visible(self):
        if self.current_page_key == "monitor":
            self.refresh_monitor_status(silent=True)

    def refresh_history(self, silent=False):
        action_id = ""
        if self.history_filter_combo is not None:
            action_id = str(self.history_filter_combo.currentData() or "").strip()
        query = {"limit": 50}
        if action_id:
            query["action_id"] = action_id
        self.request("GET", "/history?" + urllib.parse.urlencode(query), label="刷新历史记录", quiet_if_busy=silent)

    def run_action(self, action_id, params, title, source_window=None):
        return self.request(
            "POST",
            "/run",
            payload={"action_id": action_id, "params": params},
            label=f"执行任务: {title}",
            source_window=source_window,
        )

    def on_error(self, message):
        if self.pending_request_path == "/run":
            self._finish_action_progress(False, message)
        self.health_badge.setText("连接失败")
        self.health_badge.setObjectName("badgeOffline")
        self.health_badge.style().unpolish(self.health_badge)
        self.health_badge.style().polish(self.health_badge)
        self.status_message.setText("后端连接失败")
        self.append_log(f"请求失败: {message}")
        if self.pending_label not in ("加载功能目录", "检查后端连接"):
            QMessageBox.critical(self, "请求失败", message)

    def on_response(self, payload):
        if "catalog" in payload:
            self.catalog_data = payload["catalog"]
            self.environment_status = payload["catalog"].get("environment", {})
            self.render_catalog(payload["catalog"])
            self.health_badge.setText("目录已同步")
            self.health_badge.setObjectName("badgeOnline")
            self.health_badge.style().unpolish(self.health_badge)
            self.health_badge.style().polish(self.health_badge)
            self.status_message.setText("已连接后端并同步目录")
            self.append_log("功能目录已更新")
            return

        if self.pending_request_path.startswith("/history"):
            items = payload.get("data", {}).get("items", []) if payload.get("success") else []
            self.history_items = items
            self.update_history_cards(items)
            self.health_badge.setText("后端在线")
            self.health_badge.setObjectName("badgeOnline")
            self.health_badge.style().unpolish(self.health_badge)
            self.health_badge.style().polish(self.health_badge)
            self.status_message.setText("历史记录已更新")
            if not payload.get("success"):
                QMessageBox.warning(self, "历史记录", payload.get("message", "无法加载历史记录"))
            return

        if self.pending_request_path == "/run":
            self.health_badge.setText("后端在线")
            self.health_badge.setObjectName("badgeOnline")
            self.health_badge.style().unpolish(self.health_badge)
            self.health_badge.style().polish(self.health_badge)
            if not payload.get("success"):
                message = payload.get("message", "任务启动失败")
                self.status_message.setText(message)
                self._finish_action_progress(False, message)
                QMessageBox.warning(self, "执行失败", message)
                return
            task_payload = payload.get("data", {}) or {}
            self.status_message.setText("任务已启动")
            self._start_task_polling(self.pending_action_window, task_payload)
            return

        if payload.get("service") == "video-backend" or "environment" in payload and payload.get("success") is True and "catalog" not in payload:
            self.health_badge.setText("后端在线")
            self.health_badge.setObjectName("badgeOnline")
            self.health_badge.style().unpolish(self.health_badge)
            self.health_badge.style().polish(self.health_badge)
            self.status_message.setText("后端健康检查通过")
            self.append_log("后端连接正常")
            env = payload.get("environment", {})
            if env:
                self.environment_status = env
                self.update_monitor_cards(env)
                self.append_log("环境状态: " + json.dumps(env, ensure_ascii=False))
            return

        success = bool(payload.get("success"))
        message = payload.get("message", "")
        logs = payload.get("logs", "")
        data = payload.get("data", {})

        self.health_badge.setText("后端在线")
        self.health_badge.setObjectName("badgeOnline")
        self.health_badge.style().unpolish(self.health_badge)
        self.health_badge.style().polish(self.health_badge)

        if logs:
            self.append_log(logs.strip())
        if data:
            self.append_log("返回数据: " + json.dumps(data, ensure_ascii=False))
        if message:
            self.append_log(message)
        self.status_message.setText(message or ("执行成功" if success else "执行失败"))
        self._finish_action_progress(success, message)

        if not success:
            QMessageBox.warning(self, "执行失败", message or "后端返回失败")

    def render_catalog(self, catalog):
        self.page_lookup = {}
        self._clear_module_buttons()
        self.action_registry = {}
        self.environment_status = catalog.get("environment", {})
        while self.page_stack.count():
            widget = self.page_stack.widget(0)
            self.page_stack.removeWidget(widget)
            widget.deleteLater()

        categories = catalog.get("categories", [])
        self._add_sidebar_page("overview", "系统总览", self.build_overview_page(catalog))
        self._add_sidebar_page("monitor", "状态监控", self.build_monitor_page(self.environment_status))
        self._add_sidebar_page("history", "历史记录", self.build_history_page())

        for category_index, category in enumerate(categories):
            category_key = f"category:{category_index}"
            self._add_sidebar_page(category_key, category.get("title", "未命名模块"), self.build_category_page(category, category_key))
            for action_index, action in enumerate(category.get("actions", [])):
                action_key = f"{category_key}:action:{action_index}"
                self.action_registry[action_key] = {
                    "category_title": category.get("title", "未命名模块"),
                    "action": action,
                }

        self.update_history_filter()
        self.navigate_to_page("overview")

    def build_overview_page(self, catalog):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(14)

        hero = QFrame()
        hero.setObjectName("heroPanel")
        hero_layout = QVBoxLayout(hero)
        hero_layout.setContentsMargins(22, 18, 22, 18)
        hero_layout.setSpacing(4)
        hero_title_row = self._build_section_title_row("功能总览", QStyle.SP_DesktopIcon)
        hero_desc = QLabel("按模块进入功能窗口，统一执行视频整理、分类、分析与合并任务。")
        hero_desc.setObjectName("mutedLabel")
        hero_layout.addLayout(hero_title_row)
        hero_layout.addWidget(hero_desc)
        layout.addWidget(hero)

        quick_box = QGroupBox("快捷入口")
        quick_layout = QVBoxLayout(quick_box)
        quick_layout.setSpacing(14)
        for category_index, category in enumerate(catalog.get("categories", [])):
            category_key = f"category:{category_index}"
            category_frame = QFrame()
            category_frame.setObjectName("sectionFrame")
            category_layout = QVBoxLayout(category_frame)
            category_layout.setContentsMargins(16, 16, 16, 16)
            category_layout.setSpacing(10)

            header_row = QHBoxLayout()
            title = QLabel(category.get("title", "未命名模块"))
            title.setObjectName("sectionTitle")
            open_category_button = QPushButton("进入模块")
            self._set_button_icon(open_category_button, self._module_icon_enum(category_key, category.get("title", "")))
            open_category_button.clicked.connect(lambda _, key=category_key: self.navigate_to_page(key))
            header_row.addWidget(title)
            header_row.addStretch(1)
            header_row.addWidget(open_category_button)
            category_layout.addLayout(header_row)

            actions_layout = QGridLayout()
            actions_layout.setHorizontalSpacing(10)
            actions_layout.setVerticalSpacing(10)
            columns = 3
            for action_index, action in enumerate(category.get("actions", [])):
                action_key = f"{category_key}:action:{action_index}"
                entry = 功能入口卡片(action.get("title", "未命名功能"), action.get("description", ""), action_key)
                entry.opened.connect(self.open_action_window)
                actions_layout.addWidget(entry, action_index // columns, action_index % columns)
            category_layout.addLayout(actions_layout)
            quick_layout.addWidget(category_frame)

        layout.addWidget(quick_box)
        layout.addStretch(1)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(page)
        return scroll

    def build_monitor_page(self, environment):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(12)

        hero = QFrame()
        hero.setObjectName("heroPanel")
        hero_layout = QVBoxLayout(hero)
        hero_layout.setContentsMargins(20, 18, 20, 18)
        hero_title_row = self._build_section_title_row("状态监控", QStyle.SP_MessageBoxInformation)
        hero_desc = QLabel("查看当前运行环境与关键依赖状态。")
        hero_desc.setObjectName("mutedLabel")
        hero_layout.addLayout(hero_title_row)
        hero_layout.addWidget(hero_desc)
        layout.addWidget(hero)

        toolbar = QFrame()
        toolbar.setObjectName("sectionFrame")
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(16, 14, 16, 14)
        toolbar_layout.setSpacing(10)

        summary_row = QHBoxLayout()
        summary_row.setSpacing(10)
        total_chip, self.monitor_total_value_label = self._build_monitor_stat_chip(
            "已检测",
            "monitorStatChip_info",
            self.style().standardIcon(QStyle.SP_FileDialogDetailedView),
        )
        ok_chip, self.monitor_ok_value_label = self._build_monitor_stat_chip(
            "正常",
            "monitorStatChip_ok",
            self.style().standardIcon(QStyle.SP_DialogApplyButton),
        )
        issue_chip, self.monitor_issue_value_label = self._build_monitor_stat_chip(
            "异常",
            "monitorStatChip_issue",
            self.style().standardIcon(QStyle.SP_MessageBoxWarning),
        )
        summary_row.addWidget(total_chip)
        summary_row.addWidget(ok_chip)
        summary_row.addWidget(issue_chip)
        summary_row.addStretch(1)

        self.monitor_update_label = QLabel("尚未刷新")
        self.monitor_update_label.setObjectName("monitorMeta")
        refresh_button = QPushButton("刷新状态")
        refresh_button.setObjectName("primaryButton")
        refresh_button.setFixedHeight(40)
        self._set_button_icon(refresh_button, QStyle.SP_BrowserReload)
        refresh_button.clicked.connect(self.refresh_monitor_status)

        toolbar_layout.addLayout(summary_row, 1)
        toolbar_layout.addStretch(1)
        toolbar_layout.addWidget(self.monitor_update_label)
        toolbar_layout.addWidget(refresh_button)
        layout.addWidget(toolbar)

        monitor_group = QGroupBox("环境状态")
        self.monitor_grid_layout = QGridLayout(monitor_group)
        self.monitor_grid_layout.setHorizontalSpacing(12)
        self.monitor_grid_layout.setVerticalSpacing(12)
        layout.addWidget(monitor_group)
        layout.addStretch(1)

        self.update_monitor_cards(environment, mark_refresh=False)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(page)
        return scroll

    def _build_monitor_stat_chip(self, title, object_name, icon):
        chip = QFrame()
        chip.setObjectName(object_name)
        chip_layout = QHBoxLayout(chip)
        chip_layout.setContentsMargins(12, 10, 12, 10)
        chip_layout.setSpacing(10)

        icon_label = QLabel()
        icon_label.setPixmap(icon.pixmap(16, 16))
        icon_label.setObjectName("monitorStatIcon")

        text_block = QVBoxLayout()
        text_block.setContentsMargins(0, 0, 0, 0)
        text_block.setSpacing(1)

        title_label = QLabel(title)
        title_label.setObjectName("monitorStatTitle")
        value_label = QLabel("0")
        value_label.setObjectName("monitorStatValue")

        text_block.addWidget(title_label)
        text_block.addWidget(value_label)

        chip_layout.addWidget(icon_label)
        chip_layout.addLayout(text_block)
        return chip, value_label

    def build_history_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(12)

        hero = QFrame()
        hero.setObjectName("heroPanel")
        hero_layout = QVBoxLayout(hero)
        hero_layout.setContentsMargins(20, 18, 20, 18)
        hero_title_row = self._build_section_title_row("历史记录", QStyle.SP_FileDialogDetailedView)
        hero_desc = QLabel("查看最近执行的任务记录，并按动作筛选显示。")
        hero_desc.setObjectName("mutedLabel")
        hero_layout.addLayout(hero_title_row)
        hero_layout.addWidget(hero_desc)
        layout.addWidget(hero)

        toolbar = QFrame()
        toolbar.setObjectName("sectionFrame")
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(16, 14, 16, 14)
        toolbar_layout.setSpacing(10)

        self.history_summary_label = QLabel("")
        self.history_summary_label.setObjectName("monitorSummary")
        self.history_filter_combo = QComboBox()
        self.history_filter_combo.setMinimumWidth(220)
        self.history_filter_combo.currentIndexChanged.connect(lambda *_: self.refresh_history(silent=True))
        self.history_update_label = QLabel("尚未刷新")
        self.history_update_label.setObjectName("monitorMeta")
        refresh_button = QPushButton("刷新记录")
        refresh_button.setObjectName("primaryButton")
        refresh_button.setFixedHeight(40)
        self._set_button_icon(refresh_button, QStyle.SP_BrowserReload)
        refresh_button.clicked.connect(self.refresh_history)

        toolbar_layout.addWidget(self.history_summary_label)
        toolbar_layout.addStretch(1)
        toolbar_layout.addWidget(self.history_filter_combo)
        toolbar_layout.addWidget(self.history_update_label)
        toolbar_layout.addWidget(refresh_button)
        layout.addWidget(toolbar)

        history_group = QGroupBox("最近任务")
        self.history_list_layout = QVBoxLayout(history_group)
        self.history_list_layout.setContentsMargins(12, 12, 12, 12)
        self.history_list_layout.setSpacing(10)
        layout.addWidget(history_group)
        layout.addStretch(1)

        self.update_history_cards(self.history_items, mark_refresh=False)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(page)
        return scroll

    def _clear_layout_widgets(self, layout):
        while layout is not None and layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            child_layout = item.layout()
            if widget is not None:
                widget.deleteLater()
            elif child_layout is not None:
                self._clear_layout_widgets(child_layout)

    def update_monitor_cards(self, environment, mark_refresh=True):
        if self.monitor_grid_layout is None:
            return

        self._clear_layout_widgets(self.monitor_grid_layout)
        environment = environment or {}
        ok_count = 0
        issue_count = 0
        columns = 3

        for index, (name, status) in enumerate(environment.items()):
            status_text = "" if status is None else str(status)
            if status_text.lower() == "ok":
                ok_count += 1
            else:
                issue_count += 1
            card = 信息卡片(name, status_text or "-", "")
            self.monitor_grid_layout.addWidget(card, index // columns, index % columns)

        if not environment:
            empty_label = QLabel("暂无状态数据，点击右上角刷新状态。")
            empty_label.setObjectName("mutedLabel")
            self.monitor_grid_layout.addWidget(empty_label, 0, 0)

        total = len(environment)
        if self.monitor_total_value_label is not None:
            self.monitor_total_value_label.setText(str(total))
        if self.monitor_ok_value_label is not None:
            self.monitor_ok_value_label.setText(str(ok_count))
        if self.monitor_issue_value_label is not None:
            self.monitor_issue_value_label.setText(str(issue_count))
        if self.monitor_summary_label is not None:
            self.monitor_summary_label.setText(f"已检测 {total} 项，正常 {ok_count} 项")

        if self.monitor_update_label is not None and mark_refresh:
            self.monitor_update_label.setText("最近刷新 " + datetime.now().strftime("%H:%M:%S"))

    def update_history_filter(self):
        if self.history_filter_combo is None:
            return
        current_value = self.history_filter_combo.currentData()
        self.history_filter_combo.blockSignals(True)
        self.history_filter_combo.clear()
        self.history_filter_combo.addItem("全部动作", "")
        for category in (self.catalog_data or {}).get("categories", []):
            for action in category.get("actions", []):
                self.history_filter_combo.addItem(action.get("title", action.get("id", "-")), action.get("id", ""))
        if current_value is not None:
            index = self.history_filter_combo.findData(current_value)
            if index >= 0:
                self.history_filter_combo.setCurrentIndex(index)
        self.history_filter_combo.blockSignals(False)

    def _build_history_card(self, item):
        frame = QFrame()
        frame.setObjectName("sectionFrame")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(8)

        header = QHBoxLayout()
        status_icon = QLabel()
        status_icon.setObjectName("historyIconBadge")
        status_icon_enum = QStyle.SP_DialogApplyButton if item.get("success") else QStyle.SP_MessageBoxWarning
        status_icon.setPixmap(self.style().standardIcon(status_icon_enum).pixmap(14, 14))
        title = QLabel(item.get("action_title") or item.get("action_id") or "-")
        title.setObjectName("fieldLabel")
        status = QLabel("Success" if item.get("success") else "Failed")
        status.setObjectName("softBadge" if item.get("success") else "codeBadge")
        header.addWidget(status_icon, 0, Qt.AlignVCenter)
        header.addWidget(title)
        header.addStretch(1)
        header.addWidget(status)
        layout.addLayout(header)

        meta = QLabel(f"Action: {item.get('action_id', '-')}    Time: {item.get('created_at', '-')}")
        meta.setObjectName("mutedLabel")
        layout.addWidget(meta)

        message = QLabel(item.get("message") or "No message")
        message.setWordWrap(True)
        message.setObjectName("toolbarLabel")
        layout.addWidget(message)
        return frame

    def _set_button_icon(self, button, icon_enum, size=15):
        button.setIcon(self.style().standardIcon(icon_enum))
        button.setIconSize(QSize(size, size))

    def _module_icon_enum(self, page_key, title):
        if page_key == "overview":
            return QStyle.SP_DesktopIcon
        if page_key == "monitor":
            return QStyle.SP_MessageBoxInformation
        if page_key == "history":
            return QStyle.SP_FileDialogDetailedView
        title_text = str(title or "")
        if "文件" in title_text:
            return QStyle.SP_DirOpenIcon
        if "分类" in title_text:
            return QStyle.SP_FileDialogContentsView
        if "统计" in title_text:
            return QStyle.SP_FileDialogInfoView
        if "自动" in title_text or "合并" in title_text:
            return QStyle.SP_MediaPlay
        return QStyle.SP_FileIcon

    def _build_section_title_row(self, text, icon_enum):
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(10)
        icon_label = QLabel()
        icon_label.setObjectName("sectionIconBadge")
        icon_label.setPixmap(self.style().standardIcon(icon_enum).pixmap(16, 16))
        title_label = QLabel(text)
        title_label.setObjectName("sectionTitle")
        row.addWidget(icon_label, 0, Qt.AlignVCenter)
        row.addWidget(title_label, 0, Qt.AlignVCenter)
        row.addStretch(1)
        return row

    def update_history_cards(self, items, mark_refresh=True):
        if self.history_list_layout is None:
            return

        self._clear_layout_widgets(self.history_list_layout)
        items = items or []

        if self.history_summary_label is not None:
            self.history_summary_label.setText(f"最近记录 {len(items)} 条")
        if self.history_update_label is not None and mark_refresh:
            self.history_update_label.setText("最近刷新 " + datetime.now().strftime("%H:%M:%S"))

        if not items:
            empty_label = QLabel("暂无历史记录，请先执行任务或点击刷新记录。")
            empty_label.setObjectName("mutedLabel")
            self.history_list_layout.addWidget(empty_label)
            self.history_list_layout.addStretch(1)
            return

        for item in items:
            self.history_list_layout.addWidget(self._build_history_card(item))
        self.history_list_layout.addStretch(1)

    def build_category_page(self, category, category_key):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(12)

        intro = QFrame()
        intro.setObjectName("heroPanel")
        intro_layout = QVBoxLayout(intro)
        intro_layout.setContentsMargins(20, 18, 20, 18)
        title_row = self._build_section_title_row(category.get("title", "未命名模块"), self._module_icon_enum(category_key, category.get("title", "")))
        intro_text = QLabel("选择下方功能按钮打开独立配置窗口。")
        intro_text.setObjectName("mutedLabel")
        intro_layout.addLayout(title_row)
        intro_layout.addWidget(intro_text)
        layout.addWidget(intro)

        entry_frame = QFrame()
        entry_frame.setObjectName("sectionFrame")
        entry_layout = QGridLayout(entry_frame)
        entry_layout.setContentsMargins(16, 16, 16, 16)
        entry_layout.setHorizontalSpacing(10)
        entry_layout.setVerticalSpacing(10)

        actions = category.get("actions", [])
        columns = 3
        for action_index, action in enumerate(actions):
            action_key = f"{category_key}:action:{action_index}"
            entry = 功能入口卡片(action.get("title", "未命名功能"), action.get("description", ""), action_key)
            entry.opened.connect(self.open_action_window)
            entry_layout.addWidget(entry, action_index // columns, action_index % columns)

        layout.addWidget(entry_frame)

        if not actions:
            empty_state = QLabel("当前模块下暂无可执行功能。")
            empty_state.setObjectName("mutedLabel")
            layout.addWidget(empty_state)

        layout.addStretch(1)
        return container

    def _apply_styles(self):
        self.setStyleSheet(APP_STYLESHEET)


ActionWindow = next(
    obj for obj in globals().values() if isinstance(obj, type) and issubclass(obj, QDialog) and obj is not QDialog
)
MainWindow = next(
    obj for obj in globals().values()
    if isinstance(obj, type) and issubclass(obj, QMainWindow) and obj is not QMainWindow
)
