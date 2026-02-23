"""
SentinelPi — Touchscreen Stylesheet
Tactical field device aesthetic. 800×480 optimized.
Large tap targets, high contrast, clear hierarchy.
"""

STYLESHEET = """
/* ── Root ─────────────────────────────────────────────────────── */
* {
    font-family: 'DejaVu Sans Mono', 'Courier New', monospace;
    color: #e0e0e0;
    outline: none;
    border: none;
}

QMainWindow, QWidget#root {
    background: #0c0c0c;
}

/* ── Status Bar ────────────────────────────────────────────────── */
QWidget#status_bar {
    background: #0a0a0a;
    border-bottom: 1px solid #1a1a1a;
}

QLabel#sb_brand {
    font-size: 15px;
    font-weight: bold;
    letter-spacing: 2px;
    color: #ffffff;
}

QWidget#sb_pill {
    background: #141414;
    border: 1px solid #222;
    border-radius: 3px;
}

QLabel#sb_pill_label {
    font-size: 9px;
    color: #444;
    letter-spacing: 2px;
}

QLabel#sb_pill_value {
    font-size: 11px;
    color: #00ff88;
    font-weight: bold;
}

QLabel#sb_battery {
    font-size: 11px;
    color: #aaa;
    letter-spacing: 1px;
}

QLabel#sb_clock {
    font-size: 16px;
    font-weight: bold;
    color: #ffffff;
    letter-spacing: 1px;
    min-width: 48px;
}

/* ── Home Screen ───────────────────────────────────────────────── */
QLabel#home_title {
    font-size: 13px;
    font-weight: bold;
    color: #555;
    letter-spacing: 4px;
}

QLabel#home_sub {
    font-size: 9px;
    color: #2a2a2a;
    letter-spacing: 2px;
}

/* ── Module Cards (home screen) ────────────────────────────────── */
QLabel#card_icon {
    font-size: 26px;
    color: #ffffff;
}

QLabel#card_title {
    font-size: 16px;
    font-weight: bold;
    color: #ffffff;
    letter-spacing: 1px;
}

QLabel#card_sub {
    font-size: 10px;
    color: #555;
    letter-spacing: 1px;
}

/* ── Settings Strip ────────────────────────────────────────────── */
QPushButton#settings_strip {
    background: #0f0f0f;
    border: 1px solid #1e1e1e;
    border-radius: 5px;
    color: #555;
    font-size: 12px;
    letter-spacing: 3px;
    text-align: left;
    padding-left: 20px;
}

QPushButton#settings_strip:hover {
    background: #141414;
    color: #888;
    border: 1px solid #333;
}

QPushButton#settings_strip:pressed {
    background: #0a0a0a;
    color: #aaa;
}

/* ── Back Button ───────────────────────────────────────────────── */
QPushButton#back_btn {
    background: #111;
    border-bottom: 1px solid #1a1a1a;
    color: #444;
    font-size: 12px;
    letter-spacing: 2px;
    text-align: left;
    padding-left: 16px;
    border-radius: 0px;
}

QPushButton#back_btn:pressed {
    background: #0d0d0d;
    color: #00ff88;
}

/* ── Module Page Layout ────────────────────────────────────────── */
QWidget#page_root {
    background: #0c0c0c;
}

QLabel#page_title {
    font-size: 20px;
    font-weight: bold;
    color: #ffffff;
    letter-spacing: 2px;
}

QLabel#page_sub {
    font-size: 9px;
    color: #444;
    letter-spacing: 3px;
}

/* ── Mode Tab Buttons ──────────────────────────────────────────── */
QPushButton#mode_tab {
    background: #111;
    border: 1px solid #1e1e1e;
    border-radius: 4px;
    color: #555;
    font-size: 12px;
    letter-spacing: 2px;
    padding: 0px;
    min-height: 46px;
}

QPushButton#mode_tab:pressed {
    background: #0d0d0d;
}

/* ── Start / Stop ──────────────────────────────────────────────── */
QPushButton#btn_start {
    background: #002a1a;
    border: 1px solid #00663a;
    border-radius: 5px;
    color: #00ff88;
    font-size: 14px;
    font-weight: bold;
    letter-spacing: 3px;
    min-height: 54px;
}

QPushButton#btn_start:pressed {
    background: #003320;
}

QPushButton#btn_start:disabled {
    background: #0a0a0a;
    border: 1px solid #1a1a1a;
    color: #2a2a2a;
}

QPushButton#btn_stop {
    background: #2a0a00;
    border: 1px solid #882200;
    border-radius: 5px;
    color: #ff5522;
    font-size: 14px;
    font-weight: bold;
    letter-spacing: 3px;
    min-height: 54px;
}

QPushButton#btn_stop:pressed {
    background: #1a0500;
}

QPushButton#btn_stop:disabled {
    background: #0a0a0a;
    border: 1px solid #1a1a1a;
    color: #2a2a2a;
}

QPushButton#btn_clear {
    background: transparent;
    border: 1px solid #1e1e1e;
    border-radius: 4px;
    color: #333;
    font-size: 11px;
    letter-spacing: 2px;
    min-height: 38px;
    padding: 0 16px;
}

QPushButton#btn_clear:pressed {
    color: #888;
    border: 1px solid #333;
}

/* ── Status Badge ──────────────────────────────────────────────── */
QLabel#status_idle {
    color: #333;
    font-size: 10px;
    letter-spacing: 2px;
    padding: 5px 12px;
    border: 1px solid #1a1a1a;
    border-radius: 3px;
    background: #0a0a0a;
}

QLabel#status_running {
    color: #00ff88;
    font-size: 10px;
    letter-spacing: 2px;
    padding: 5px 12px;
    border: 1px solid #00aa55;
    border-radius: 3px;
    background: #001a0d;
}

QLabel#status_error {
    color: #ff5522;
    font-size: 10px;
    letter-spacing: 2px;
    padding: 5px 12px;
    border: 1px solid #aa3300;
    border-radius: 3px;
    background: #1a0500;
}

/* ── Terminal ──────────────────────────────────────────────────── */
QTextEdit#terminal {
    background: #070707;
    border: 1px solid #1a1a1a;
    border-radius: 4px;
    color: #00cc66;
    font-family: 'DejaVu Sans Mono', 'Courier New', monospace;
    font-size: 11px;
    padding: 10px;
    selection-background-color: #003322;
}

/* ── Input Fields ──────────────────────────────────────────────── */
QLineEdit#input_field {
    background: #0f0f0f;
    border: 1px solid #252525;
    border-radius: 4px;
    color: #cccccc;
    font-size: 13px;
    padding: 10px 12px;
    min-height: 44px;
}

QLineEdit#input_field:focus {
    border: 1px solid #00aa55;
}

QTextEdit#payload_edit {
    background: #0f0f0f;
    border: 1px solid #252525;
    border-radius: 4px;
    color: #cccccc;
    font-size: 12px;
    padding: 10px;
}

QTextEdit#payload_edit:focus {
    border: 1px solid #00aa55;
}

QComboBox#combo {
    background: #0f0f0f;
    border: 1px solid #252525;
    border-radius: 4px;
    color: #cccccc;
    font-size: 13px;
    padding: 8px 12px;
    min-height: 44px;
}

QComboBox#combo::drop-down { border: none; width: 24px; }
QComboBox#combo::down-arrow { color: #444; }

QComboBox QAbstractItemView {
    background: #111;
    border: 1px solid #252525;
    color: #ccc;
    selection-background-color: #003322;
    font-size: 13px;
    padding: 4px;
}

QSpinBox#spinbox {
    background: #0f0f0f;
    border: 1px solid #252525;
    border-radius: 4px;
    color: #cccccc;
    font-size: 13px;
    padding: 8px 12px;
    min-height: 44px;
}

QSpinBox#spinbox:focus {
    border: 1px solid #00aa55;
}

/* ── Labels ────────────────────────────────────────────────────── */
QLabel#section_label {
    color: #3a3a3a;
    font-size: 9px;
    letter-spacing: 3px;
}

QLabel#info_label {
    color: #666;
    font-size: 11px;
    line-height: 1.5;
}

QLabel#warn_label {
    color: #ff8833;
    font-size: 11px;
}

/* ── Scrollbars ────────────────────────────────────────────────── */
QScrollBar:vertical {
    background: #0a0a0a;
    width: 5px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: #2a2a2a;
    border-radius: 2px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover { background: #3a3a3a; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

/* ── Settings page ─────────────────────────────────────────────── */
QPushButton#settings_row_btn {
    background: #111;
    border: 1px solid #1e1e1e;
    border-radius: 5px;
    color: #aaa;
    font-size: 13px;
    text-align: left;
    padding: 0 20px;
    min-height: 56px;
}

QPushButton#settings_row_btn:pressed {
    background: #0d0d0d;
    border: 1px solid #333;
    color: #fff;
}

QLabel#settings_row_label {
    font-size: 13px;
    color: #aaa;
}

QLabel#settings_row_value {
    font-size: 11px;
    color: #444;
    letter-spacing: 1px;
}
"""
