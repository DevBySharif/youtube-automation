"""
styles.py
Global Qt stylesheet for Timestamp Script Analyzer.

Lime Green Dark Palette:
  Primary Background:   #0D0D0D
  Secondary Panels:     #161616
  Cards:                #1E1E1E
  Borders:              #2A2A2A
  Accent Color:         #9EFF00 (Lime Green)
  Accent Hover:         #B8FF3B
  Accent Pressed:       #82D600
  Text Primary:         #F5F5F5
  Secondary Text:       #9E9E9E
  Error:                #FF4D4D
  Warning:              #FFD54F
  Success:              #9EFF00
"""

DARK_STYLESHEET = """
/* ── Base ─────────────────────────────────────────────────── */
QMainWindow, QDialog {
    background-color: #0D0D0D;
    color: #F5F5F5;
}

QWidget {
    background-color: #0D0D0D;
    color: #F5F5F5;
    font-family: "Segoe UI", "Arial", sans-serif;
    font-size: 10pt;
}

/* ── Menu Bar ──────────────────────────────────────────────── */
QMenuBar {
    background-color: #0D0D0D;
    color: #F5F5F5;
    border-bottom: 1px solid #2A2A2A;
    padding: 2px 0;
}
QMenuBar::item {
    padding: 6px 12px;
    border-radius: 6px;
    color: #9E9E9E;
}
QMenuBar::item:selected {
    background-color: #161616;
    color: #9EFF00;
}
QMenu {
    background-color: #161616;
    border: 1px solid #2A2A2A;
    color: #F5F5F5;
    padding: 6px;
    border-radius: 8px;
}
QMenu::item {
    padding: 6px 20px 6px 12px;
    border-radius: 6px;
}
QMenu::item:selected {
    background-color: #9EFF00;
    color: #0D0D0D;
    font-weight: bold;
}
QMenu::separator {
    height: 1px;
    background: #2A2A2A;
    margin: 4px 0;
}

/* ── Splitter ──────────────────────────────────────────────── */
QSplitter::handle {
    background-color: #2A2A2A;
}
QSplitter::handle:horizontal {
    width: 2px;
}
QSplitter::handle:vertical {
    height: 2px;
}

/* ── Cards / Group Panels ─────────────────────────────────── */
QFrame#panel, QWidget#card {
    background-color: #1E1E1E;
    border: 1px solid #2A2A2A;
    border-radius: 12px;
}
QFrame#secondaryPanel {
    background-color: #161616;
    border: 1px solid #2A2A2A;
    border-radius: 12px;
}

/* ── Labels ────────────────────────────────────────────────── */
QLabel {
    background: transparent;
    color: #F5F5F5;
}
QLabel#sectionLabel {
    color: #9EFF00;
    font-size: 8.5pt;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
}
QLabel#subTextLabel {
    color: #9E9E9E;
    font-size: 8.5pt;
}
QLabel#statusLabel {
    color: #9E9E9E;
    font-size: 9.5pt;
    font-weight: 600;
}

/* ── Plain Text Editor ─────────────────────────────────────── */
QPlainTextEdit {
    background-color: #161616;
    border: 1px solid #2A2A2A;
    border-radius: 10px;
    color: #F5F5F5;
    font-family: "Consolas", "Courier New", monospace;
    font-size: 10.5pt;
    line-height: 1.6;
    padding: 12px;
    selection-background-color: #9EFF00;
    selection-color: #0D0D0D;
}
QPlainTextEdit:focus {
    border-color: #9EFF00;
}
QPlainTextEdit[readOnly="true"] {
    background-color: #121212;
    color: #D5D5D5;
}

/* ── Combo Box ─────────────────────────────────────────────── */
QComboBox {
    background-color: #161616;
    border: 1px solid #2A2A2A;
    border-radius: 8px;
    color: #F5F5F5;
    padding: 8px 12px;
    font-size: 10pt;
    min-height: 22px;
}
QComboBox:hover {
    border-color: #9EFF00;
}
QComboBox:focus {
    border-color: #9EFF00;
}
QComboBox::drop-down {
    border: none;
    width: 24px;
}
QComboBox::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid #9EFF00;
    width: 0;
    height: 0;
}
QComboBox QAbstractItemView {
    background-color: #161616;
    border: 1px solid #2A2A2A;
    color: #F5F5F5;
    selection-background-color: #9EFF00;
    selection-color: #0D0D0D;
    outline: none;
    padding: 4px;
    border-radius: 6px;
}

/* ── Slider ────────────────────────────────────────────────── */
QSlider::groove:horizontal {
    background: #2A2A2A;
    height: 6px;
    border-radius: 3px;
}
QSlider::handle:horizontal {
    background: #9EFF00;
    width: 18px;
    height: 18px;
    margin: -6px 0;
    border-radius: 9px;
    border: 2px solid #0D0D0D;
}
QSlider::handle:horizontal:hover {
    background: #B8FF3B;
}
QSlider::sub-page:horizontal {
    background: #9EFF00;
    border-radius: 3px;
}

/* ── Progress Bar ──────────────────────────────────────────── */
QProgressBar {
    background-color: #161616;
    border: none;
    border-radius: 3px;
    height: 6px;
    text-align: center;
    color: transparent;
}
QProgressBar::chunk {
    background-color: #9EFF00;
    border-radius: 3px;
}

/* ── Buttons ───────────────────────────────────────────────── */
QPushButton {
    background-color: #161616;
    border: 1px solid #2A2A2A;
    border-radius: 8px;
    color: #F5F5F5;
    padding: 8px 16px;
    font-size: 10pt;
    font-weight: 500;
}
QPushButton:hover {
    background-color: #242424;
    border-color: #3E3E3E;
}
QPushButton:pressed {
    background-color: #1E1E1E;
}
QPushButton:disabled {
    background-color: #161616;
    color: #555555;
    border-color: #222222;
}

QPushButton#generateButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #B8FF3B, stop:1 #9EFF00);
    border: 1px solid #9EFF00;
    color: #0D0D0D;
    font-size: 11.5pt;
    font-weight: 800;
    padding: 14px 24px;
    border-radius: 10px;
    letter-spacing: 0.5px;
}
QPushButton#generateButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #CEFF66, stop:1 #B8FF3B);
    border-color: #CEFF66;
}
QPushButton#generateButton:pressed {
    background: #82D600;
}
QPushButton#generateButton:disabled {
    background: #222222;
    border-color: #333333;
    color: #666666;
}

QPushButton#previewButton {
    background-color: #161616;
    border: 1px solid #9EFF00;
    color: #9EFF00;
    font-weight: 600;
    border-radius: 8px;
    padding: 8px 14px;
}
QPushButton#previewButton:hover {
    background-color: #1F2C12;
    border-color: #B8FF3B;
    color: #B8FF3B;
}
QPushButton#previewButton:disabled {
    background-color: #161616;
    border-color: #33441A;
    color: #668833;
}

QPushButton#cancelButton {
    background-color: #2D1414;
    border: 1px solid #5A2424;
    color: #FF4D4D;
    font-size: 10pt;
    padding: 8px 16px;
    border-radius: 8px;
}
QPushButton#cancelButton:hover {
    background-color: #3D1A1A;
}

QPushButton#playButton {
    background-color: #9EFF00;
    border: none;
    border-radius: 18px;
    min-width: 36px;
    min-height: 36px;
    max-width: 36px;
    max-height: 36px;
    font-size: 12pt;
    color: #0D0D0D;
    padding: 0;
}
QPushButton#playButton:hover {
    background-color: #B8FF3B;
}

/* ── Tab Widget ────────────────────────────────────────────── */
QTabWidget::pane {
    border: 1px solid #2A2A2A;
    border-radius: 0 10px 10px 10px;
    background-color: #1E1E1E;
    top: -1px;
}
QTabBar::tab {
    background-color: #161616;
    border: 1px solid #2A2A2A;
    border-bottom: none;
    padding: 10px 22px;
    color: #9E9E9E;
    border-top-left-radius: 10px;
    border-top-right-radius: 10px;
    margin-right: 3px;
    font-size: 10pt;
    font-weight: 500;
}
QTabBar::tab:selected {
    background-color: #1E1E1E;
    color: #9EFF00;
    border-bottom: 2px solid #9EFF00;
    font-weight: 600;
}
QTabBar::tab:hover:!selected {
    background-color: #202020;
    color: #F5F5F5;
}

/* ── Scroll Bars ───────────────────────────────────────────── */
QScrollBar:vertical {
    background: transparent;
    width: 8px;
}
QScrollBar::handle:vertical {
    background: #2A2A2A;
    border-radius: 4px;
    min-height: 24px;
}
QScrollBar::handle:vertical:hover {
    background: #3E3E3E;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

/* ── Status Bar ────────────────────────────────────────────── */
QStatusBar {
    background-color: #161616;
    color: #9E9E9E;
    font-size: 8.5pt;
    border-top: 1px solid #2A2A2A;
    padding: 0 8px;
}
"""
