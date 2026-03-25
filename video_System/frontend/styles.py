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
#headerFrame, #sectionFrame, #contentPanel, #moduleNavFrame, #dialogHeader, #heroPanel, #actionCard, QGroupBox, QScrollArea {
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
    font-size: 13px;
    font-weight: 600;
    color: #0f172a;
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
QGroupBox, #headerFrame, #sectionFrame, #contentPanel, #moduleNavFrame, #dialogHeader, #heroPanel, #actionCard {
    border: 1px solid #dde5ef;
    border-radius: 16px;
}
#statusStrip {
    background: #fbfcfe;
    border: 1px solid #dbe4f0;
    border-radius: 12px;
    min-width: 180px;
}
#entryTile {
    background: #ffffff;
    border: 1px solid #dde5ef;
    border-radius: 12px;
}
#entryTile:hover {
    border: 1px solid #93c5fd;
    background: #f8fbff;
}
#fieldCard {
    background: #fafcff;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
}
QGroupBox {
    margin-top: 12px;
    padding: 14px;
    font-weight: 700;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 14px;
    padding: 0 6px;
    color: #334155;
}
QLineEdit, QTextEdit, QComboBox, QSpinBox {
    border: 1px solid #d5deea;
    border-radius: 12px;
    padding: 10px 12px;
    background: #ffffff;
    color: #111827;
    selection-background-color: #dbeafe;
    selection-color: #111827;
    min-height: 18px;
}
QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus {
    border: 1px solid #60a5fa;
    background: #ffffff;
}
#pathLineEdit {
    min-height: 18px;
}
QPushButton {
    background: #ffffff;
    color: #374151;
    border: 1px solid #d5deea;
    border-radius: 12px;
    padding: 10px 16px;
    font-weight: 700;
}
QPushButton:hover {
    background: #f8fafc;
    border: 1px solid #c6d4e3;
}
QPushButton#primaryButton {
    background: #2563eb;
    border: 1px solid #2563eb;
    color: white;
}
QPushButton#primaryButton:hover {
    background: #1d4ed8;
}
QPushButton#browseButton {
    background: #f8fafc;
    color: #334155;
    min-width: 88px;
}
QPushButton#moduleButton {
    min-width: 124px;
    padding: 8px 14px;
    background: #f8fafc;
    border: 1px solid #dbe4f0;
    color: #475569;
    border-radius: 12px;
    font-size: 13px;
    font-weight: 600;
}
QPushButton#moduleButton:hover {
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    color: #1d4ed8;
}
QPushButton#moduleButton:checked {
    background: #2563eb;
    border: 1px solid #2563eb;
    color: white;
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
