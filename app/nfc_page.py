"""SentinelPi — NFC / RFID Page"""

import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QStackedWidget
)
from PyQt5.QtCore import Qt
from base_page import BaseModulePage

MODS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../modules", "nfc")


class NfcPage(BaseModulePage):
    PAGE_TITLE    = "NFC / RFID"
    PAGE_SUBTITLE = "PN532 — proximity tag interaction"
    MODULE_KEY    = "nfc"

    SCRIPTS = {
        "Read":    os.path.join(MODS, "nfc_read.py"),
        "Write":   os.path.join(MODS, "nfc_write.py"),
        "Emulate": os.path.join(MODS, "nfc_emulate.py"),
        "Clone":   os.path.join(MODS, "nfc_clone.py"),
    }

    def __init__(self):
        self._active_mode = "Read"
        super().__init__()

    @property
    def SCRIPT_PATH(self):
        return self.SCRIPTS[self._active_mode]

    def _build_controls(self, layout):
        layout.addWidget(self._lbl("MODE"))
        mode_row = QHBoxLayout(); mode_row.setSpacing(6)
        self._mode_buttons = {}
        for mode in self.SCRIPTS:
            btn = QPushButton(mode.upper())
            btn.setObjectName("module_card"); btn.setFixedHeight(44)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda _, m=mode: self._set_mode(m))
            mode_row.addWidget(btn); self._mode_buttons[mode] = btn
        layout.addLayout(mode_row)
        layout.addSpacing(8)

        self._stack = QStackedWidget()
        self._stack.addWidget(self._read_panel())
        self._stack.addWidget(self._write_panel())
        self._stack.addWidget(self._emulate_panel())
        self._stack.addWidget(self._clone_panel())
        layout.addWidget(self._stack)
        self._set_mode("Read")

    def _set_mode(self, mode):
        self._active_mode = mode
        self._stack.setCurrentIndex(list(self.SCRIPTS).index(mode))
        for m, btn in self._mode_buttons.items():
            btn.setStyleSheet("background:#001a0d;border:1px solid #00aa55;color:#00ff88;"
                              if m == mode else "")

    def _get_script_args(self):
        if self._active_mode == "Write":
            uid  = self._write_uid.text().strip()
            data = self._write_data.text().strip()
            return (["--uid", uid] if uid else []) + ["--data", data]
        if self._active_mode == "Emulate":
            uid = self._emu_uid.text().strip()
            return ["--uid", uid] if uid else []
        return []

    def _read_panel(self):
        w = QWidget(); vl = QVBoxLayout(w); vl.setContentsMargins(0,0,0,0)
        i = QLabel("Place a tag near the PN532 antenna and press START to read its UID and data.")
        i.setObjectName("info_label"); i.setWordWrap(True); vl.addWidget(i)
        return w

    def _write_panel(self):
        w = QWidget(); vl = QVBoxLayout(w); vl.setContentsMargins(0,0,0,0); vl.setSpacing(8)
        vl.addWidget(self._lbl("TARGET UID  (blank = any tag)"))
        self._write_uid = QLineEdit(); self._write_uid.setObjectName("input_field")
        self._write_uid.setPlaceholderText("e.g.  04 A3 B1 22"); vl.addWidget(self._write_uid)
        vl.addWidget(self._lbl("DATA TO WRITE"))
        self._write_data = QLineEdit(); self._write_data.setObjectName("input_field")
        self._write_data.setPlaceholderText("ASCII or hex string"); vl.addWidget(self._write_data)
        return w

    def _emulate_panel(self):
        w = QWidget(); vl = QVBoxLayout(w); vl.setContentsMargins(0,0,0,0); vl.setSpacing(8)
        i = QLabel("Emulate a virtual NFC tag. Pi will respond as a tag to readers.")
        i.setObjectName("info_label"); i.setWordWrap(True); vl.addWidget(i)
        vl.addWidget(self._lbl("EMULATED UID"))
        self._emu_uid = QLineEdit(); self._emu_uid.setObjectName("input_field")
        self._emu_uid.setPlaceholderText("e.g.  04 1A 2B 3C"); vl.addWidget(self._emu_uid)
        return w

    def _clone_panel(self):
        w = QWidget(); vl = QVBoxLayout(w); vl.setContentsMargins(0,0,0,0)
        i = QLabel("Reads source tag then writes full content to a blank writable tag. Follow terminal prompts.")
        i.setObjectName("info_label"); i.setWordWrap(True); vl.addWidget(i)
        return w

    def _lbl(self, text):
        l = QLabel(text); l.setObjectName("section_label"); return l
