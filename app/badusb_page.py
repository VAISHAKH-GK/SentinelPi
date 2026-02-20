"""SentinelPi — Bad USB Page"""

import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QTextEdit, QComboBox, QStackedWidget
)
from PyQt5.QtCore import Qt
from base_page import BaseModulePage

MODS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../modules", "badusb")


class BadUsbPage(BaseModulePage):
    PAGE_TITLE    = "BAD USB"
    PAGE_SUBTITLE = "STM32 BluePill — HID keystroke injection"
    MODULE_KEY    = "badusb"

    SCRIPTS = {
        "Send Payload":  os.path.join(MODS, "send_payload.py"),
        "Custom Script": os.path.join(MODS, "custom_script.py"),
        "Reverse Shell": os.path.join(MODS, "reverse_shell.py"),
    }

    PRESETS = {
        "Open Notepad (Windows)":  "WIN r\nDELAY 500\nSTRING notepad\nENTER",
        "Open Terminal (Linux)":   "CTRL ALT t",
        "Lock Screen (Windows)":   "WIN l",
        "Hello World":             "STRING Hello from SentinelPi!\nENTER",
    }

    def __init__(self):
        self._active_mode = "Send Payload"
        super().__init__()

    @property
    def SCRIPT_PATH(self):
        return self.SCRIPTS[self._active_mode]

    def _build_controls(self, layout):
        layout.addWidget(self._lbl("MODE"))
        row = QHBoxLayout(); row.setSpacing(6)
        self._mode_buttons = {}
        for mode in self.SCRIPTS:
            btn = QPushButton(mode.upper())
            btn.setObjectName("module_card"); btn.setFixedHeight(44)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda _, m=mode: self._set_mode(m))
            row.addWidget(btn); self._mode_buttons[mode] = btn
        layout.addLayout(row); layout.addSpacing(8)

        self._stack = QStackedWidget()
        self._stack.addWidget(self._payload_panel())
        self._stack.addWidget(self._custom_panel())
        self._stack.addWidget(self._shell_panel())
        layout.addWidget(self._stack)
        self._set_mode("Send Payload")

    def _set_mode(self, mode):
        self._active_mode = mode
        self._stack.setCurrentIndex(list(self.SCRIPTS).index(mode))
        for m, btn in self._mode_buttons.items():
            btn.setStyleSheet("background:#001a0d;border:1px solid #00aa55;color:#00ff88;"
                              if m == mode else "")

    def _get_script_args(self):
        if self._active_mode == "Send Payload":
            return ["--payload", self._payload_edit.toPlainText().strip()]
        if self._active_mode == "Reverse Shell":
            return ["--lhost", self._lhost.text().strip(),
                    "--lport", self._lport.text().strip(),
                    "--os",    self._target_os.currentText().lower()]
        return []

    def _payload_panel(self):
        w = QWidget(); vl = QVBoxLayout(w); vl.setContentsMargins(0,0,0,0); vl.setSpacing(8)
        row = QHBoxLayout()
        row.addWidget(self._lbl("PRESET"))
        self._preset = QComboBox(); self._preset.setObjectName("combo")
        self._preset.addItem("— select preset —")
        self._preset.addItems(list(self.PRESETS))
        self._preset.currentTextChanged.connect(
            lambda t: self._payload_edit.setPlainText(self.PRESETS[t]) if t in self.PRESETS else None)
        row.addWidget(self._preset, 1); vl.addLayout(row)
        vl.addWidget(self._lbl("DUCKY SCRIPT PAYLOAD"))
        self._payload_edit = QTextEdit(); self._payload_edit.setObjectName("terminal")
        self._payload_edit.setFixedHeight(100)
        self._payload_edit.setPlaceholderText("STRING Hello World\nENTER")
        vl.addWidget(self._payload_edit)
        return w

    def _custom_panel(self):
        w = QWidget(); vl = QVBoxLayout(w); vl.setContentsMargins(0,0,0,0); vl.setSpacing(8)
        i = QLabel("Load a .duck script file from disk and send it via STM32.")
        i.setObjectName("info_label"); i.setWordWrap(True); vl.addWidget(i)
        self._script_path = QLineEdit(); self._script_path.setObjectName("input_field")
        self._script_path.setPlaceholderText("/home/pi/payloads/script.duck")
        vl.addWidget(self._script_path)
        return w

    def _shell_panel(self):
        w = QWidget(); vl = QVBoxLayout(w); vl.setContentsMargins(0,0,0,0); vl.setSpacing(8)
        warn = QLabel("⚠  LAB USE ONLY — Injects a reverse shell payload into the connected machine.")
        warn.setObjectName("info_label"); warn.setWordWrap(True)
        warn.setStyleSheet("color:#ff8833;"); vl.addWidget(warn)
        vl.addWidget(self._lbl("LISTENER IP"))
        self._lhost = QLineEdit(); self._lhost.setObjectName("input_field")
        self._lhost.setPlaceholderText("192.168.x.x"); vl.addWidget(self._lhost)
        vl.addWidget(self._lbl("PORT"))
        self._lport = QLineEdit(); self._lport.setObjectName("input_field")
        self._lport.setPlaceholderText("4444"); vl.addWidget(self._lport)
        vl.addWidget(self._lbl("TARGET OS"))
        self._target_os = QComboBox(); self._target_os.setObjectName("combo")
        self._target_os.addItems(["Windows", "Linux", "macOS"]); vl.addWidget(self._target_os)
        return w

    def _lbl(self, text):
        l = QLabel(text); l.setObjectName("section_label"); return l
