from PyQt5.QtCore import QSize, Qt, pyqtSignal
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
    QSpinBox,
    QStyle,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


PATH_FIELD_TYPES = {"dir", "dir_optional", "file", "file_optional", "save_file"}


class PathInput(QWidget):
    pathCommitted = pyqtSignal(str, str)
    refreshRequested = pyqtSignal(str)
    deleteRequested = pyqtSignal(str, str)
    clearAllRequested = pyqtSignal(str)

    def __init__(self, mode="dir"):
        super().__init__()
        self.mode = mode
        self.combo = QComboBox()
        self.combo.setEditable(True)
        self.combo.setInsertPolicy(QComboBox.NoInsert)
        self.combo.setObjectName("pathHistoryCombo")
        self.combo.lineEdit().setObjectName("pathLineEdit")
        self.button = self._create_icon_button(
            "utilityIconButton",
            self.style().standardIcon(QStyle.SP_DirOpenIcon),
            "浏览并选择路径",
        )
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
        layout.setSpacing(8)
        layout.addWidget(self.combo, 1)
        layout.addWidget(self.button)
        layout.addWidget(self.refresh_button)
        layout.addWidget(self.delete_button)
        layout.addWidget(self.clear_button)
        self.button.clicked.connect(self.browse)
        self.refresh_button.clicked.connect(self.refresh_history)
        self.delete_button.clicked.connect(self.delete_current_history)
        self.clear_button.clicked.connect(self.clear_all_history)
        self.combo.activated.connect(lambda *_: self.commit_current_value())
        self.combo.lineEdit().editingFinished.connect(self.commit_current_value)

    def _create_icon_button(self, object_name, icon, tooltip):
        button = QPushButton("")
        button.setObjectName(object_name)
        button.setFixedSize(36, 36)
        button.setIcon(icon)
        button.setIconSize(QSize(15, 15))
        button.setToolTip(tooltip)
        button.setCursor(Qt.PointingHandCursor)
        shadow = QGraphicsDropShadowEffect(button)
        shadow.setBlurRadius(16)
        shadow.setOffset(0, 3)
        shadow.setColor(QColor(15, 23, 42, 24))
        button.setGraphicsEffect(shadow)
        return button

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
        index = self.combo.findText(text, Qt.MatchFixedString)
        if index >= 0:
            self.combo.removeItem(index)
        self.combo.insertItem(0, text)

    def browse(self):
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
        self.combo.setEditText(current)

    def commit_current_value(self):
        value = self.value()
        if value:
            self._add_candidate(value)
            self.pathCommitted.emit(value, self.history_kind())

    def refresh_history(self):
        self.refreshRequested.emit(self.history_kind())
        self.combo.update()
        self.update()

    def delete_current_history(self):
        value = self.value()
        if value:
            self.deleteRequested.emit(value, self.history_kind())

    def clear_all_history(self):
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
        self.combo.update()
        self.update()


class StatusStrip(QFrame):
    def __init__(self, title, value, hint):
        super().__init__()
        self.setObjectName("statusStrip")
        self.setFixedHeight(72)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 12, 18, 12)
        layout.setSpacing(14)

        text_block = QVBoxLayout()
        text_block.setContentsMargins(0, 0, 0, 0)
        text_block.setSpacing(2)

        title_label = QLabel(title)
        title_label.setObjectName("statusLabel")
        text_block.addWidget(title_label)

        if hint:
            hint_label = QLabel(hint)
            hint_label.setObjectName("statusHint")
            hint_label.setWordWrap(True)
            text_block.addWidget(hint_label)

        value_label = QLabel(str(value))
        value_label.setObjectName("statusValue")

        layout.addLayout(text_block, 1)
        layout.addWidget(value_label, alignment=Qt.AlignRight | Qt.AlignVCenter)


class ActionEntryTile(QFrame):
    opened = pyqtSignal(str)

    def __init__(self, title, description, page_key):
        super().__init__()
        self.page_key = page_key
        self.setObjectName("entryTile")
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(56)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 8, 18, 8)
        layout.setSpacing(0)

        title_label = QLabel(title)
        title_label.setObjectName("entryTitle")
        title_label.setWordWrap(False)
        title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        layout.addWidget(title_label)

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


class ActionFormCard(QFrame):
    submitted = pyqtSignal(str, dict, str)
    pathRecorded = pyqtSignal(list)
    pathRefreshRequested = pyqtSignal(str, str)
    pathDeleteRequested = pyqtSignal(str, str, str)
    pathClearRequested = pyqtSignal(str, str)

    def __init__(self, action_meta, show_description=True):
        super().__init__()
        self.action_meta = action_meta
        self.show_description = show_description
        self.fields = {}
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

        footer = QHBoxLayout()
        self.run_button = QPushButton("执行任务")
        self.run_button.setObjectName("primaryButton")
        self.run_button.setFixedHeight(44)
        self.run_button.setMinimumWidth(132)
        self.run_button.clicked.connect(self.submit)
        footer.addStretch(1)
        footer.addWidget(self.run_button)
        layout.addLayout(footer)

    def _field_span(self, field):
        if field.get("type") in ("dir", "dir_optional", "file", "file_optional", "save_file", "textarea"):
            return 2
        return 1

    def _build_field_card(self, field, widget):
        frame = QFrame()
        frame.setObjectName("fieldCard")
        inner = QVBoxLayout(frame)
        inner.setContentsMargins(14, 12, 14, 12)
        inner.setSpacing(8)

        label = QLabel(field["label"])
        label.setObjectName("fieldLabel")
        inner.addWidget(label)
        inner.addWidget(widget)
        return frame

    def _build_widget(self, field):
        field_type = field.get("type", "text")
        default = field.get("default")

        if field_type in PATH_FIELD_TYPES:
            widget = PathInput(field_type)
            widget.set_value(default)
            widget.pathCommitted.connect(
                lambda value, kind, field_name=field.get("name"): self.pathRecorded.emit(
                    [{"field_name": field_name, "path_kind": kind, "path_value": value}]
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
            widget = QCheckBox()
            widget.setText("启用")
            widget.setChecked(bool(default))
            return widget
        if field_type == "int":
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

    def apply_params(self, params):
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
            values = [item.get("path_value", "") for item in items if item.get("path_kind") == expected_kind]
            widget.set_history(values)

    def submit(self):
        self.submitted.emit(self.action_meta["id"], self.collect_params(), self.action_meta["title"])

    def set_submitting(self, submitting):
        if hasattr(self, "run_button") and self.run_button is not None:
            self.run_button.setDisabled(submitting)
            self.run_button.setText("执行中..." if submitting else "执行任务")

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
动作卡片 = ActionFormCard
