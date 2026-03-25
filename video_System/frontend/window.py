import json
import urllib.parse
import urllib.request
from datetime import datetime

from PyQt5.QtCore import QThread, QTimer, Qt
from PyQt5.QtWidgets import (
    QDialog,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from video_system.frontend.api import ApiWorker
from video_system.frontend.styles import APP_STYLESHEET, APP_TITLE, DEFAULT_BASE_URL
from video_system.frontend.widgets import 信息卡片, 动作卡片, 功能入口卡片


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

        title = QLabel(action_meta.get("title", "未命名功能"))
        title.setObjectName("sectionTitle")
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
        intro_layout.addWidget(title)
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
        self.monitor_grid_layout = None
        self.monitor_summary_label = None
        self.monitor_update_label = None

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
        title = QLabel(APP_TITLE)
        title.setObjectName("headerTitle")
        subtitle = QLabel("视频处理控制台")
        subtitle.setObjectName("headerSubtitle")
        subtitle.setWordWrap(True)
        title_block.addWidget(title)
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
        refresh_button.clicked.connect(self.fetch_catalog)
        health_button = QPushButton("检查连接")
        health_button.setFixedHeight(42)
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
        saved_params = self.fetch_action_preferences(record["action"].get("id"))
        if saved_params:
            window.action_card.apply_params(saved_params)
        window.setAttribute(Qt.WA_DeleteOnClose, True)
        window.destroyed.connect(lambda *_: self.action_windows.pop(action_key, None))
        self.action_windows[action_key] = window
        window.show()

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

    def request(self, method, path, payload=None, label="请求", quiet_if_busy=False):
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

    def run_action(self, action_id, params, title):
        self.request("POST", "/run", payload={"action_id": action_id, "params": params}, label=f"执行任务: {title}")

    def on_error(self, message):
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

        for category_index, category in enumerate(categories):
            category_key = f"category:{category_index}"
            self._add_sidebar_page(category_key, category.get("title", "未命名模块"), self.build_category_page(category, category_key))
            for action_index, action in enumerate(category.get("actions", [])):
                action_key = f"{category_key}:action:{action_index}"
                self.action_registry[action_key] = {
                    "category_title": category.get("title", "未命名模块"),
                    "action": action,
                }

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
        hero_title = QLabel("功能总览")
        hero_title.setObjectName("heroTitle")
        hero_desc = QLabel("按模块进入功能窗口，统一执行视频整理、分类、分析与合并任务。")
        hero_desc.setObjectName("mutedLabel")
        hero_layout.addWidget(hero_title)
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
        hero_title = QLabel("状态监控")
        hero_title.setObjectName("sectionTitle")
        hero_desc = QLabel("查看当前运行环境与关键依赖状态。")
        hero_desc.setObjectName("mutedLabel")
        hero_layout.addWidget(hero_title)
        hero_layout.addWidget(hero_desc)
        layout.addWidget(hero)

        toolbar = QFrame()
        toolbar.setObjectName("sectionFrame")
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(16, 14, 16, 14)
        toolbar_layout.setSpacing(10)

        self.monitor_summary_label = QLabel("")
        self.monitor_summary_label.setObjectName("monitorSummary")
        self.monitor_update_label = QLabel("尚未刷新")
        self.monitor_update_label.setObjectName("monitorMeta")
        refresh_button = QPushButton("刷新状态")
        refresh_button.setObjectName("primaryButton")
        refresh_button.setFixedHeight(40)
        refresh_button.clicked.connect(self.refresh_monitor_status)

        toolbar_layout.addWidget(self.monitor_summary_label)
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
        columns = 3

        for index, (name, status) in enumerate(environment.items()):
            status_text = "" if status is None else str(status)
            if status_text.lower() == "ok":
                ok_count += 1
            card = 信息卡片(name, status_text or "-", "")
            self.monitor_grid_layout.addWidget(card, index // columns, index % columns)

        if not environment:
            empty_label = QLabel("暂无状态数据，点击右上角刷新状态。")
            empty_label.setObjectName("mutedLabel")
            self.monitor_grid_layout.addWidget(empty_label, 0, 0)

        if self.monitor_summary_label is not None:
            total = len(environment)
            self.monitor_summary_label.setText(f"已检测 {total} 项，正常 {ok_count} 项")

        if self.monitor_update_label is not None and mark_refresh:
            self.monitor_update_label.setText("最近刷新 " + datetime.now().strftime("%H:%M:%S"))

    def build_category_page(self, category, category_key):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(12)

        intro = QFrame()
        intro.setObjectName("heroPanel")
        intro_layout = QVBoxLayout(intro)
        intro_layout.setContentsMargins(20, 18, 20, 18)
        title = QLabel(category.get("title", "未命名模块"))
        title.setObjectName("sectionTitle")
        intro_text = QLabel("选择下方功能按钮打开独立配置窗口。")
        intro_text.setObjectName("mutedLabel")
        intro_layout.addWidget(title)
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
