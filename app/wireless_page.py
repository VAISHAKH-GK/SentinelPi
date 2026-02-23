"""SentinelPi — Wireless Page (Touchscreen)"""

import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QStackedWidget, QLineEdit, QSpinBox, QLabel
from base_page import BaseModulePage

MODS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../modules", "wireless")


class WirelessPage(BaseModulePage):
    PAGE_TITLE = "WIRELESS 2.4 GHz"
    PAGE_CHIP  = "nRF24L01+PA+LNA · SPI"
    MODULE_KEY = "wireless"

    SCRIPTS = {
        "Scan":   os.path.join(MODS, "channel_scan.py"),
        "Sniff":  os.path.join(MODS, "packet_sniff.py"),
        "Replay": os.path.join(MODS, "replay.py"),
        "Jam":    os.path.join(MODS, "jammer.py"),
    }

    def __init__(self):
        self._active = "Scan"
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
        self._stack.addWidget(self._scan_panel())
        self._stack.addWidget(self._sniff_panel())
        self._stack.addWidget(self._replay_panel())
        self._stack.addWidget(self._jam_panel())
        layout.addWidget(self._stack)

    def _set_mode(self, mode):
        self._active = mode
        self._stack.setCurrentIndex(list(self.SCRIPTS).index(mode))
        self._activate_mode_btn(
            self._mode_btns[list(self.SCRIPTS).index(mode)], self._mode_btns
        )

    def _get_script_args(self):
        if self._active == "Sniff":
            addr = self._addr.text().strip()
            return ["--channel", str(self._ch.value())] + \
                   (["--address", addr] if addr else [])
        if self._active == "Replay":
            return ["--file", self._rfile.text().strip()]
        return []

    def _scan_panel(self):
        w = QWidget(); v = QVBoxLayout(w); v.setContentsMargins(0, 4, 0, 0)
        i = QLabel("Sweeps channels 0–124 (2400–2524 MHz). Reports active channels in terminal.")
        i.setObjectName("info_label"); i.setWordWrap(True); v.addWidget(i)
        return w

    def _sniff_panel(self):
        w = QWidget(); v = QVBoxLayout(w); v.setContentsMargins(0, 4, 0, 0); v.setSpacing(6)
        v.addWidget(self._lbl("ADDRESS  (blank = promiscuous)"))
        self._addr = QLineEdit(); self._addr.setObjectName("input_field")
        self._addr.setPlaceholderText("E7 E7 E7 E7 E7"); v.addWidget(self._addr)
        v.addWidget(self._lbl("CHANNEL  (0–125)"))
        self._ch = QSpinBox(); self._ch.setRange(0, 125); self._ch.setValue(76)
        v.addWidget(self._ch)
        return w

    def _replay_panel(self):
        w = QWidget(); v = QVBoxLayout(w); v.setContentsMargins(0, 4, 0, 0); v.setSpacing(6)
        i = QLabel("Replays a capture file. Run Sniff first to capture packets.")
        i.setObjectName("info_label"); i.setWordWrap(True); v.addWidget(i)
        v.addWidget(self._lbl("CAPTURE FILE"))
        self._rfile = QLineEdit(); self._rfile.setObjectName("input_field")
        self._rfile.setPlaceholderText("/home/pi/capture.bin"); v.addWidget(self._rfile)
        return w

    def _jam_panel(self):
        w = QWidget(); v = QVBoxLayout(w); v.setContentsMargins(0, 4, 0, 0)
        i = QLabel("⚠  SHIELDED LAB ONLY\nTransmits noise across 2.4 GHz band.")
        i.setObjectName("info_label"); i.setWordWrap(True)
        i.setStyleSheet("color: #ff8833;"); v.addWidget(i)
        return w
