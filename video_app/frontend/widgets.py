from PyQt5.QtCore import QSize, Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFrame,
    QGraphicsDropShadowEffect,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QStyle,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


PATH_FIELD_TYPES = {"dir", "dir_optional", "file", "file_optional", "save_file"}


class NoWheelComboBox(QComboBox):
    def wheelEvent(self, event):
        if self.view().isVisible():
            super().wheelEvent(event)
            return
        event.ignore()


class BoolStateChip(QPushButton):
    def __init__(self, checked=False, on_icon=None, off_icon=None):
        super().__init__("")
        self.setObjectName("boolStateChip")
        self.setCheckable(True)
        self.setMinimumHeight(40)
        self.setCursor(Qt.PointingHandCursor)
        self._on_icon = on_icon
        self._off_icon = off_icon
        self.toggled.connect(self._sync_state)
        self.setChecked(bool(checked))
        self._sync_state(self.isChecked())

    def _sync_state(self, checked):
        self.setText("启用" if checked else "关闭")
        self.setIcon(self._on_icon if checked else self._off_icon)
        self.setIconSize(QSize(14, 14))
        self.setProperty("state", "on" if checked else "off")
        self.style().unpolish(self)
        self.style().polish(self)


class SegmentedSelect(QWidget):
    selectionChanged = pyqtSignal(object, str)

    def __init__(self, options, default=None):
        super().__init__()
        self._options = list(options or [])
        self._buttons = []
        self._current_index = -1

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        for index, option in enumerate(self._options):
            button = QPushButton(str(option.get("label", "")))
            button.setObjectName("segmentButton")
            button.setCheckable(True)
            button.setCursor(Qt.PointingHandCursor)
            button.setMinimumHeight(40)
            button.clicked.connect(lambda checked=False, idx=index: self.setCurrentIndex(idx))
            layout.addWidget(button, 1)
            self._buttons.append(button)

        if default is not None:
            index = self.findData(default)
            if index < 0:
                index = 0 if self._buttons else -1
            self.setCurrentIndex(index)
        elif self._buttons:
            self.setCurrentIndex(0)

    def set_option_icon(self, value, icon):
        index = self.findData(value)
        if index < 0:
            return
        self._buttons[index].setIcon(icon)
        self._buttons[index].setIconSize(QSize(14, 14))

    def currentData(self):
        if 0 <= self._current_index < len(self._options):
            return self._options[self._current_index].get("value")
        return None

    def currentText(self):
        if 0 <= self._current_index < len(self._options):
            return str(self._options[self._current_index].get("label", ""))
        return ""

    def findData(self, value):
        for index, option in enumerate(self._options):
            if option.get("value") == value:
                return index
        return -1

    def findText(self, text):
        for index, option in enumerate(self._options):
            if str(option.get("label", "")) == str(text):
                return index
        return -1

    def setCurrentIndex(self, index):
        if index < 0 or index >= len(self._buttons):
            return
        self._current_index = index
        for button_index, button in enumerate(self._buttons):
            button.setChecked(button_index == index)
        self.selectionChanged.emit(self.currentData(), self.currentText())


class PanelStepper(QWidget):
    valueChanged = pyqtSignal(int)

    def __init__(self, minimum=0, maximum=999999, step=1, value=0):
        super().__init__()
        self._minimum = int(minimum)
        self._maximum = int(maximum)
        self._step = max(1, int(step))
        self._value = self._minimum

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.minus_button = QPushButton("")
        self.minus_button.setObjectName("stepperButton")
        self.minus_button.setIcon(self.style().standardIcon(QStyle.SP_ArrowLeft))
        self.minus_button.setIconSize(QSize(12, 12))
        self.minus_button.setFixedSize(40, 40)
        self.minus_button.clicked.connect(lambda: self.setValue(self._value - self._step))

        self.value_label = QLineEdit()
        self.value_label.setObjectName("stepperValue")
        self.value_label.setReadOnly(True)
        self.value_label.setAlignment(Qt.AlignCenter)
        self.value_label.setMinimumHeight(40)

        self.plus_button = QPushButton("")
        self.plus_button.setObjectName("stepperButton")
        self.plus_button.setIcon(self.style().standardIcon(QStyle.SP_ArrowRight))
        self.plus_button.setIconSize(QSize(12, 12))
        self.plus_button.setFixedSize(40, 40)
        self.plus_button.clicked.connect(lambda: self.setValue(self._value + self._step))

        layout.addWidget(self.minus_button)
        layout.addWidget(self.value_label, 1)
        layout.addWidget(self.plus_button)

        self.setValue(value)

    def _sync(self):
        self.value_label.setText(str(self._value))
        self.minus_button.setEnabled(self._value > self._minimum)
        self.plus_button.setEnabled(self._value < self._maximum)

    def value(self):
        return int(self._value)

    def setValue(self, value):
        self._value = max(self._minimum, min(self._maximum, int(value)))
        self._sync()
        self.valueChanged.emit(self._value)


class PathInput(QWidget):
    pathCommitted = pyqtSignal(str, str)
    refreshRequested = pyqtSignal(str)
    deleteRequested = pyqtSignal(str, str)
    clearAllRequested = pyqtSignal(str)

    def __init__(self, mode="dir"):
        super().__init__()
        self.mode = mode
        self._locked = True
        self._edit_enabled = False

        self.combo = NoWheelComboBox()
        self.combo.setEditable(True)
        self.combo.setInsertPolicy(QComboBox.NoInsert)
        self.combo.setObjectName("pathHistoryCombo")
        self.combo.setMinimumHeight(36)
        self.combo.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        if self.combo.lineEdit() is not None:
            self.combo.lineEdit().setObjectName("pathLineEdit")

        self.browse_button = self._create_icon_button(
            "utilityIconButton",
            self.style().standardIcon(QStyle.SP_DirOpenIcon),
            "浏览并选择路径",
        )
        self.edit_button = self._create_icon_button(
            "toggleIconButton",
            self.style().standardIcon(QStyle.SP_FileDialogDetailedView),
            "编辑模式",
            checkable=True,
        )
        self.edit_button.setChecked(False)
        self.lock_button = self._create_icon_button(
            "toggleIconButton",
            self.style().standardIcon(QStyle.SP_BrowserStop),
            "锁定当前路径",
            checkable=True,
        )
        self.lock_button.setChecked(True)
        self.refresh_button = self._create_icon_button(
            "utilityIconButton",
            self.style().standardIcon(QStyle.SP_BrowserReload),
            "刷新历史路径",
        )
        self.delete_button = self._create_icon_button(
            "dangerIconButton",
            self.style().standardIcon(getattr(QStyle, "SP_LineEditClearButton", QStyle.SP_DialogCloseButton)),
            "删除当前历史路径",
        )
        self.clear_button = self._create_icon_button(
            "dangerIconButton",
            self.style().standardIcon(getattr(QStyle, "SP_TrashIcon", QStyle.SP_DialogDiscardButton)),
            "清空当前类型全部历史路径",
        )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        layout.addWidget(self.combo, 1)
        layout.addWidget(self.browse_button)
        layout.addWidget(self.edit_button)
        layout.addWidget(self.lock_button)
        layout.addWidget(self.refresh_button)
        layout.addWidget(self.delete_button)
        layout.addWidget(self.clear_button)

        self.browse_button.clicked.connect(self.browse)
        self.edit_button.toggled.connect(self.set_edit_enabled)
        self.lock_button.toggled.connect(self.set_locked)
        self.refresh_button.clicked.connect(self.refresh_history)
        self.delete_button.clicked.connect(self.delete_current_history)
        self.clear_button.clicked.connect(self.clear_all_history)
        self.combo.activated.connect(self._handle_selection_changed)
        if self.combo.lineEdit() is not None:
            self.combo.lineEdit().editingFinished.connect(self.commit_current_value)

        self._apply_interaction_state()

    def set_context(self, label="", purpose=""):
        line_edit = self.combo.lineEdit()
        if line_edit is None:
            return
        placeholder = purpose or label or "请输入路径"
        line_edit.setPlaceholderText(placeholder)

    def _create_icon_button(self, object_name, icon, tooltip, checkable=False):
        button = QPushButton("")
        button.setObjectName(object_name)
        button.setFixedSize(32, 32)
        button.setIcon(icon)
        button.setIconSize(QSize(14, 14))
        button.setToolTip(tooltip)
        button.setCursor(Qt.PointingHandCursor)
        button.setCheckable(checkable)
        shadow = QGraphicsDropShadowEffect(button)
        shadow.setBlurRadius(12)
        shadow.setOffset(0, 2)
        shadow.setColor(QColor(15, 23, 42, 18))
        button.setGraphicsEffect(shadow)
        return button

    def _apply_interaction_state(self):
        line_edit = self.combo.lineEdit()
        editable = self._edit_enabled and not self._locked
        if line_edit is not None:
            line_edit.setReadOnly(not editable)
        self.browse_button.setEnabled(not self._locked)
        self.edit_button.setEnabled(not self._locked)
        self.delete_button.setEnabled(not self._locked)
        self.clear_button.setEnabled(not self._locked)
        self.refresh_button.setEnabled(True)
        self.combo.setToolTip("路径已锁定" if self._locked else self.value())
        self.edit_button.setToolTip("退出编辑模式" if editable else "进入编辑模式")
        self.lock_button.setToolTip("解锁当前路径" if self._locked else "锁定当前路径")

    def _handle_selection_changed(self, *_):
        if not self._locked:
            self.commit_current_value()

    def set_edit_enabled(self, enabled):
        self._edit_enabled = bool(enabled)
        self._apply_interaction_state()

    def set_locked(self, locked):
        self._locked = bool(locked)
        self._apply_interaction_state()

    def history_kind(self):
        if self.mode in ("dir", "dir_optional"):
            return "dir"
        if self.mode == "save_file":
            return "save_file"
        return "file"

    def _add_candidate(self, value):
        text = str(value or "").strip()
        if not text:
            return
        current_text = self.value()
        index = self.combo.findText(text, Qt.MatchFixedString)
        if index >= 0:
            self.combo.removeItem(index)
        self.combo.insertItem(0, text)
        if current_text and current_text != text:
            self.combo.setEditText(current_text)

    def browse(self):
        if self._locked:
            return
        current = self.value()
        if self.mode in ("dir", "dir_optional"):
            path = QFileDialog.getExistingDirectory(self, "选择目录", current)
        elif self.mode == "save_file":
            path, _ = QFileDialog.getSaveFileName(self, "选择输出文件", current, "Excel Files (*.xlsx);;All Files (*)")
        else:
            path, _ = QFileDialog.getOpenFileName(self, "选择文件", current)
        if path:
            self.set_value(path)
            self.commit_current_value()

    def value(self):
        return self.combo.currentText().strip()

    def set_value(self, value):
        text = "" if value is None else str(value).strip()
        if text:
            self._add_candidate(text)
        self.combo.setEditText(text)
        self.combo.setToolTip(text)

    def set_history(self, values):
        current = self.value()
        self.combo.blockSignals(True)
        self.combo.clear()
        seen = set()
        for value in values or []:
            text = str(value or "").strip()
            if not text or text in seen:
                continue
            self.combo.addItem(text)
            seen.add(text)
        self.combo.blockSignals(False)
        if current:
            self.combo.setEditText(current)
        elif self.combo.count() > 0:
            self.combo.setCurrentIndex(0)
        self.combo.setToolTip(self.value())

    def commit_current_value(self):
        if self._locked:
            return
        value = self.value()
        if value:
            self._add_candidate(value)
            self.combo.setEditText(value)
            self.combo.setToolTip(value)
            self.pathCommitted.emit(value, self.history_kind())

    def refresh_history(self):
        self.refreshRequested.emit(self.history_kind())
        self.combo.update()
        self.update()

    def delete_current_history(self):
        if self._locked:
            return
        value = self.value()
        if value:
            self.deleteRequested.emit(value, self.history_kind())

    def clear_all_history(self):
        if self._locked:
            return
        self.clearAllRequested.emit(self.history_kind())

    def remove_history_value(self, value, clear_current=False):
        text = str(value or "").strip()
        if not text:
            return
        index = self.combo.findText(text, Qt.MatchFixedString)
        if index >= 0:
            self.combo.removeItem(index)
        if clear_current and self.value() == text:
            self.combo.setEditText("")
        self.combo.setToolTip(self.value())
        self.combo.update()
        self.update()


class StatusStrip(QFrame):
    def __init__(self, title, value, hint):
        super().__init__()
        self.setObjectName("statusStrip")
        self.setMinimumHeight(112)
        state_key, state_label, detail_text, icon = self._resolve_state(str(value or ""), str(hint or ""))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(10)

        icon_shell = QFrame()
        icon_shell.setObjectName(f"statusIconShell_{state_key}")
        icon_shell.setFixedSize(38, 38)
        icon_layout = QVBoxLayout(icon_shell)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_layout.setAlignment(Qt.AlignCenter)

        icon_label = QLabel()
        icon_label.setPixmap(icon.pixmap(18, 18))
        icon_label.setAlignment(Qt.AlignCenter)
        icon_layout.addWidget(icon_label)
        header.addWidget(icon_shell, 0, Qt.AlignTop)

        title_label = QLabel(title)
        title_label.setObjectName("statusLabel")
        header.addWidget(title_label, 1, Qt.AlignLeft | Qt.AlignVCenter)

        value_label = QLabel(state_label)
        value_label.setObjectName(f"statusValueBadge_{state_key}")
        value_label.setAlignment(Qt.AlignCenter)
        header.addWidget(value_label, 0, Qt.AlignRight | Qt.AlignVCenter)
        layout.addLayout(header)

        detail_row = QHBoxLayout()
        detail_row.setContentsMargins(0, 0, 0, 0)
        detail_row.setSpacing(8)

        detail_badge = QLabel("环境项")
        detail_badge.setObjectName("statusMetaBadge")
        detail_row.addWidget(detail_badge, 0, Qt.AlignLeft | Qt.AlignVCenter)

        detail_row.addStretch(1)
        layout.addLayout(detail_row)

        if detail_text:
            hint_label = QLabel(detail_text)
            hint_label.setObjectName("statusHint")
            hint_label.setWordWrap(True)
            hint_label.setTextInteractionFlags(Qt.NoTextInteraction)
            hint_label.setToolTip(str(value or hint or ""))
            layout.addWidget(hint_label)

    def _resolve_state(self, raw_value, raw_hint):
        normalized = raw_value.strip()
        lowered = normalized.lower()
        detail_text = raw_hint.strip()
        if not detail_text and lowered != "ok":
            detail_text = normalized
        if len(detail_text) > 36:
            detail_text = detail_text[:33] + "..."
        if lowered == "ok":
            return "ok", "正常", "", self.style().standardIcon(QStyle.SP_DialogApplyButton)
        if "missing" in lowered:
            return "missing", "缺失", detail_text, self.style().standardIcon(QStyle.SP_MessageBoxWarning)
        if "unavailable" in lowered or "denied" in lowered or "error" in lowered or "failed" in lowered:
            return "error", "异常", detail_text, self.style().standardIcon(QStyle.SP_MessageBoxCritical)
        return "info", "检查", detail_text, self.style().standardIcon(QStyle.SP_MessageBoxInformation)


class ActionEntryTile(QFrame):
    opened = pyqtSignal(str)

    def __init__(self, title, description, page_key, icon_enum=QStyle.SP_FileIcon):
        super().__init__()
        self.page_key = page_key
        self.setObjectName("entryTile")
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(142)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(10)

        icon = QLabel()
        icon.setObjectName("entryIcon")
        icon.setPixmap(self.style().standardIcon(icon_enum).pixmap(16, 16))
        header.addWidget(icon, 0, Qt.AlignTop)

        status_badge = QLabel("可执行")
        status_badge.setObjectName("entryStatus")
        status_badge.setAlignment(Qt.AlignCenter)
        header.addStretch(1)
        header.addWidget(status_badge, 0, Qt.AlignTop)
        layout.addLayout(header)

        title_label = QLabel(title)
        title_label.setObjectName("entryTitle")
        title_label.setWordWrap(True)
        title_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        layout.addWidget(title_label)

        desc_label = QLabel(description or "打开独立功能窗口进行配置和执行。")
        desc_label.setObjectName("entryDesc")
        desc_label.setWordWrap(True)
        desc_label.setMinimumHeight(34)
        layout.addWidget(desc_label, 1)

        footer = QHBoxLayout()
        footer.setContentsMargins(0, 0, 0, 0)
        footer.setSpacing(8)

        action_badge = QLabel("快速操作")
        action_badge.setObjectName("entryMetaBadge")
        action_badge.setAlignment(Qt.AlignCenter)
        footer.addWidget(action_badge, 0, Qt.AlignLeft | Qt.AlignVCenter)
        footer.addStretch(1)

        open_button = QPushButton("打开")
        open_button.setObjectName("entryOpenButton")
        open_button.setCursor(Qt.PointingHandCursor)
        open_button.setMinimumWidth(84)
        open_button.setFixedHeight(32)
        open_button.setIcon(self.style().standardIcon(QStyle.SP_ArrowForward))
        open_button.setIconSize(QSize(14, 14))
        open_button.clicked.connect(self._emit_opened)
        footer.addWidget(open_button, 0, Qt.AlignRight | Qt.AlignVCenter)
        layout.addLayout(footer)

    def _emit_opened(self):
        self.opened.emit(self.page_key)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setProperty("pressed", True)
            self.style().unpolish(self)
            self.style().polish(self)
            self._emit_opened()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.setProperty("pressed", False)
        self.style().unpolish(self)
        self.style().polish(self)
        super().mouseReleaseEvent(event)


class ModuleEntryCard(QFrame):
    opened = pyqtSignal(str)

    def __init__(self, title, description, page_key, icon_enum, action_count=0, preview_actions=None):
        super().__init__()
        self.page_key = page_key
        self.setObjectName("moduleEntryCard")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(14, 14, 14, 14)
        outer.setSpacing(10)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(12)

        icon = QLabel()
        icon.setObjectName("moduleEntryIcon")
        icon.setPixmap(self.style().standardIcon(icon_enum).pixmap(18, 18))
        header.addWidget(icon, 0, Qt.AlignTop)

        title_block = QVBoxLayout()
        title_block.setContentsMargins(0, 0, 0, 0)
        title_block.setSpacing(3)

        title_label = QLabel(title)
        title_label.setObjectName("moduleEntryTitle")
        title_block.addWidget(title_label)

        desc_label = QLabel(description or "进入模块后可打开对应功能窗口。")
        desc_label.setWordWrap(True)
        desc_label.setObjectName("moduleEntryDesc")
        title_block.addWidget(desc_label)
        header.addLayout(title_block, 1)

        status_badge = QLabel("就绪")
        status_badge.setObjectName("moduleEntryStatus")
        header.addWidget(status_badge, 0, Qt.AlignTop)
        outer.addLayout(header)

        meta_row = QHBoxLayout()
        meta_row.setContentsMargins(0, 0, 0, 0)
        meta_row.setSpacing(8)

        count_badge = QLabel(f"{int(action_count)} 个功能")
        count_badge.setObjectName("moduleEntryMetaBadge")
        meta_row.addWidget(count_badge, 0, Qt.AlignLeft | Qt.AlignVCenter)

        scope_badge = QLabel("快速入口")
        scope_badge.setObjectName("moduleEntryMetaBadge")
        meta_row.addWidget(scope_badge, 0, Qt.AlignLeft | Qt.AlignVCenter)
        meta_row.addStretch(1)
        outer.addLayout(meta_row)

        preview_actions = list(preview_actions or [])[:3]
        if preview_actions:
            preview_row = QHBoxLayout()
            preview_row.setContentsMargins(0, 0, 0, 0)
            preview_row.setSpacing(8)
            for action_title in preview_actions:
                pill = QLabel(str(action_title))
                pill.setObjectName("moduleEntryActionPill")
                preview_row.addWidget(pill, 0, Qt.AlignLeft | Qt.AlignVCenter)
            preview_row.addStretch(1)
            outer.addLayout(preview_row)

        footer = QHBoxLayout()
        footer.setContentsMargins(0, 0, 0, 0)
        footer.setSpacing(8)
        footer.addStretch(1)

        open_button = QPushButton("进入模块")
        open_button.setObjectName("moduleEntryOpenButton")
        open_button.setCursor(Qt.PointingHandCursor)
        open_button.setIcon(self.style().standardIcon(QStyle.SP_ArrowForward))
        open_button.setIconSize(QSize(14, 14))
        open_button.clicked.connect(self._emit_opened)
        footer.addWidget(open_button)
        outer.addLayout(footer)

    def _emit_opened(self):
        self.opened.emit(self.page_key)


class ActionFormCard(QFrame):
    submitted = pyqtSignal(str, dict, str)
    preferencesChanged = pyqtSignal(dict)
    pathRecorded = pyqtSignal(list)
    pathRefreshRequested = pyqtSignal(str, str)
    pathDeleteRequested = pyqtSignal(str, str, str)
    pathClearRequested = pyqtSignal(str, str)

    def __init__(self, action_meta, show_description=True):
        super().__init__()
        self.action_meta = action_meta
        self.show_description = show_description
        self.fields = {}
        self._suspend_preferences_emit = False
        self._preferences_timer = QTimer(self)
        self._preferences_timer.setSingleShot(True)
        self._preferences_timer.setInterval(280)
        self._preferences_timer.timeout.connect(self._emit_preferences_changed)
        self.setObjectName("actionCard")
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 22, 22, 22)
        layout.setSpacing(18)

        if self.show_description and self.action_meta.get("description"):
            desc = QLabel(self.action_meta.get("description", ""))
            desc.setWordWrap(True)
            desc.setObjectName("mutedLabel")
            layout.addWidget(desc)

        if self.action_meta.get("id") == "videofusion_merge":
            self._build_videofusion_layout(layout)
            self._connect_preference_watchers()
            return

        form = QGridLayout()
        form.setContentsMargins(0, 0, 0, 0)
        form.setHorizontalSpacing(14)
        form.setVerticalSpacing(14)
        row = 0
        column = 0
        for field in self.action_meta.get("fields", []):
            widget = self._build_widget(field)
            self.fields[field["name"]] = (field, widget)
            field_card = self._build_field_card(field, widget)
            span = self._field_span(field)
            form.addWidget(field_card, row, column, 1, span)
            if span == 2:
                row += 1
                column = 0
            else:
                if column == 0:
                    column = 1
                else:
                    row += 1
                    column = 0
        layout.addLayout(form)
        layout.addStretch(1)
        self._connect_preference_watchers()

        footer = QHBoxLayout()
        self.run_button = QPushButton("执行任务")
        self.run_button.setObjectName("primaryButton")
        self.run_button.setFixedHeight(44)
        self.run_button.setMinimumWidth(132)
        self.run_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.run_button.setIconSize(QSize(14, 14))
        self.run_button.clicked.connect(self.submit)
        footer.addStretch(1)
        footer.addWidget(self.run_button)
        layout.addLayout(footer)

    def _add_field_to_grid(self, grid, row, column, field):
        widget = self._build_widget(field)
        self.fields[field["name"]] = (field, widget)
        field_card = self._build_field_card(field, widget)
        span = self._field_span(field)
        grid.addWidget(field_card, row, column, 1, span)
        if span == 2:
            return row + 1, 0
        if column == 0:
            return row, 1
        return row + 1, 0

    def _build_videofusion_layout(self, layout):
        env_names = {"source_root", "runtime_root", "ffmpeg_file"}
        task_names = {"input_dir", "output_dir", "temp_dir", "target_dir", "queue_dir"}
        env_fields = []
        task_fields = []
        other_fields = []

        for field in self.action_meta.get("fields", []):
            name = field.get("name")
            if name in env_names:
                env_fields.append(field)
            elif name in task_names:
                task_fields.append(field)
            else:
                other_fields.append(field)

        summary_panel = self._build_videofusion_summary_panel()
        layout.addWidget(summary_panel)
        if env_fields:
            layout.addWidget(self._build_field_group("运行环境", env_fields))
        if task_fields:
            layout.addWidget(self._build_field_group("任务路径", task_fields))
        if other_fields:
            layout.addWidget(self._build_field_group("执行参数", other_fields))
        self._connect_videofusion_summary_updates()
        self._refresh_videofusion_summary()
        layout.addStretch(1)

        footer = QHBoxLayout()
        self.run_button = QPushButton("执行任务")
        self.run_button.setObjectName("primaryButton")
        self.run_button.setFixedHeight(44)
        self.run_button.setMinimumWidth(132)
        self.run_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.run_button.setIconSize(QSize(14, 14))
        self.run_button.clicked.connect(self.submit)
        footer.addStretch(1)
        footer.addWidget(self.run_button)
        layout.addLayout(footer)

    def _build_videofusion_summary_panel(self):
        frame = QFrame()
        frame.setObjectName("configSummaryPanel")
        outer = QVBoxLayout(frame)
        outer.setContentsMargins(16, 14, 16, 14)
        outer.setSpacing(10)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(10)

        icon = QLabel()
        icon.setObjectName("summaryPanelIcon")
        icon.setPixmap(self.style().standardIcon(QStyle.SP_FileDialogDetailedView).pixmap(16, 16))
        header.addWidget(icon, 0, Qt.AlignTop)

        title_block = QVBoxLayout()
        title_block.setContentsMargins(0, 0, 0, 0)
        title_block.setSpacing(2)

        title = QLabel("当前配置摘要")
        title.setObjectName("summaryPanelTitle")
        title_block.addWidget(title)

        subtitle = QLabel("实时汇总当前模式、方向、引擎与关键开关。")
        subtitle.setObjectName("summaryPanelSubtitle")
        title_block.addWidget(subtitle)

        header.addLayout(title_block, 1)

        status_badge = QLabel("实时同步")
        status_badge.setObjectName("summaryPanelBadge")
        header.addWidget(status_badge, 0, Qt.AlignRight | Qt.AlignVCenter)
        outer.addLayout(header)

        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(10)

        self.vf_summary_labels = {}
        summary_items = [
            ("mode", "模式", QStyle.SP_MediaPlay),
            ("orientation", "朝向", QStyle.SP_ArrowUp),
            ("engine", "引擎", QStyle.SP_ComputerIcon),
            ("fps", "帧率", QStyle.SP_FileDialogDetailedView),
            ("rotation", "旋转", QStyle.SP_BrowserReload),
            ("merge", "合并", QStyle.SP_DialogApplyButton),
            ("cleanup", "清理", getattr(QStyle, "SP_TrashIcon", QStyle.SP_DialogDiscardButton)),
            ("rename", "命名", QStyle.SP_FileIcon),
        ]
        for index, (key, label_text, icon_style) in enumerate(summary_items):
            chip = QFrame()
            chip.setObjectName("summaryChip")
            chip_layout = QVBoxLayout(chip)
            chip_layout.setContentsMargins(12, 10, 12, 10)
            chip_layout.setSpacing(8)

            top_row = QHBoxLayout()
            top_row.setContentsMargins(0, 0, 0, 0)
            top_row.setSpacing(8)

            icon = QLabel()
            icon.setObjectName("summaryChipIcon")
            icon.setPixmap(self.style().standardIcon(icon_style).pixmap(14, 14))
            top_row.addWidget(icon, 0, Qt.AlignLeft | Qt.AlignVCenter)

            label = QLabel(label_text)
            label.setObjectName("summaryChipLabel")
            top_row.addWidget(label, 0, Qt.AlignLeft | Qt.AlignVCenter)
            top_row.addStretch(1)

            value = QLabel("-")
            value.setObjectName("summaryChipValue")
            chip_layout.addLayout(top_row)
            chip_layout.addWidget(value)
            self.vf_summary_labels[key] = value
            grid.addWidget(chip, index // 4, index % 4)

        outer.addLayout(grid)
        return frame

    def _connect_videofusion_summary_updates(self):
        mapping = {
            "run_mode": self._refresh_videofusion_summary,
            "orientation": self._refresh_videofusion_summary,
            "engine": self._refresh_videofusion_summary,
            "video_fps": self._refresh_videofusion_summary,
            "rotation": self._refresh_videofusion_summary,
            "merge_video": self._refresh_videofusion_summary,
            "delete_temp_dir": self._refresh_videofusion_summary,
            "rename_output": self._refresh_videofusion_summary,
        }
        for field_name, callback in mapping.items():
            pair = self.fields.get(field_name)
            if pair is None:
                continue
            field, widget = pair
            field_type = field.get("type")
            if field_type == "bool":
                widget.toggled.connect(lambda *_args, cb=callback: cb())
            elif field_type == "int":
                if hasattr(widget, "valueChanged"):
                    widget.valueChanged.connect(lambda *_args, cb=callback: cb())
            elif field_type == "select":
                if hasattr(widget, "selectionChanged"):
                    widget.selectionChanged.connect(lambda *_args, cb=callback: cb())
                elif hasattr(widget, "currentIndexChanged"):
                    widget.currentIndexChanged.connect(lambda *_args, cb=callback: cb())

    def _refresh_videofusion_summary(self):
        if not hasattr(self, "vf_summary_labels"):
            return
        values = {
            "mode": self._summary_text("run_mode"),
            "orientation": self._summary_text("orientation"),
            "engine": self._summary_text("engine"),
            "fps": f"{self._summary_value('video_fps')} fps",
            "rotation": self._summary_text("rotation"),
            "merge": "开启" if self._summary_value("merge_video") else "关闭",
            "cleanup": "开启" if self._summary_value("delete_temp_dir") else "关闭",
            "rename": "开启" if self._summary_value("rename_output") else "关闭",
        }
        for key, label in self.vf_summary_labels.items():
            label.setText(str(values.get(key, "-")))

    def _summary_value(self, field_name):
        pair = self.fields.get(field_name)
        if pair is None:
            return ""
        field, widget = pair
        field_type = field.get("type")
        if field_type == "bool":
            return widget.isChecked()
        if field_type == "int":
            return widget.value()
        if field_type == "select":
            return widget.currentData()
        return ""

    def _summary_text(self, field_name):
        pair = self.fields.get(field_name)
        if pair is None:
            return "-"
        field, widget = pair
        field_type = field.get("type")
        if field_type == "select":
            if hasattr(widget, "currentText"):
                return widget.currentText() or "-"
            return str(widget.currentData() or "-")
        value = self._summary_value(field_name)
        return str(value or "-")

    def _build_field_group(self, title, fields):
        group = QFrame()
        group.setObjectName("fieldGroupCard")
        outer = QVBoxLayout(group)
        outer.setContentsMargins(16, 16, 16, 16)
        outer.setSpacing(12)

        header_card = QFrame()
        header_card.setObjectName(f"groupHeader_{self._group_style_key(title)}")
        header_layout = QHBoxLayout(header_card)
        header_layout.setContentsMargins(14, 12, 14, 12)
        header_layout.setSpacing(10)

        icon = QLabel()
        icon.setObjectName(f"groupTitleIcon_{self._group_style_key(title)}")
        icon.setPixmap(self._group_icon(title).pixmap(14, 14))

        title_block = QVBoxLayout()
        title_block.setContentsMargins(0, 0, 0, 0)
        title_block.setSpacing(2)

        title_label = QLabel(title)
        title_label.setObjectName("groupTitleLabel")
        title_block.addWidget(title_label)

        subtitle_label = QLabel(self._group_subtitle(title))
        subtitle_label.setObjectName("groupSubtitleLabel")
        title_block.addWidget(subtitle_label)

        header_layout.addWidget(icon, 0, Qt.AlignTop)
        header_layout.addLayout(title_block, 1)
        header_layout.addStretch(1)
        outer.addWidget(header_card)

        if self._group_style_key(title) == "parameters":
            strip_fields = list(fields)
            regular_fields = []

            if strip_fields:
                strip_grid = QGridLayout()
                strip_grid.setContentsMargins(0, 0, 0, 0)
                strip_grid.setHorizontalSpacing(12)
                strip_grid.setVerticalSpacing(12)
                row = 0
                column = 0
                for field in strip_fields:
                    widget = self._build_widget(field)
                    self.fields[field["name"]] = (field, widget)
                    strip_grid.addWidget(self._build_parameter_strip(field, widget), row, column, 1, 1)
                    if column == 0:
                        column = 1
                    else:
                        row += 1
                        column = 0
                outer.addLayout(strip_grid)

            fields = regular_fields

        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(14)
        row = 0
        column = 0
        for field in fields:
            row, column = self._add_field_to_grid(grid, row, column, field)
        outer.addLayout(grid)
        return group

    def _build_parameter_strip(self, field, widget):
        frame = QFrame()
        frame.setObjectName("parameterStrip")
        inner = QVBoxLayout(frame)
        inner.setContentsMargins(14, 12, 14, 12)
        inner.setSpacing(8)

        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)
        top_row.setSpacing(8)

        icon = QLabel()
        icon.setObjectName("parameterStripIcon")
        icon.setPixmap(self._field_icon(field).pixmap(14, 14))
        top_row.addWidget(icon, 0, Qt.AlignLeft | Qt.AlignVCenter)

        label = QLabel(field["label"])
        label.setObjectName("parameterStripTitle")
        top_row.addWidget(label, 0, Qt.AlignLeft | Qt.AlignVCenter)

        purpose_text = self._field_purpose_text(field)
        if purpose_text:
            badge = QLabel(purpose_text)
            badge.setObjectName("parameterStripBadge")
            top_row.addWidget(badge, 0, Qt.AlignLeft | Qt.AlignVCenter)

        top_row.addStretch(1)
        inner.addLayout(top_row)
        inner.addWidget(widget)
        return frame

    def _field_icon(self, field):
        name = str(field.get("name") or "").lower()
        if "mode" in name:
            return self.style().standardIcon(QStyle.SP_MediaPlay)
        if "orientation" in name:
            return self.style().standardIcon(QStyle.SP_ArrowUp)
        if "rotation" in name:
            return self.style().standardIcon(QStyle.SP_BrowserReload)
        if "engine" in name:
            return self.style().standardIcon(QStyle.SP_ComputerIcon)
        if "fps" in name or "frame" in name:
            return self.style().standardIcon(QStyle.SP_FileDialogDetailedView)
        if "merge" in name:
            return self.style().standardIcon(QStyle.SP_DialogApplyButton)
        if "delete" in name or "clean" in name:
            return self.style().standardIcon(getattr(QStyle, "SP_TrashIcon", QStyle.SP_DialogDiscardButton))
        if "rename" in name:
            return self.style().standardIcon(QStyle.SP_FileIcon)
        if "deband" in name or "deblock" in name or "shake" in name:
            return self.style().standardIcon(QStyle.SP_MessageBoxWarning)
        return self.style().standardIcon(QStyle.SP_FileDialogInfoView)

    def _segmented_option_icons(self, field):
        name = str(field.get("name") or "").lower()
        if name == "run_mode":
            return {
                "direct_merge": self.style().standardIcon(QStyle.SP_MediaPlay),
                "process_then_merge": self.style().standardIcon(QStyle.SP_FileDialogDetailedView),
            }
        if name == "orientation":
            return {
                "vertical": self.style().standardIcon(QStyle.SP_ArrowUp),
                "horizontal": self.style().standardIcon(QStyle.SP_ArrowRight),
            }
        if name == "rotation":
            return {
                "nothing": self.style().standardIcon(QStyle.SP_DialogResetButton),
                "clockwise": self.style().standardIcon(QStyle.SP_ArrowRight),
                "counterclockwise": self.style().standardIcon(QStyle.SP_ArrowLeft),
                "upside_down": self.style().standardIcon(QStyle.SP_ArrowDown),
            }
        if name == "engine":
            return {
                "ffmpeg": self.style().standardIcon(QStyle.SP_ComputerIcon),
                "opencv": self.style().standardIcon(QStyle.SP_FileDialogContentsView),
            }
        return {}

    def _bool_icons(self, field):
        name = str(field.get("name") or "").lower()
        if "merge" in name:
            return (
                self.style().standardIcon(QStyle.SP_DialogApplyButton),
                self.style().standardIcon(QStyle.SP_DialogCancelButton),
            )
        if "delete" in name:
            return (
                self.style().standardIcon(getattr(QStyle, "SP_TrashIcon", QStyle.SP_DialogDiscardButton)),
                self.style().standardIcon(QStyle.SP_BrowserStop),
            )
        if "rename" in name:
            return (
                self.style().standardIcon(QStyle.SP_FileIcon),
                self.style().standardIcon(QStyle.SP_DialogCancelButton),
            )
        return (
            self.style().standardIcon(QStyle.SP_DialogApplyButton),
            self.style().standardIcon(QStyle.SP_DialogCancelButton),
        )

    def _int_step_config(self, field):
        name = str(field.get("name") or "").lower()
        if name == "video_fps":
            return {"step": 1}
        if "sample_frame" in name:
            return {"step": 50}
        if "batch" in name:
            return {"step": 10}
        return {"step": 1}

    def _group_style_key(self, title):
        mapping = {
            "运行环境": "environment",
            "任务路径": "paths",
            "执行参数": "parameters",
        }
        return mapping.get(title, "default")

    def _group_icon(self, title):
        mapping = {
            "运行环境": QStyle.SP_ComputerIcon,
            "任务路径": QStyle.SP_DirOpenIcon,
            "执行参数": QStyle.SP_FileDialogDetailedView,
        }
        return self.style().standardIcon(mapping.get(title, QStyle.SP_FileIcon))

    def _group_subtitle(self, title):
        mapping = {
            "运行环境": "源码、运行目录与工具链配置",
            "任务路径": "输入、输出与临时目录控制",
            "执行参数": "模式、方向、帧率与处理开关",
        }
        return mapping.get(title, "当前分组配置")

    def _field_span(self, field):
        if field.get("type") in ("dir", "dir_optional", "file", "file_optional", "save_file", "textarea"):
            return 2
        return 1

    def _build_field_card(self, field, widget):
        frame = QFrame()
        frame.setObjectName("fieldCard")
        inner = QVBoxLayout(frame)
        inner.setContentsMargins(12, 10, 12, 10)
        inner.setSpacing(6)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(6)

        label = QLabel(field["label"])
        label.setObjectName("fieldLabel")
        header.addWidget(label, 0, Qt.AlignLeft | Qt.AlignVCenter)

        purpose_text = self._field_purpose_text(field)
        if purpose_text:
            badge = QLabel(purpose_text)
            badge.setObjectName("fieldPurposeBadge")
            header.addWidget(badge, 0, Qt.AlignLeft | Qt.AlignVCenter)

        header.addStretch(1)
        inner.addLayout(header)
        inner.addWidget(widget)
        return frame

    def _field_purpose_text(self, field):
        field_name = str(field.get("name") or "").lower()
        field_type = str(field.get("type") or "")
        if field_type not in PATH_FIELD_TYPES:
            return ""
        if "source" in field_name:
            return "源目录"
        if "target" in field_name:
            return "目标目录"
        if "output" in field_name:
            return "输出目录"
        if "temp" in field_name:
            return "临时目录"
        if "queue" in field_name:
            return "队列目录"
        if "runtime" in field_name:
            return "运行目录"
        if "mapping" in field_name:
            return "映射文件"
        if "excel" in field_name:
            return "报表文件"
        if "ffmpeg" in field_name:
            return "工具文件"
        if "input" in field_name:
            return "输入目录"
        if field_type == "save_file":
            return "输出文件"
        if field_type in {"file", "file_optional"}:
            return "输入文件"
        return "路径"

    def _build_widget(self, field):
        field_type = field.get("type", "text")
        default = field.get("default")

        if field_type in PATH_FIELD_TYPES:
            widget = PathInput(field_type)
            widget.set_context(field.get("label", ""), self._field_purpose_text(field))
            widget.set_value(default)
            widget.pathCommitted.connect(
                lambda value, kind, field_name=field.get("name"), action_id=self.action_meta.get("id"): self.pathRecorded.emit(
                    [{"action_id": action_id, "field_name": field_name, "path_kind": kind, "path_value": value}]
                )
            )
            widget.refreshRequested.connect(
                lambda kind, field_name=field.get("name"): self.pathRefreshRequested.emit(field_name, kind)
            )
            widget.deleteRequested.connect(
                lambda value, kind, field_name=field.get("name"): self.pathDeleteRequested.emit(field_name, kind, value)
            )
            widget.clearAllRequested.connect(
                lambda kind, field_name=field.get("name"): self.pathClearRequested.emit(field_name, kind)
            )
            return widget
        if field_type == "bool":
            on_icon, off_icon = self._bool_icons(field)
            return BoolStateChip(bool(default), on_icon=on_icon, off_icon=off_icon)
        if field_type == "int":
            if self.action_meta.get("id") == "videofusion_merge":
                config = self._int_step_config(field)
                return PanelStepper(
                    minimum=field.get("min", 0),
                    maximum=field.get("max", 999999),
                    step=config.get("step", 1),
                    value=int(default or 0),
                )
            widget = QSpinBox()
            widget.setRange(field.get("min", 0), field.get("max", 999999))
            widget.setValue(int(default or 0))
            return widget
        if field_type == "textarea":
            widget = QTextEdit()
            widget.setMinimumHeight(100)
            if default:
                widget.setPlainText(str(default))
            return widget
        if field_type == "select":
            if self.action_meta.get("id") == "videofusion_merge" and field.get("name") in {"run_mode", "orientation", "rotation", "engine"}:
                widget = SegmentedSelect(field.get("options", []), default=default)
                for value, icon in self._segmented_option_icons(field).items():
                    widget.set_option_icon(value, icon)
                return widget
            widget = QComboBox()
            for option in field.get("options", []):
                widget.addItem(option["label"], option["value"])
            if default is not None:
                index = widget.findData(default)
                if index >= 0:
                    widget.setCurrentIndex(index)
            return widget

        widget = QLineEdit()
        if default is not None:
            widget.setText(str(default))
        return widget

    def collect_params(self):
        params = {}
        for name, (field, widget) in self.fields.items():
            field_type = field.get("type", "text")
            if field_type in PATH_FIELD_TYPES:
                value = widget.value()
            elif field_type == "bool":
                value = widget.isChecked()
            elif field_type == "int":
                value = widget.value()
            elif field_type == "textarea":
                value = widget.toPlainText()
            elif field_type == "select":
                value = widget.currentData()
            else:
                value = widget.text().strip()
            params[name] = value
        return params

    def schedule_preferences_emit(self, *_args):
        if self._suspend_preferences_emit:
            return
        self._preferences_timer.start()

    def _emit_preferences_changed(self):
        if self._suspend_preferences_emit:
            return
        self.preferencesChanged.emit(self.collect_params())

    def apply_params(self, params):
        self._suspend_preferences_emit = True
        for name, value in (params or {}).items():
            pair = self.fields.get(name)
            if pair is None:
                continue
            field, widget = pair
            field_type = field.get("type", "text")
            if field_type in PATH_FIELD_TYPES:
                widget.set_value(value)
            elif field_type == "bool":
                widget.setChecked(bool(value))
            elif field_type == "int":
                try:
                    widget.setValue(int(value))
                except Exception:
                    pass
            elif field_type == "textarea":
                widget.setPlainText("" if value is None else str(value))
            elif field_type == "select":
                index = widget.findData(value)
                if index < 0 and value is not None:
                    index = widget.findText(str(value))
                if index >= 0:
                    widget.setCurrentIndex(index)
            else:
                widget.setText("" if value is None else str(value))
        self._suspend_preferences_emit = False

    def apply_path_history(self, items):
        items = items or []
        for field_name, (field, widget) in self.fields.items():
            field_type = field.get("type", "text")
            if field_type not in PATH_FIELD_TYPES or not hasattr(widget, "set_history"):
                continue
            if field_type in ("dir", "dir_optional"):
                expected_kind = "dir"
            elif field_type == "save_file":
                expected_kind = "save_file"
            else:
                expected_kind = "file"
            values = [
                item.get("path_value", "")
                for item in items
                if item.get("path_kind") == expected_kind and item.get("field_name") == field_name
            ]
            widget.set_history(values)

    def submit(self):
        self.submitted.emit(self.action_meta["id"], self.collect_params(), self.action_meta["title"])

    def set_submitting(self, submitting):
        if hasattr(self, "run_button") and self.run_button is not None:
            self.run_button.setDisabled(submitting)
            self.run_button.setText("执行中..." if submitting else "执行任务")

    def _connect_preference_watchers(self):
        for field, widget in self.fields.values():
            field_type = field.get("type", "text")
            if field_type in PATH_FIELD_TYPES:
                if hasattr(widget, "pathCommitted"):
                    widget.pathCommitted.connect(self.schedule_preferences_emit)
                if hasattr(widget, "deleteRequested"):
                    widget.deleteRequested.connect(lambda *_args: self.schedule_preferences_emit())
                if hasattr(widget, "clearAllRequested"):
                    widget.clearAllRequested.connect(lambda *_args: self.schedule_preferences_emit())
                continue
            if field_type == "bool":
                widget.toggled.connect(self.schedule_preferences_emit)
                continue
            if field_type == "int":
                if hasattr(widget, "valueChanged"):
                    widget.valueChanged.connect(self.schedule_preferences_emit)
                continue
            if field_type == "textarea":
                widget.textChanged.connect(self.schedule_preferences_emit)
                continue
            if field_type == "select":
                if hasattr(widget, "selectionChanged"):
                    widget.selectionChanged.connect(lambda *_args: self.schedule_preferences_emit())
                elif hasattr(widget, "currentIndexChanged"):
                    widget.currentIndexChanged.connect(self.schedule_preferences_emit)
                continue
            if hasattr(widget, "editingFinished"):
                widget.editingFinished.connect(self.schedule_preferences_emit)

    def remove_path_history_value(self, field_name, value, clear_current=False):
        pair = self.fields.get(field_name)
        if pair is None:
            return
        _, widget = pair
        if hasattr(widget, "remove_history_value"):
            widget.remove_history_value(value, clear_current=clear_current)

    def clear_path_history(self, field_name):
        pair = self.fields.get(field_name)
        if pair is None:
            return
        _, widget = pair
        if hasattr(widget, "set_history"):
            widget.set_history([])


路径输入框 = PathInput
信息卡片 = StatusStrip
功能入口卡片 = ActionEntryTile
模块入口卡片 = ModuleEntryCard
动作卡片 = ActionFormCard
