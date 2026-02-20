"""SentinelPi — Global Stylesheet"""

STYLESHEET = """
* {
    font-family: 'Courier New', 'DejaVu Sans Mono', monospace;
    color: #e0e0e0;
    outline: none;
}

QMainWindow, QWidget#root {
    background-color: #0a0a0a;
}

QWidget#sidebar {
    background-color: #0f0f0f;
    border-right: 1px solid #1a1a1a;
}

QLabel#logo {
    font-size: 20px;
    font-weight: bold;
    color: #00ff88;
    letter-spacing: 3px;
    padding: 0px 0px 4px 0px;
}

QLabel#logo_sub {
    font-size: 9px;
    color: #444;
    letter-spacing: 2px;
}

QPushButton#nav_btn {
    background-color: transparent;
    border: none;
    border-left: 3px solid transparent;
    color: #555;
    font-size: 12px;
    letter-spacing: 1px;
    text-align: left;
    padding: 12px 16px;
}

QPushButton#nav_btn:hover {
    background-color: #151515;
    color: #aaa;
    border-left: 3px solid #333;
}

QPushButton#nav_btn[active="true"] {
    background-color: #111;
    color: #00ff88;
    border-left: 3px solid #00ff88;
}

QWidget#content {
    background-color: #0a0a0a;
}

QLabel#page_title {
    font-size: 22px;
    font-weight: bold;
    color: #ffffff;
    letter-spacing: 2px;
}

QLabel#page_sub {
    font-size: 10px;
    color: #444;
    letter-spacing: 3px;
}

QFrame#divider {
    background-color: #1a1a1a;
    max-height: 1px;
}

QPushButton#module_card {
    background-color: #111111;
    border: 1px solid #1e1e1e;
    border-radius: 4px;
    color: #cccccc;
    font-size: 13px;
    padding: 20px 16px;
    text-align: left;
}

QPushButton#module_card:hover {
    background-color: #161616;
    border: 1px solid #2a2a2a;
    color: #ffffff;
}

QPushButton#module_card:pressed {
    background-color: #0d0d0d;
    border: 1px solid #00ff88;
}

QPushButton#btn_start {
    background-color: #003322;
    border: 1px solid #00aa55;
    border-radius: 3px;
    color: #00ff88;
    font-size: 12px;
    letter-spacing: 2px;
    padding: 10px 24px;
}

QPushButton#btn_start:hover {
    background-color: #004433;
    border: 1px solid #00ff88;
}

QPushButton#btn_start:disabled {
    background-color: #0a0a0a;
    border: 1px solid #222;
    color: #333;
}

QPushButton#btn_stop {
    background-color: #2a0a00;
    border: 1px solid #aa3300;
    border-radius: 3px;
    color: #ff5522;
    font-size: 12px;
    letter-spacing: 2px;
    padding: 10px 24px;
}

QPushButton#btn_stop:hover {
    background-color: #3a1000;
    border: 1px solid #ff5522;
}

QPushButton#btn_stop:disabled {
    background-color: #0a0a0a;
    border: 1px solid #222;
    color: #333;
}

QPushButton#btn_clear {
    background-color: transparent;
    border: 1px solid #252525;
    border-radius: 3px;
    color: #444;
    font-size: 11px;
    letter-spacing: 1px;
    padding: 6px 16px;
}

QPushButton#btn_clear:hover {
    border: 1px solid #444;
    color: #888;
}

QTextEdit#terminal {
    background-color: #060606;
    border: 1px solid #1a1a1a;
    border-radius: 3px;
    color: #00cc66;
    font-family: 'Courier New', monospace;
    font-size: 12px;
    padding: 8px;
    selection-background-color: #003322;
}

QLabel#status_idle {
    color: #444;
    font-size: 10px;
    letter-spacing: 2px;
    padding: 4px 10px;
    border: 1px solid #1a1a1a;
    border-radius: 2px;
}

QLabel#status_running {
    color: #00ff88;
    font-size: 10px;
    letter-spacing: 2px;
    padding: 4px 10px;
    border: 1px solid #00aa55;
    border-radius: 2px;
    background-color: #001a0d;
}

QLabel#status_error {
    color: #ff5522;
    font-size: 10px;
    letter-spacing: 2px;
    padding: 4px 10px;
    border: 1px solid #aa3300;
    border-radius: 2px;
    background-color: #1a0500;
}

QLineEdit#input_field {
    background-color: #0d0d0d;
    border: 1px solid #252525;
    border-radius: 3px;
    color: #cccccc;
    font-size: 12px;
    padding: 8px;
}

QLineEdit#input_field:focus {
    border: 1px solid #00aa55;
}

QComboBox#combo {
    background-color: #0d0d0d;
    border: 1px solid #252525;
    border-radius: 3px;
    color: #cccccc;
    font-size: 12px;
    padding: 6px 8px;
}

QComboBox#combo:hover {
    border: 1px solid #444;
}

QComboBox#combo::drop-down { border: none; }

QComboBox QAbstractItemView {
    background-color: #111;
    border: 1px solid #252525;
    color: #ccc;
    selection-background-color: #003322;
}

QLabel#section_label {
    color: #444;
    font-size: 10px;
    letter-spacing: 3px;
}

QLabel#info_label {
    color: #888;
    font-size: 11px;
}

QLabel#data_label {
    color: #00cc66;
    font-size: 12px;
    font-family: 'Courier New', monospace;
}

QScrollBar:vertical {
    background: #0a0a0a;
    width: 6px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: #252525;
    border-radius: 3px;
    min-height: 20px;
}
QScrollBar::handle:vertical:hover { background: #333; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

QWidget#dash_card {
    background-color: #0f0f0f;
    border: 1px solid #1a1a1a;
    border-radius: 4px;
}

QLabel#dash_card_title  { color: #555;    font-size: 9px;  letter-spacing: 3px; }
QLabel#dash_card_value  { color: #ffffff; font-size: 18px; font-weight: bold; }
QLabel#dash_card_status_ok  { color: #00ff88; font-size: 9px; letter-spacing: 2px; }
QLabel#dash_card_status_off { color: #333;    font-size: 9px; letter-spacing: 2px; }

QWidget#warn_banner {
    background-color: #1a0a00;
    border: 1px solid #553300;
    border-radius: 3px;
}

QLabel#warn_text { color: #ff8833; font-size: 10px; letter-spacing: 1px; }
"""
