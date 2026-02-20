"""SentinelPi — Infrared Page"""

import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QComboBox, QSpinBox, QStackedWidget
)
from PyQt5.QtCore import Qt
from base_page import BaseModulePage

MODS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../modules", "infrared")
PROTOCOLS = ["NEC", "Sony SIRC", "RC-5", "RC-6", "Samsung", "Auto-detect"]


class InfraredPage(BaseModulePage):
    PAGE_TITLE    = "INFRARED"
    PAGE_SUBTITLE = "IR TX/RX — capture, decode, replay"
    MODULE_KEY    = "infrared"

    SCRIPTS = {
        "Capture":      os.path.join(MODS, "ir_capture.py"),
        "Replay":       os.path.join(MODS, "ir_replay.py"),
        "Raw Transmit": os.path.join(MODS, "ir_transmit.py"),
        "Brute Force":  os.path.join(MODS, "ir_bruteforce.py"),
    }

    def __init__(self):
        self._active_mode = "Capture"
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
        self._stack.addWidget(self._capture_panel())
        self._stack.addWidget(self._replay_panel())
        self._stack.addWidget(self._transmit_panel())
        self._stack.addWidget(self._bruteforce_panel())
        layout.addWidget(self._stack)
        self._set_mode("Capture")

    def _set_mode(self, mode):
        self._active_mode = mode
        self._stack.setCurrentIndex(list(self.SCRIPTS).index(mode))
        for m, btn in self._mode_buttons.items():
            btn.setStyleSheet("background:#001a0d;border:1px solid #00aa55;color:#00ff88;"
                              if m == mode else "")

    def _get_script_args(self):
        if self._active_mode == "Capture":
            return ["--protocol", self._cap_proto.currentText(),
                    "--output", "/tmp/ir_capture.json"]
        if self._active_mode == "Replay":
            return ["--file", self._replay_file.text().strip()]
        if self._active_mode == "Raw Transmit":
            return ["--code", self._raw_code.text().strip(),
                    "--protocol", self._tx_proto.currentText()]
        if self._active_mode == "Brute Force":
            return ["--device", self._bf_device.currentText().lower(),
                    "--start", str(self._bf_start.value()),
                    "--end",   str(self._bf_end.value())]
        return []

    def _capture_panel(self):
        w = QWidget(); vl = QVBoxLayout(w); vl.setContentsMargins(0,0,0,0); vl.setSpacing(8)
        i = QLabel("Point any IR remote at the receiver and press START. Signal decoded and saved.")
        i.setObjectName("info_label"); i.setWordWrap(True); vl.addWidget(i)
        vl.addWidget(self._lbl("EXPECTED PROTOCOL"))
        self._cap_proto = QComboBox(); self._cap_proto.setObjectName("combo")
        self._cap_proto.addItems(PROTOCOLS); vl.addWidget(self._cap_proto)
        return w

    def _replay_panel(self):
        w = QWidget(); vl = QVBoxLayout(w); vl.setContentsMargins(0,0,0,0); vl.setSpacing(8)
        i = QLabel("Replay a previously captured IR signal via the IR transmitter LED.")
        i.setObjectName("info_label"); i.setWordWrap(True); vl.addWidget(i)
        vl.addWidget(self._lbl("CAPTURE FILE"))
        self._replay_file = QLineEdit(); self._replay_file.setObjectName("input_field")
        self._replay_file.setPlaceholderText("/tmp/ir_capture.json"); vl.addWidget(self._replay_file)
        return w

    def _transmit_panel(self):
        w = QWidget(); vl = QVBoxLayout(w); vl.setContentsMargins(0,0,0,0); vl.setSpacing(8)
        vl.addWidget(self._lbl("PROTOCOL"))
        self._tx_proto = QComboBox(); self._tx_proto.setObjectName("combo")
        self._tx_proto.addItems(PROTOCOLS); vl.addWidget(self._tx_proto)
        vl.addWidget(self._lbl("HEX CODE"))
        self._raw_code = QLineEdit(); self._raw_code.setObjectName("input_field")
        self._raw_code.setPlaceholderText("e.g.  0x20DF10EF"); vl.addWidget(self._raw_code)
        return w

    def _bruteforce_panel(self):
        w = QWidget(); vl = QVBoxLayout(w); vl.setContentsMargins(0,0,0,0); vl.setSpacing(8)
        i = QLabel("Brute-forces IR codes for a device type by transmitting codes sequentially.")
        i.setObjectName("info_label"); i.setWordWrap(True); vl.addWidget(i)
        vl.addWidget(self._lbl("DEVICE TYPE"))
        self._bf_device = QComboBox(); self._bf_device.setObjectName("combo")
        self._bf_device.addItems(["TV","AC","Set-Top Box","Projector","Custom"])
        vl.addWidget(self._bf_device)
        range_row = QHBoxLayout(); range_row.setSpacing(12)
        sb = QVBoxLayout(); sb.addWidget(self._lbl("START CODE"))
        self._bf_start = QSpinBox(); self._bf_start.setRange(0,0xFFFF); self._bf_start.setValue(0)
        self._bf_start.setStyleSheet("background:#0d0d0d;border:1px solid #252525;color:#ccc;padding:6px;font-family:monospace;")
        sb.addWidget(self._bf_start); range_row.addLayout(sb)
        eb = QVBoxLayout(); eb.addWidget(self._lbl("END CODE"))
        self._bf_end = QSpinBox(); self._bf_end.setRange(0,0xFFFF); self._bf_end.setValue(255)
        self._bf_end.setStyleSheet("background:#0d0d0d;border:1px solid #252525;color:#ccc;padding:6px;font-family:monospace;")
        eb.addWidget(self._bf_end); range_row.addLayout(eb)
        vl.addLayout(range_row)
        return w

    def _lbl(self, text):
        l = QLabel(text); l.setObjectName("section_label"); return l
