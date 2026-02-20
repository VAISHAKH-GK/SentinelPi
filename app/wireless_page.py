"""SentinelPi — Wireless Page"""

import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QSpinBox, QStackedWidget
)
from PyQt5.QtCore import Qt
from base_page import BaseModulePage

MODS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../modules", "wireless")


class WirelessPage(BaseModulePage):
    PAGE_TITLE    = "2.4 GHz WIRELESS"
    PAGE_SUBTITLE = "nRF24L01+PA+LNA — channel analysis & packet capture"
    MODULE_KEY    = "wireless"

    SCRIPTS = {
        "Channel Scan":  os.path.join(MODS, "channel_scan.py"),
        "Packet Sniff":  os.path.join(MODS, "packet_sniff.py"),
        "Replay Attack": os.path.join(MODS, "replay.py"),
        "Jam (Demo)":    os.path.join(MODS, "jammer.py"),
    }

    def __init__(self):
        self._active_mode = "Channel Scan"
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
        self._stack.addWidget(self._scan_panel())
        self._stack.addWidget(self._sniff_panel())
        self._stack.addWidget(self._replay_panel())
        self._stack.addWidget(self._jam_panel())
        layout.addWidget(self._stack)
        self._set_mode("Channel Scan")

    def _set_mode(self, mode):
        self._active_mode = mode
        self._stack.setCurrentIndex(list(self.SCRIPTS).index(mode))
        for m, btn in self._mode_buttons.items():
            btn.setStyleSheet("background:#001a0d;border:1px solid #00aa55;color:#00ff88;"
                              if m == mode else "")

    def _get_script_args(self):
        if self._active_mode == "Packet Sniff":
            addr = self._sniff_addr.text().strip()
            return ["--channel", str(self._sniff_ch.value())] + \
                   (["--address", addr] if addr else [])
        if self._active_mode == "Replay Attack":
            return ["--file", self._replay_file.text().strip()]
        return []

    def _scan_panel(self):
        w = QWidget(); vl = QVBoxLayout(w); vl.setContentsMargins(0,0,0,0)
        i = QLabel("Scans all 125 channels (2400–2525 MHz) and reports signal activity.")
        i.setObjectName("info_label"); i.setWordWrap(True); vl.addWidget(i)
        return w

    def _sniff_panel(self):
        w = QWidget(); vl = QVBoxLayout(w); vl.setContentsMargins(0,0,0,0); vl.setSpacing(8)
        vl.addWidget(self._lbl("TARGET ADDRESS  (blank = promiscuous)"))
        self._sniff_addr = QLineEdit(); self._sniff_addr.setObjectName("input_field")
        self._sniff_addr.setPlaceholderText("5-byte hex  e.g.  E7 E7 E7 E7 E7")
        vl.addWidget(self._sniff_addr)
        vl.addWidget(self._lbl("CHANNEL  (0–125)"))
        self._sniff_ch = QSpinBox(); self._sniff_ch.setRange(0, 125); self._sniff_ch.setValue(76)
        self._sniff_ch.setStyleSheet("background:#0d0d0d;border:1px solid #252525;color:#ccc;padding:6px;font-family:monospace;")
        vl.addWidget(self._sniff_ch)
        return w

    def _replay_panel(self):
        w = QWidget(); vl = QVBoxLayout(w); vl.setContentsMargins(0,0,0,0); vl.setSpacing(8)
        i = QLabel("Replays a previously captured packet dump.")
        i.setObjectName("info_label"); i.setWordWrap(True); vl.addWidget(i)
        vl.addWidget(self._lbl("CAPTURE FILE PATH"))
        self._replay_file = QLineEdit(); self._replay_file.setObjectName("input_field")
        self._replay_file.setPlaceholderText("/home/pi/captures/dump.bin")
        vl.addWidget(self._replay_file)
        return w

    def _jam_panel(self):
        w = QWidget(); vl = QVBoxLayout(w); vl.setContentsMargins(0,0,0,0)
        warn = QLabel("⚠  DEMO ONLY — Only use in a shielded lab. Illegal outside controlled settings.")
        warn.setObjectName("info_label"); warn.setWordWrap(True)
        warn.setStyleSheet("color:#ff8833;"); vl.addWidget(warn)
        return w

    def _lbl(self, text):
        l = QLabel(text); l.setObjectName("section_label"); return l
