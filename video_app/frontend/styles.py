APP_TITLE = "视频系统工业工作台"
DEFAULT_BASE_URL = "http://127.0.0.1:8766"


APP_STYLESHEET = """
QWidget {
    background: #f5f7fb;
    color: #1f2937;
    font-size: 14px;
}
QMainWindow {
    background: #eef2f7;
}
#headerFrame, #sectionFrame, #contentPanel, #moduleNavFrame, #dialogHeader, #heroPanel, #actionCard, #taskProgressPanel, QGroupBox, QScrollArea {
    background: #ffffff;
}
#headerTitle {
    font-size: 28px;
    font-weight: 700;
    color: #0f172a;
}
#heroTitle {
    font-size: 22px;
    font-weight: 700;
    color: #0f172a;
}
#headerSubtitle, #mutedLabel, #toolbarLabel {
    color: #64748b;
}
#monitorSummary {
    color: #0f172a;
    font-size: 14px;
    font-weight: 700;
}
#monitorMeta {
    color: #64748b;
    font-size: 12px;
}
#sectionTitle {
    font-size: 20px;
    font-weight: 700;
    color: #0f172a;
}
#statusLabel {
    color: #64748b;
    font-size: 12px;
    font-weight: 600;
}
#statusHint {
    color: #94a3b8;
    font-size: 12px;
}
#statusValue {
    color: #0f172a;
    font-size: 22px;
    font-weight: 700;
}
#entryTitle {
    font-size: 14px;
    font-weight: 600;
    color: #334155;
}
#fieldLabel {
    color: #334155;
    font-size: 12px;
    font-weight: 700;
}
#softBadge, #codeBadge {
    padding: 5px 10px;
    border-radius: 11px;
    font-size: 12px;
    font-weight: 600;
}
#softBadge {
    background: #eff6ff;
    color: #1d4ed8;
    border: 1px solid #bfdbfe;
}
#codeBadge {
    background: #f8fafc;
    color: #475569;
    border: 1px solid #e2e8f0;
}
#badgeOnline, #badgeOffline {
    padding: 8px 14px;
    border-radius: 14px;
    font-weight: 700;
}
#badgeOnline {
    background: #ecfdf3;
    color: #15803d;
    border: 1px solid #bbf7d0;
}
#badgeOffline {
    background: #fff7ed;
    color: #c2410c;
    border: 1px solid #fed7aa;
}
QGroupBox, #headerFrame, #sectionFrame, #contentPanel, #moduleNavFrame, #dialogHeader, #heroPanel, #actionCard, #taskProgressPanel {
    border: 1px solid #dbe4f0;
    border-radius: 18px;
}
#statusStrip {
    background: #fbfcfe;
    border: 1px solid #dbe4f0;
    border-radius: 12px;
    min-width: 180px;
}
#entryTile {
    background: #ffffff;
    border: 1px solid #dbe4f0;
    border-radius: 16px;
}
#entryTile:hover {
    background: #f8fbff;
    border: 1px solid #bfdbfe;
}
#entryTile:hover #entryTitle {
    color: #1d4ed8;
}
#entryTile[pressed="true"] {
    background: #eff6ff;
    border: 1px solid #93c5fd;
}
#fieldCard {
    background: #fcfdff;
    border: 1px solid #e5edf6;
    border-radius: 16px;
}
#taskProgressPanel {
    background: #fcfdff;
}
QGroupBox {
    margin-top: 14px;
    padding: 18px 16px 16px 16px;
    font-weight: 700;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 16px;
    padding: 0 8px;
    color: #475569;
    background: #ffffff;
}
QLineEdit, QTextEdit, QComboBox, QSpinBox {
    border: 1px solid #dbe4f0;
    border-radius: 14px;
    padding: 10px 14px;
    background: #fbfdff;
    color: #111827;
    selection-background-color: #dbeafe;
    selection-color: #111827;
    min-height: 18px;
}
QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus {
    border: 1px solid #93c5fd;
    background: #ffffff;
}
QLineEdit:hover, QTextEdit:hover, QComboBox:hover, QSpinBox:hover {
    border: 1px solid #bfdbfe;
    background: #ffffff;
}
QComboBox {
    padding-right: 28px;
}
QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 28px;
    border: none;
    background: transparent;
}
QComboBox::down-arrow {
    image: none;
    width: 0;
    height: 0;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #64748b;
    margin-right: 10px;
}
QComboBox QAbstractItemView {
    background: #ffffff;
    border: 1px solid #dbe4f0;
    border-radius: 12px;
    padding: 6px;
    selection-background-color: #eff6ff;
    selection-color: #1d4ed8;
    outline: none;
}
QScrollArea {
    border: 1px solid #e2e8f0;
    border-radius: 18px;
    background: #ffffff;
}
QScrollBar:vertical {
    background: transparent;
    width: 10px;
    margin: 8px 3px 8px 0;
}
QScrollBar::handle:vertical {
    background: #cbd5e1;
    border-radius: 5px;
    min-height: 28px;
}
QScrollBar::handle:vertical:hover {
    background: #94a3b8;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: transparent;
    height: 0;
}
#pathLineEdit {
    min-height: 18px;
}
QPushButton {
    background: #ffffff;
    color: #334155;
    border: 1px solid #dbe4f0;
    border-radius: 14px;
    padding: 9px 16px;
    font-weight: 700;
    font-size: 13px;
}
QPushButton:hover {
    background: #f8fbff;
    border: 1px solid #bfdbfe;
    color: #1d4ed8;
}
QPushButton:pressed {
    background: #eff6ff;
    border: 1px solid #93c5fd;
    color: #1d4ed8;
}
QPushButton:disabled {
    background: #f8fafc;
    color: #94a3b8;
    border: 1px solid #e2e8f0;
}
QPushButton#primaryButton {
    background: #2563eb;
    border: 1px solid #2563eb;
    color: white;
    padding: 9px 18px;
}
QPushButton#primaryButton:hover {
    background: #1d4ed8;
    border: 1px solid #1d4ed8;
    color: white;
}
QPushButton#primaryButton:pressed {
    background: #1e40af;
    border: 1px solid #1e40af;
    color: white;
}
QPushButton#browseButton {
    background: #f8fafc;
    color: #334155;
    min-width: 88px;
}
QPushButton#utilityButton {
    background: #f8fafc;
    color: #334155;
    min-width: 62px;
    padding: 10px 10px;
}
QPushButton#dangerButton {
    background: #fff7ed;
    color: #c2410c;
    border: 1px solid #fed7aa;
    min-width: 62px;
    padding: 10px 10px;
}
QPushButton#dangerButton:hover {
    background: #ffedd5;
    border: 1px solid #fdba74;
}
QPushButton#utilityIconButton, QPushButton#dangerIconButton {
    min-width: 36px;
    max-width: 36px;
    min-height: 36px;
    max-height: 36px;
    padding: 0;
    border-radius: 18px;
}
QPushButton#utilityIconButton {
    background: #ffffff;
    color: #475569;
    border: 1px solid #e2e8f0;
}
QPushButton#utilityIconButton:hover {
    background: #f8fbff;
    color: #1d4ed8;
    border: 1px solid #bfdbfe;
}
QPushButton#utilityIconButton:pressed {
    background: #eff6ff;
    color: #1d4ed8;
    border: 1px solid #93c5fd;
}
QPushButton#dangerIconButton {
    background: #ffffff;
    color: #b45309;
    border: 1px solid #fde7d3;
}
QPushButton#dangerIconButton:hover {
    background: #fff7ed;
    color: #c2410c;
    border: 1px solid #fdba74;
}
QPushButton#dangerIconButton:pressed {
    background: #ffedd5;
    color: #c2410c;
    border: 1px solid #fb923c;
}
QPushButton#moduleButton {
    min-width: 124px;
    padding: 9px 16px;
    background: #ffffff;
    border: 1px solid #dbe4f0;
    color: #475569;
    border-radius: 14px;
    font-size: 13px;
    font-weight: 600;
}
QPushButton#moduleButton:hover {
    background: #f8fbff;
    border: 1px solid #bfdbfe;
    color: #1d4ed8;
}
QPushButton#moduleButton:checked {
    background: #2563eb;
    border: 1px solid #2563eb;
    color: white;
}
QPushButton#moduleButton:pressed {
    background: #eff6ff;
    border: 1px solid #93c5fd;
    color: #1d4ed8;
}
QCheckBox {
    spacing: 8px;
    color: #334155;
    font-weight: 600;
}
QStatusBar {
    background: #ffffff;
    color: #64748b;
    border-top: 1px solid #dde5ef;
}
"""
