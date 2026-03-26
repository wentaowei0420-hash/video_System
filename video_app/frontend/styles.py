APP_TITLE = "视频系统工业工作台"
DEFAULT_BASE_URL = "http://127.0.0.1:8766"


APP_STYLESHEET = """
QWidget {
    background: #f5f7fb;
    color: #1f2937;
    font-size: 13px;
}
QMainWindow {
    background: #eef2f7;
}
#headerFrame, #sectionFrame, #contentPanel, #moduleNavFrame, #dialogHeader, #heroPanel, #actionCard, #taskProgressPanel, QGroupBox, QScrollArea {
    background: #ffffff;
}
#headerTitle {
    font-size: 24px;
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
#headerToolbar {
    background: #ffffff;
    border: 1px solid #dbe4f0;
    border-radius: 18px;
}
#backendAddressShell {
    background: #f8fbff;
    border: 1px solid #dbeafe;
    border-radius: 16px;
}
#toolbarIconBadge {
    min-width: 30px;
    max-width: 30px;
    min-height: 30px;
    max-height: 30px;
    border-radius: 15px;
    background: #ffffff;
    border: 1px solid #dbe4f0;
    qproperty-alignment: AlignCenter;
}
#toolbarAddressLabel {
    color: #475569;
    font-size: 12px;
    font-weight: 800;
}
#toolbarLineEdit {
    background: #ffffff;
    border: 1px solid #dbe4f0;
    border-radius: 14px;
    padding: 10px 14px;
}
#toolbarLineEdit:focus {
    border: 1px solid #93c5fd;
}
#toolbarLineEdit:hover {
    border: 1px solid #bfdbfe;
}
#monitorSummary {
    color: #0f172a;
    font-size: 14px;
    font-weight: 700;
}
#monitorStatIcon {
    background: transparent;
}
#monitorStatTitle {
    color: #64748b;
    font-size: 12px;
    font-weight: 600;
}
#monitorStatValue {
    color: #0f172a;
    font-size: 18px;
    font-weight: 700;
}
#monitorMeta {
    color: #64748b;
    font-size: 12px;
}
#sectionTitle {
    font-size: 16px;
    font-weight: 700;
    color: #0f172a;
}
#heroIconBadge, #sectionIconBadge, #historyIconBadge, #entryArrow {
    background: transparent;
}
#heroIconBadge, #sectionIconBadge {
    min-width: 34px;
    max-width: 34px;
    min-height: 34px;
    max-height: 34px;
    border-radius: 17px;
    border: 1px solid #dbeafe;
    background: #f8fbff;
    qproperty-alignment: AlignCenter;
}
#historyIconBadge {
    min-width: 24px;
    max-width: 24px;
    min-height: 24px;
    max-height: 24px;
    border-radius: 12px;
    border: 1px solid #e2e8f0;
    background: #ffffff;
    qproperty-alignment: AlignCenter;
}
#templateStatusStrip {
    background: #ffffff;
    border: 1px solid #dbe4f0;
    border-radius: 16px;
}
#templateStatusChip {
    background: #f8fbff;
    border: 1px solid #dbeafe;
    border-radius: 12px;
    min-width: 116px;
}
#templateStatusChipIcon {
    min-width: 24px;
    max-width: 24px;
    min-height: 24px;
    max-height: 24px;
    border-radius: 12px;
    background: #ffffff;
    border: 1px solid #dbe4f0;
    qproperty-alignment: AlignCenter;
}
#templateStatusChipTitle {
    color: #64748b;
    font-size: 11px;
    font-weight: 700;
}
#templateStatusChipValue {
    color: #0f172a;
    font-size: 11px;
    font-weight: 800;
}
#statusLabel {
    color: #0f172a;
    font-size: 14px;
    font-weight: 800;
}
#statusHint {
    color: #64748b;
    font-size: 12px;
    font-weight: 600;
}
#statusMetaBadge {
    padding: 4px 9px;
    border-radius: 10px;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    color: #475569;
    font-size: 11px;
    font-weight: 700;
}
#entryTitle {
    font-size: 15px;
    font-weight: 700;
    color: #1d4ed8;
}
#entryArrow {
    color: #94a3b8;
}
#fieldLabel {
    color: #334155;
    font-size: 11px;
    font-weight: 700;
}
#fieldPurposeBadge {
    padding: 2px 7px;
    border-radius: 8px;
    background: #f1f5f9;
    color: #475569;
    border: 1px solid #e2e8f0;
    font-size: 10px;
    font-weight: 700;
}
#softBadge, #codeBadge {
    padding: 3px 7px;
    border-radius: 9px;
    font-size: 10px;
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
    padding: 6px 12px;
    border-radius: 12px;
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
    border-radius: 16px;
}
#moduleNavFrame {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
}
#statusStrip {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ffffff, stop:1 #f8fbff);
    border: 1px solid #dbe4f0;
    border-radius: 16px;
    min-width: 180px;
}
#monitorStatChip_info, #monitorStatChip_ok, #monitorStatChip_issue {
    border-radius: 16px;
    border: 1px solid transparent;
    min-width: 112px;
}
#monitorStatChip_info {
    background: #f8fbff;
    border-color: #dbeafe;
}
#monitorStatChip_ok {
    background: #f1fcf5;
    border-color: #ccefd8;
}
#monitorStatChip_issue {
    background: #fff8eb;
    border-color: #fde68a;
}
#statusIconShell_ok, #statusIconShell_missing, #statusIconShell_error, #statusIconShell_info {
    border-radius: 20px;
    border: 1px solid transparent;
}
#statusIconShell_ok {
    background: #effcf3;
    border-color: #bbf7d0;
}
#statusIconShell_missing {
    background: #fff8eb;
    border-color: #fde68a;
}
#statusIconShell_error {
    background: #fff1f2;
    border-color: #fecdd3;
}
#statusIconShell_info {
    background: #eff6ff;
    border-color: #bfdbfe;
}
#statusValueBadge_ok, #statusValueBadge_missing, #statusValueBadge_error, #statusValueBadge_info {
    min-width: 54px;
    padding: 5px 10px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 700;
}
#statusValueBadge_ok {
    background: #effcf3;
    color: #15803d;
    border: 1px solid #bbf7d0;
}
#statusValueBadge_missing {
    background: #fff8eb;
    color: #b45309;
    border: 1px solid #fde68a;
}
#statusValueBadge_error {
    background: #fff1f2;
    color: #be123c;
    border: 1px solid #fecdd3;
}
#statusValueBadge_info {
    background: #eff6ff;
    color: #1d4ed8;
    border: 1px solid #bfdbfe;
}
#entryTile {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ffffff, stop:1 #f8fbff);
    border: 1px solid #dbe4f0;
    border-radius: 16px;
}
#entryTile:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ffffff, stop:1 #eff6ff);
    border: 1px solid #bfdbfe;
}
#entryTile:hover #entryTitle {
    color: #1d4ed8;
}
#entryTile[pressed="true"] {
    background: #eff6ff;
    border: 1px solid #93c5fd;
}
#entryIcon {
    min-width: 34px;
    max-width: 34px;
    min-height: 34px;
    max-height: 34px;
    border-radius: 17px;
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    qproperty-alignment: AlignCenter;
}
#moduleEntryCard {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ffffff, stop:1 #f8fbff);
    border: 1px solid #dbe4f0;
    border-radius: 16px;
}
#moduleEntryCard:hover {
    border: 1px solid #bfdbfe;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ffffff, stop:1 #eff6ff);
}
#moduleEntryIcon {
    min-width: 38px;
    max-width: 38px;
    min-height: 38px;
    max-height: 38px;
    border-radius: 19px;
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    qproperty-alignment: AlignCenter;
}
#moduleEntryTitle {
    color: #0f172a;
    font-size: 15px;
    font-weight: 800;
}
#moduleEntryDesc {
    color: #64748b;
    font-size: 11px;
    font-weight: 600;
}
#moduleEntryStatus {
    padding: 5px 10px;
    border-radius: 10px;
    background: #ecfdf3;
    border: 1px solid #bbf7d0;
    color: #15803d;
    font-size: 11px;
    font-weight: 800;
}
#moduleEntryMetaBadge {
    padding: 4px 9px;
    border-radius: 10px;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    color: #475569;
    font-size: 11px;
    font-weight: 700;
}
#moduleEntryActionPill {
    padding: 4px 9px;
    border-radius: 10px;
    background: #eef6ff;
    border: 1px solid #dbeafe;
    color: #1d4ed8;
    font-size: 11px;
    font-weight: 700;
}
QPushButton#moduleEntryOpenButton {
    background: #ffffff;
    border: 1px solid #dbe4f0;
    border-radius: 12px;
    padding: 8px 14px;
    color: #334155;
    font-size: 12px;
    font-weight: 800;
}
QPushButton#moduleEntryOpenButton:hover {
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    color: #1d4ed8;
}
QPushButton#moduleEntryOpenButton:pressed {
    background: #dbeafe;
    border: 1px solid #93c5fd;
    color: #1d4ed8;
}
#entryStatus {
    padding: 5px 10px;
    border-radius: 10px;
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    color: #1d4ed8;
    font-size: 11px;
    font-weight: 800;
}
#entryDesc {
    color: #64748b;
    font-size: 13px;
    font-weight: 600;
}
#entryMetaBadge {
    padding: 4px 9px;
    border-radius: 10px;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    color: #475569;
    font-size: 11px;
    font-weight: 700;
}
QPushButton#entryOpenButton {
    background: #ffffff;
    border: 1px solid #dbe4f0;
    border-radius: 12px;
    padding: 7px 12px;
    color: #334155;
    font-size: 12px;
    font-weight: 800;
}
QPushButton#entryOpenButton:hover {
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    color: #1d4ed8;
}
QPushButton#entryOpenButton:pressed {
    background: #dbeafe;
    border: 1px solid #93c5fd;
    color: #1d4ed8;
}
#historyRecordCard {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ffffff, stop:1 #f8fbff);
    border: 1px solid #dbe4f0;
    border-radius: 16px;
}
#historyMetaBadge {
    padding: 4px 9px;
    border-radius: 10px;
    background: #eef6ff;
    border: 1px solid #dbeafe;
    color: #1d4ed8;
    font-size: 11px;
    font-weight: 700;
}
#historyMetaText {
    color: #64748b;
    font-size: 12px;
    font-weight: 600;
}
#historyMessage {
    color: #334155;
    font-size: 13px;
    font-weight: 600;
}
#fieldCard {
    background: #fcfdff;
    border: 1px solid #e5edf6;
    border-radius: 14px;
}
#fieldGroupCard {
    background: #f8fbff;
    border: 1px solid #d7e5f5;
    border-radius: 16px;
}
#vfColumnPanel {
    background: transparent;
    border: none;
}
#configSummaryPanel {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #f8fbff, stop:1 #ffffff);
    border: 1px solid #d7e5f5;
    border-radius: 16px;
}
#summaryPanelIcon {
    min-width: 30px;
    max-width: 30px;
    min-height: 30px;
    max-height: 30px;
    border-radius: 15px;
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    qproperty-alignment: AlignCenter;
}
#summaryPanelTitle {
    color: #0f172a;
    font-size: 13px;
    font-weight: 800;
}
#summaryPanelSubtitle {
    color: #64748b;
    font-size: 12px;
    font-weight: 600;
}
#summaryPanelBadge {
    padding: 4px 10px;
    border-radius: 10px;
    background: #ecfdf3;
    border: 1px solid #bbf7d0;
    color: #15803d;
    font-size: 11px;
    font-weight: 800;
}
#summaryChip {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    min-width: 120px;
}
#summaryChipIcon {
    min-width: 24px;
    max-width: 24px;
    min-height: 24px;
    max-height: 24px;
    border-radius: 12px;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    qproperty-alignment: AlignCenter;
}
#summaryChipLabel {
    color: #64748b;
    font-size: 11px;
    font-weight: 700;
}
#summaryChipValue {
    color: #0f172a;
    font-size: 13px;
    font-weight: 800;
}
#parameterStrip {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
}
#parameterStripTitle {
    color: #0f172a;
    font-size: 12px;
    font-weight: 700;
}
#parameterStripIcon {
    min-width: 24px;
    max-width: 24px;
    min-height: 24px;
    max-height: 24px;
    border-radius: 12px;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    qproperty-alignment: AlignCenter;
}
#parameterStripBadge {
    padding: 3px 8px;
    border-radius: 9px;
    background: #eff6ff;
    color: #1d4ed8;
    border: 1px solid #bfdbfe;
    font-size: 11px;
    font-weight: 700;
}
QPushButton#boolStateChip {
    min-height: 40px;
    padding: 8px 14px;
    border-radius: 14px;
    font-size: 12px;
    font-weight: 800;
}
QPushButton#boolStateChip[state="off"] {
    background: #f8fafc;
    color: #64748b;
    border: 1px solid #dbe4f0;
}
QPushButton#boolStateChip[state="off"]:hover {
    background: #eff6ff;
    color: #334155;
    border: 1px solid #bfdbfe;
}
QPushButton#boolStateChip[state="on"] {
    background: #ecfdf3;
    color: #15803d;
    border: 1px solid #bbf7d0;
}
QPushButton#boolStateChip[state="on"]:hover {
    background: #dcfce7;
    color: #166534;
    border: 1px solid #86efac;
}
QPushButton#segmentButton {
    min-height: 40px;
    padding: 8px 12px;
    border-radius: 14px;
    background: #f8fafc;
    color: #475569;
    border: 1px solid #dbe4f0;
    font-size: 12px;
    font-weight: 800;
}
QPushButton#segmentButton:hover {
    background: #eff6ff;
    color: #1d4ed8;
    border: 1px solid #bfdbfe;
}
QPushButton#segmentButton:checked {
    background: #2563eb;
    color: #ffffff;
    border: 1px solid #2563eb;
}
QPushButton#segmentButton:pressed {
    background: #1d4ed8;
    color: #ffffff;
    border: 1px solid #1d4ed8;
}
QPushButton#stepperButton {
    min-width: 40px;
    max-width: 40px;
    min-height: 40px;
    max-height: 40px;
    padding: 0;
    border-radius: 14px;
    background: #f8fafc;
    color: #475569;
    border: 1px solid #dbe4f0;
}
QPushButton#stepperButton:hover {
    background: #eff6ff;
    color: #1d4ed8;
    border: 1px solid #bfdbfe;
}
QLineEdit#stepperValue {
    min-height: 40px;
    border-radius: 14px;
    background: #ffffff;
    border: 1px solid #dbe4f0;
    color: #0f172a;
    font-size: 13px;
    font-weight: 800;
}
#groupHeader_environment, #groupHeader_paths, #groupHeader_parameters {
    border-radius: 14px;
    border: 1px solid transparent;
}
#groupHeader_environment {
    background: #eef6ff;
    border-color: #dbeafe;
}
#groupHeader_paths {
    background: #eefbf3;
    border-color: #ccefd8;
}
#groupHeader_parameters {
    background: #fff8eb;
    border-color: #fde68a;
}
#groupTitleLabel {
    color: #0f172a;
    font-size: 14px;
    font-weight: 700;
}
#groupSubtitleLabel {
    color: #64748b;
    font-size: 12px;
    font-weight: 600;
}
#groupTitleIcon_environment, #groupTitleIcon_paths, #groupTitleIcon_parameters, #groupTitleIcon {
    min-width: 24px;
    max-width: 24px;
    min-height: 24px;
    max-height: 24px;
    border-radius: 12px;
    qproperty-alignment: AlignCenter;
}
#groupTitleIcon_environment {
    background: #ffffff;
    border: 1px solid #bfdbfe;
}
#groupTitleIcon_paths {
    background: #ffffff;
    border: 1px solid #bbf7d0;
}
#groupTitleIcon_parameters {
    background: #ffffff;
    border: 1px solid #fde68a;
}
#taskProgressPanel {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #fcfdff, stop:1 #ffffff);
    border: 1px solid #dbe4f0;
    border-radius: 18px;
}
#taskProgressPanel[state="running"] {
    border: 1px solid #bbf7d0;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #f0fdf4, stop:1 #ffffff);
}
#taskProgressPanel[state="success"] {
    border: 1px solid #86efac;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ecfdf5, stop:1 #ffffff);
}
#taskProgressPanel[state="failed"] {
    border: 1px solid #fca5a5;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #fef2f2, stop:1 #ffffff);
}
#taskConsoleIcon {
    min-width: 34px;
    max-width: 34px;
    min-height: 34px;
    max-height: 34px;
    border-radius: 17px;
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    qproperty-alignment: AlignCenter;
}
#taskConsoleTitle {
    color: #0f172a;
    font-size: 14px;
    font-weight: 800;
}
#taskConsoleSubtitle {
    color: #64748b;
    font-size: 12px;
    font-weight: 600;
}
#taskMetaStrip {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
}
#taskMetaLabel {
    color: #64748b;
    font-size: 11px;
    font-weight: 700;
}
#taskMetaValue {
    color: #0f172a;
    font-size: 12px;
    font-weight: 800;
}
#taskMetaDivider {
    background: #e2e8f0;
    border: none;
}
#taskIdBadge {
    padding: 5px 10px;
    border-radius: 10px;
    background: #f8fafc;
    border: 1px solid #dbe4f0;
    color: #475569;
    font-size: 11px;
    font-weight: 800;
}
#taskStateBadge_idle, #taskStateBadge_running, #taskStateBadge_success, #taskStateBadge_failed {
    padding: 5px 11px;
    border-radius: 10px;
    font-size: 11px;
    font-weight: 800;
}
#taskStateBadge_idle {
    background: #f8fafc;
    border: 1px solid #dbe4f0;
    color: #475569;
}
#taskStateBadge_running {
    background: #effff5;
    border: 1px solid #86efac;
    color: #15803d;
}
#taskStateBadge_success {
    background: #ecfdf3;
    border: 1px solid #86efac;
    color: #166534;
}
#taskStateBadge_failed {
    background: #fef2f2;
    border: 1px solid #fca5a5;
    color: #b91c1c;
}
QGroupBox {
    margin-top: 10px;
    padding: 14px 12px 12px 12px;
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
#tagChip {
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    border-radius: 12px;
}
#tagChipLabel {
    color: #1d4ed8;
    font-size: 12px;
    font-weight: 700;
}
QPushButton#tagChipRemoveButton {
    background: #ffffff;
    border: 1px solid #dbeafe;
    border-radius: 11px;
    color: #475569;
    padding: 0;
    font-size: 12px;
    font-weight: 800;
}
QPushButton#tagChipRemoveButton:hover {
    background: #dbeafe;
    border: 1px solid #93c5fd;
    color: #1d4ed8;
}
QPushButton#tagChipRemoveButton:pressed {
    background: #bfdbfe;
    border: 1px solid #60a5fa;
    color: #1d4ed8;
}
QPushButton#tagRecentChip {
    background: #ffffff;
    border: 1px solid #dbeafe;
    border-radius: 12px;
    color: #1d4ed8;
    padding: 6px 10px;
    font-size: 12px;
    font-weight: 700;
}
QPushButton#tagRecentChip:hover {
    background: #eff6ff;
    border: 1px solid #93c5fd;
    color: #1d4ed8;
}
QPushButton#tagRecentChip:pressed {
    background: #dbeafe;
    border: 1px solid #60a5fa;
    color: #1d4ed8;
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
    min-height: 14px;
}
QPushButton {
    background: #ffffff;
    color: #334155;
    border: 1px solid #dbe4f0;
    border-radius: 12px;
    padding: 8px 14px;
    font-weight: 700;
    font-size: 12px;
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
QPushButton#toolbarPrimaryButton {
    background: #2563eb;
    border: 1px solid #2563eb;
    color: white;
    border-radius: 12px;
    padding: 8px 16px;
    font-size: 12px;
    font-weight: 800;
}
QPushButton#toolbarPrimaryButton:hover {
    background: #1d4ed8;
    border: 1px solid #1d4ed8;
    color: white;
}
QPushButton#toolbarPrimaryButton:pressed {
    background: #1e40af;
    border: 1px solid #1e40af;
    color: white;
}
QPushButton#toolbarActionButton {
    background: #ffffff;
    border: 1px solid #dbe4f0;
    color: #334155;
    border-radius: 12px;
    padding: 8px 16px;
    font-size: 12px;
    font-weight: 800;
}
QPushButton#toolbarActionButton:hover {
    background: #f8fbff;
    border: 1px solid #bfdbfe;
    color: #1d4ed8;
}
QPushButton#toolbarActionButton:pressed {
    background: #eff6ff;
    border: 1px solid #93c5fd;
    color: #1d4ed8;
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
QPushButton#toggleIconButton {
    background: #f8fafc;
    color: #475569;
    border: 1px solid #dbe4f0;
}
QPushButton#toggleIconButton:hover {
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    color: #1d4ed8;
}
QPushButton#toggleIconButton:checked {
    background: #dbeafe;
    border: 1px solid #93c5fd;
    color: #1d4ed8;
}
QPushButton#toggleIconButton:disabled {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    color: #94a3b8;
}
QPushButton#browseButton {
    background: #f8fafc;
    color: #334155;
    min-width: 88px;
}
QPushButton#utilityButton {
    background: #f8fafc;
    color: #334155;
    min-width: 52px;
    padding: 7px 7px;
}
QPushButton#dangerButton {
    background: #fff7ed;
    color: #c2410c;
    border: 1px solid #fed7aa;
    min-width: 52px;
    padding: 7px 7px;
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
    min-width: 132px;
    padding: 8px 14px;
    background: transparent;
    border: 1px solid transparent;
    border-bottom: 3px solid transparent;
    color: #64748b;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 800;
    text-align: left;
}
QPushButton#moduleButton:hover {
    background: #ffffff;
    border: 1px solid #dbeafe;
    border-bottom: 3px solid #bfdbfe;
    color: #1d4ed8;
}
QPushButton#moduleButton:checked {
    background: #ffffff;
    border: 1px solid #dbeafe;
    border-bottom: 3px solid #2563eb;
    color: #0f172a;
}
QPushButton#moduleButton:pressed {
    background: #eff6ff;
    border: 1px solid #93c5fd;
    border-bottom: 3px solid #1d4ed8;
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

/* strict desktop tool overrides */
QWidget {
    background: #f3f3f3;
    color: #222222;
    font-size: 12px;
}
QMainWindow {
    background: #efefef;
}
#headerFrame, #sectionFrame, #contentPanel, #moduleNavFrame, #dialogHeader, #heroPanel, #actionCard, #taskProgressPanel, QGroupBox, QScrollArea, #templateStatusStrip, #fieldGroupCard, #configSummaryPanel, #historyRecordCard, #entryTile, #moduleEntryCard, #statusStrip {
    background: #ffffff;
    border: 1px solid #cfcfcf;
    border-radius: 4px;
}
#headerToolbar, #backendAddressShell {
    background: #ffffff;
    border: 1px solid #cfcfcf;
    border-radius: 4px;
}
#moduleNavFrame {
    background: #f7f7f7;
}
#headerTitle, #heroTitle, #sectionTitle, #moduleEntryTitle, #entryTitle, #summaryPanelTitle, #groupTitleLabel {
    color: #222222;
    font-weight: 700;
}
#headerTitle {
    font-size: 18px;
}
#heroTitle {
    font-size: 17px;
}
#sectionTitle {
    font-size: 14px;
}
#headerSubtitle, #mutedLabel, #toolbarLabel, #moduleEntryDesc, #entryDesc, #summaryPanelSubtitle, #groupSubtitleLabel, #historyMetaText, #monitorMeta, #monitorStatTitle {
    color: #666666;
}
#heroIconBadge, #sectionIconBadge, #historyIconBadge, #toolbarIconBadge, #templateStatusChipIcon, #summaryPanelIcon, #summaryChipIcon, #entryIcon, #moduleEntryIcon {
    background: #f4f4f4;
    border: 1px solid #d6d6d6;
    border-radius: 3px;
}
#softBadge, #codeBadge, #historyMetaBadge, #moduleEntryMetaBadge, #moduleEntryActionPill, #entryMetaBadge, #statusMetaBadge, #fieldPurposeBadge, #summaryPanelBadge {
    background: #f4f4f4;
    border: 1px solid #d6d6d6;
    color: #444444;
    border-radius: 3px;
    padding: 2px 6px;
}
#badgeOnline, #badgeOffline, #entryStatus, #moduleEntryStatus {
    border-radius: 3px;
    padding: 3px 8px;
    font-weight: 700;
}
#badgeOnline, #moduleEntryStatus {
    background: #edf7ed;
    color: #256c2f;
    border: 1px solid #b9d9bc;
}
#badgeOffline, #entryStatus {
    background: #f8f8f8;
    color: #555555;
    border: 1px solid #d4d4d4;
}
QLineEdit, QTextEdit, QComboBox, QSpinBox {
    background: #ffffff;
    border: 1px solid #bfbfbf;
    border-radius: 2px;
    padding: 6px 8px;
    min-height: 18px;
    color: #222222;
}
QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus {
    border: 1px solid #7da2ce;
    background: #ffffff;
}
QLineEdit:hover, QTextEdit:hover, QComboBox:hover, QSpinBox:hover {
    border: 1px solid #a9a9a9;
    background: #ffffff;
}
QComboBox::drop-down {
    width: 22px;
}
QPushButton {
    background: #f6f6f6;
    color: #222222;
    border: 1px solid #bfbfbf;
    border-radius: 2px;
    padding: 5px 12px;
    font-size: 12px;
    font-weight: 500;
}
QPushButton:hover {
    background: #ffffff;
    border: 1px solid #9f9f9f;
    color: #111111;
}
QPushButton:pressed {
    background: #e9e9e9;
    border: 1px solid #8d8d8d;
}
QPushButton#primaryButton, QPushButton#toolbarPrimaryButton {
    background: #f6f6f6;
    color: #222222;
    border: 1px solid #9a9a9a;
}
QPushButton#primaryButton:hover, QPushButton#toolbarPrimaryButton:hover {
    background: #ffffff;
    color: #111111;
    border: 1px solid #7f7f7f;
}
QPushButton#primaryButton:pressed, QPushButton#toolbarPrimaryButton:pressed {
    background: #e9e9e9;
    color: #111111;
    border: 1px solid #6f6f6f;
}
QPushButton#toolbarActionButton, QPushButton#moduleEntryOpenButton, QPushButton#entryOpenButton, QPushButton#browseButton {
    background: #f6f6f6;
    border: 1px solid #bfbfbf;
    border-radius: 2px;
    color: #222222;
}
QPushButton#moduleButton {
    min-width: 118px;
    background: transparent;
    border: 1px solid transparent;
    border-bottom: 2px solid transparent;
    border-radius: 0;
    color: #444444;
    padding: 6px 12px;
    font-size: 12px;
    font-weight: 600;
}
QPushButton#moduleButton:hover {
    background: #f6f6f6;
    border: 1px solid #d0d0d0;
    border-bottom: 2px solid #b0b0b0;
    color: #222222;
}
QPushButton#moduleButton:checked {
    background: #ffffff;
    border: 1px solid #c8c8c8;
    border-bottom: 2px solid #7d7d7d;
    color: #111111;
}
#entryTile:hover, #moduleEntryCard:hover, #historyRecordCard:hover, #fieldCard:hover {
    background: #fcfcfc;
    border: 1px solid #c5c5c5;
}
#templateStatusChip, #summaryChip, #parameterStrip, #fieldCard {
    background: #fafafa;
    border: 1px solid #d6d6d6;
    border-radius: 3px;
}
QScrollArea {
    border-radius: 3px;
}
QGroupBox {
    margin-top: 8px;
    padding: 10px 10px 10px 10px;
    font-weight: 700;
}
QGroupBox::title {
    color: #444444;
    background: #ffffff;
}
QStatusBar {
    background: #f7f7f7;
    color: #555555;
    border-top: 1px solid #cccccc;
}

/* compact layout overrides */
QWidget {
    font-size: 11px;
}
#headerTitle {
    font-size: 15px;
}
#heroTitle {
    font-size: 14px;
}
#sectionTitle, #moduleEntryTitle, #entryTitle {
    font-size: 12px;
}
#headerFrame, #sectionFrame, #contentPanel, #moduleNavFrame, #dialogHeader, #heroPanel, #actionCard, #taskProgressPanel, QGroupBox, QScrollArea, #templateStatusStrip, #fieldGroupCard, #configSummaryPanel, #historyRecordCard, #entryTile, #moduleEntryCard, #statusStrip {
    border-radius: 2px;
}
#heroIconBadge, #sectionIconBadge, #historyIconBadge, #toolbarIconBadge, #templateStatusChipIcon, #summaryPanelIcon, #summaryChipIcon, #entryIcon, #moduleEntryIcon {
    min-width: 22px;
    max-width: 22px;
    min-height: 22px;
    max-height: 22px;
    border-radius: 2px;
}
#toolbarLineEdit {
    padding: 4px 6px;
    border-radius: 2px;
}
QLineEdit, QTextEdit, QComboBox, QSpinBox {
    padding: 4px 6px;
    min-height: 16px;
    border-radius: 2px;
}
QPushButton {
    padding: 4px 10px;
    font-size: 11px;
    border-radius: 2px;
}
QPushButton#primaryButton, QPushButton#toolbarPrimaryButton, QPushButton#toolbarActionButton, QPushButton#moduleEntryOpenButton, QPushButton#entryOpenButton, QPushButton#browseButton {
    padding: 4px 10px;
    border-radius: 2px;
}
QPushButton#moduleButton {
    min-width: 92px;
    padding: 4px 8px;
    font-size: 11px;
}
#softBadge, #codeBadge, #historyMetaBadge, #moduleEntryMetaBadge, #moduleEntryActionPill, #entryMetaBadge, #statusMetaBadge, #fieldPurposeBadge, #summaryPanelBadge, #entryStatus, #moduleEntryStatus, #badgeOnline, #badgeOffline {
    font-size: 10px;
    padding: 2px 5px;
    border-radius: 2px;
}
#templateStatusChip, #summaryChip, #parameterStrip, #fieldCard {
    border-radius: 2px;
}
QGroupBox {
    margin-top: 5px;
    padding: 6px 6px 6px 6px;
}
QGroupBox::title {
    padding: 0 4px;
}
"""
