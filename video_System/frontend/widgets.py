from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class 路径输入框(QWidget):
    def __init__(self, mode="dir"):
        super().__init__()
        self.mode = mode
        self.line_edit = QLineEdit()
        self.button = QPushButton("浏览")
        self.line_edit.setObjectName("pathLineEdit")
        self.button.setObjectName("browseButton")
        self.button.setFixedWidth(88)
        self.button.setFixedHeight(42)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        layout.addWidget(self.line_edit, 1)
        layout.addWidget(self.button)
        self.button.clicked.connect(self.browse)

    def browse(self):
        current = self.value()
        if self.mode in ("dir", "dir_optional"):
            path = QFileDialog.getExistingDirectory(self, "选择目录", current)
        elif self.mode == "save_file":
            path, _ = QFileDialog.getSaveFileName(self, "选择输出文件", current, "Excel Files (*.xlsx);;All Files (*)")
        else:
            path, _ = QFileDialog.getOpenFileName(self, "选择文件", current)
        if path:
            self.line_edit.setText(path)

    def value(self):
        return self.line_edit.text().strip()

    def set_value(self, value):
        self.line_edit.setText("" if value is None else str(value))


class 信息卡片(QFrame):
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


class 功能入口卡片(QFrame):
    opened = pyqtSignal(str)

    def __init__(self, title, description, page_key):
        super().__init__()
        self.page_key = page_key
        self.setObjectName("entryTile")
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(50)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 6, 14, 6)
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
            self._emit_opened()
        super().mousePressEvent(event)


class 动作卡片(QFrame):
    submitted = pyqtSignal(str, dict, str)

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
        run_button = QPushButton("执行任务")
        run_button.setObjectName("primaryButton")
        run_button.setFixedHeight(44)
        run_button.setMinimumWidth(132)
        run_button.clicked.connect(self.submit)
        footer.addStretch(1)
        footer.addWidget(run_button)
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

        if field_type in ("dir", "dir_optional", "file", "file_optional", "save_file"):
            widget = 路径输入框(field_type)
            widget.set_value(default)
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
            if field_type in ("dir", "dir_optional", "file", "file_optional", "save_file"):
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
            if field_type in ("dir", "dir_optional", "file", "file_optional", "save_file"):
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

    def submit(self):
        self.submitted.emit(self.action_meta["id"], self.collect_params(), self.action_meta["title"])


PathInput = None
StatusStrip = None
ActionEntryTile = None
ActionFormCard = None

for _name, _value in list(globals().items()):
    if not isinstance(_value, type):
        continue
    if issubclass(_value, QWidget) and not issubclass(_value, QFrame) and _value is not QWidget:
        PathInput = _value
    elif issubclass(_value, QFrame) and getattr(_value, "submitted", None) is not None:
        ActionFormCard = _value
    elif issubclass(_value, QFrame) and getattr(_value, "opened", None) is not None:
        ActionEntryTile = _value
    elif issubclass(_value, QFrame) and _value is not QFrame:
        StatusStrip = StatusStrip or _value
