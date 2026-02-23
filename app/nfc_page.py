"""SentinelPi — NFC / RFID Page (Touchscreen)"""

import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget, QLineEdit, QLabel
from base_page import BaseModulePage

MODS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../modules", "nfc")


class NfcPage(BaseModulePage):
    PAGE_TITLE = "NFC / RFID"
    PAGE_CHIP  = "PN532 · SPI"
    MODULE_KEY = "nfc"

    SCRIPTS = {
        "Read":    os.path.join(MODS, "nfc_read.py"),
        "Write":   os.path.join(MODS, "nfc_write.py"),
        "Emulate": os.path.join(MODS, "nfc_emulate.py"),
        "Clone":   os.path.join(MODS, "nfc_clone.py"),
    }

    def __init__(self):
        self._active = "Read"
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
        self._stack.addWidget(self._read_panel())
        self._stack.addWidget(self._write_panel())
        self._stack.addWidget(self._emulate_panel())
        self._stack.addWidget(self._clone_panel())
        layout.addWidget(self._stack)

    def _set_mode(self, mode):
        self._active = mode
        self._stack.setCurrentIndex(list(self.SCRIPTS).index(mode))
        self._activate_mode_btn(
            self._mode_btns[list(self.SCRIPTS).index(mode)], self._mode_btns
        )

    def _get_script_args(self):
        if self._active == "Write":
            uid  = self._write_uid.text().strip()
            data = self._write_data.text().strip()
            return (["--uid", uid] if uid else []) + ["--data", data]
        if self._active == "Emulate":
            uid = self._emu_uid.text().strip()
            return ["--uid", uid] if uid else []
        return []

    def _read_panel(self):
        w = QWidget(); v = QVBoxLayout(w); v.setContentsMargins(0, 4, 0, 0)
        i = QLabel("Place tag near PN532 antenna, then tap START.")
        i.setObjectName("info_label"); i.setWordWrap(True); v.addWidget(i)
        return w

    def _write_panel(self):
        w = QWidget(); v = QVBoxLayout(w); v.setContentsMargins(0, 4, 0, 0); v.setSpacing(6)
        v.addWidget(self._lbl("TARGET UID  (blank = any)"))
        self._write_uid = QLineEdit(); self._write_uid.setObjectName("input_field")
        self._write_uid.setPlaceholderText("04 A3 B1 22"); v.addWidget(self._write_uid)
        v.addWidget(self._lbl("DATA TO WRITE"))
        self._write_data = QLineEdit(); self._write_data.setObjectName("input_field")
        self._write_data.setPlaceholderText("text or hex"); v.addWidget(self._write_data)
        return w

    def _emulate_panel(self):
        w = QWidget(); v = QVBoxLayout(w); v.setContentsMargins(0, 4, 0, 0); v.setSpacing(6)
        i = QLabel("Pi responds as an NFC tag to any reader.")
        i.setObjectName("info_label"); i.setWordWrap(True); v.addWidget(i)
        v.addWidget(self._lbl("EMULATED UID"))
        self._emu_uid = QLineEdit(); self._emu_uid.setObjectName("input_field")
        self._emu_uid.setPlaceholderText("04 1A 2B 3C"); v.addWidget(self._emu_uid)
        return w

    def _clone_panel(self):
        w = QWidget(); v = QVBoxLayout(w); v.setContentsMargins(0, 4, 0, 0)
        i = QLabel("Step 1: place source tag → Step 2: place blank tag.\nFollow terminal prompts.")
        i.setObjectName("info_label"); i.setWordWrap(True); v.addWidget(i)
        return w
