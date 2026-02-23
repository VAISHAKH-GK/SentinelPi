"""SentinelPi — Bad USB Page (Touchscreen)"""

import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget,
    QLineEdit, QTextEdit, QComboBox, QLabel
)
from base_page import BaseModulePage

MODS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../modules", "badusb")

PRESETS = {
    "Open Notepad (Win)":    "WIN r\nDELAY 500\nSTRING notepad\nENTER",
    "Open Terminal (Linux)": "CTRL ALT t",
    "Lock Screen (Win)":     "WIN l",
    "Hello World":           "STRING Hello from SentinelPi!\nENTER",
}


class BadUsbPage(BaseModulePage):
    PAGE_TITLE = "BAD USB"
    PAGE_CHIP  = "STM32 BluePill · USB HID"
    MODULE_KEY = "badusb"

    SCRIPTS = {
        "Payload":  os.path.join(MODS, "send_payload.py"),
        "Script":   os.path.join(MODS, "custom_script.py"),
        "RevShell": os.path.join(MODS, "reverse_shell.py"),
    }

    def __init__(self):
        self._active = "Payload"
        self._mode_btns = []
        super().__init__()

    def SCRIPT_PATH(self):
        return self.SCRIPTS[self._active]

    def _build_mode_bar(self, layout):
        for mode in self.SCRIPTS:
            btn = self._make_mode_btn(mode, lambda _, m=mode: self._set_mode(m))
            layout.addWidget(btn)
            self._mode_btns.append(btn)
        self._activate_mode_btn(self._mode_btns[0], self._mode_btns)

    def _build_controls(self, layout):
        self._stack = QStackedWidget()
        self._stack.addWidget(self._payload_panel())
        self._stack.addWidget(self._script_panel())
        self._stack.addWidget(self._shell_panel())
        layout.addWidget(self._stack)

    def _set_mode(self, mode):
        self._active = mode
        self._stack.setCurrentIndex(list(self.SCRIPTS).index(mode))
        self._activate_mode_btn(
            self._mode_btns[list(self.SCRIPTS).index(mode)], self._mode_btns
        )

    def _get_script_args(self):
        if self._active == "Payload":
            return ["--payload", self._payload.toPlainText().strip()]
        if self._active == "RevShell":
            return ["--lhost", self._lhost.text().strip(),
                    "--lport", self._lport.text().strip(),
                    "--os",    self._os.currentText().lower()]
        return []

    def _payload_panel(self):
        w = QWidget(); v = QVBoxLayout(w); v.setContentsMargins(0, 4, 0, 0); v.setSpacing(6)
        row = QHBoxLayout()
        row.addWidget(self._lbl("PRESET"))
        self._preset = QComboBox(); self._preset.setObjectName("combo")
        self._preset.addItem("— select —"); self._preset.addItems(list(PRESETS))
        self._preset.currentTextChanged.connect(
            lambda t: self._payload.setPlainText(PRESETS[t]) if t in PRESETS else None)
        row.addWidget(self._preset, 1); v.addLayout(row)
        v.addWidget(self._lbl("DUCKY SCRIPT"))
        self._payload = QTextEdit(); self._payload.setObjectName("input_multiline")
        self._payload.setFixedHeight(72)
        self._payload.setPlaceholderText("STRING Hello\nENTER")
        v.addWidget(self._payload)
        return w

    def _script_panel(self):
        w = QWidget(); v = QVBoxLayout(w); v.setContentsMargins(0, 4, 0, 0); v.setSpacing(6)
        i = QLabel("Load a .duck script file from disk.")
        i.setObjectName("info_label"); v.addWidget(i)
        v.addWidget(self._lbl("FILE PATH"))
        self._spath = QLineEdit(); self._spath.setObjectName("input_field")
        self._spath.setPlaceholderText("/home/pi/scripts/payload.duck")
        v.addWidget(self._spath)
        return w

    def _shell_panel(self):
        w = QWidget(); v = QVBoxLayout(w); v.setContentsMargins(0, 4, 0, 0); v.setSpacing(6)
        i = QLabel("⚠  LAB ONLY — Injects reverse shell into connected machine.")
        i.setObjectName("info_label"); i.setWordWrap(True)
        i.setStyleSheet("color: #ff8833;"); v.addWidget(i)
        row = QHBoxLayout(); row.setSpacing(8)
        lh = QVBoxLayout(); lh.addWidget(self._lbl("LHOST"))
        self._lhost = QLineEdit(); self._lhost.setObjectName("input_field")
        self._lhost.setPlaceholderText("192.168.x.x"); lh.addWidget(self._lhost)
        lp = QVBoxLayout(); lp.addWidget(self._lbl("LPORT"))
        self._lport = QLineEdit(); self._lport.setObjectName("input_field")
        self._lport.setPlaceholderText("4444"); lp.addWidget(self._lport)
        row.addLayout(lh, 2); row.addLayout(lp, 1); v.addLayout(row)
        v.addWidget(self._lbl("TARGET OS"))
        self._os = QComboBox(); self._os.setObjectName("combo")
        self._os.addItems(["Windows", "Linux", "macOS"]); v.addWidget(self._os)
        return w
