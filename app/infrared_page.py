"""SentinelPi — Infrared Page (Touchscreen)"""

import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget,
    QLineEdit, QComboBox, QSpinBox, QLabel
)
from base_page import BaseModulePage

MODS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../modules", "infrared")
PROTOCOLS = ["NEC", "Sony SIRC", "RC-5", "RC-6", "Samsung", "Auto"]


class InfraredPage(BaseModulePage):
    PAGE_TITLE = "INFRARED"
    PAGE_CHIP  = "IR TX/RX · GPIO"
    MODULE_KEY = "infrared"

    SCRIPTS = {
        "Capture":  os.path.join(MODS, "ir_capture.py"),
        "Replay":   os.path.join(MODS, "ir_replay.py"),
        "Transmit": os.path.join(MODS, "ir_transmit.py"),
        "Brute":    os.path.join(MODS, "ir_bruteforce.py"),
    }

    def __init__(self):
        self._active = "Capture"
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
        self._ir_stack = QStackedWidget()
        self._ir_stack.addWidget(self._capture_panel())
        self._ir_stack.addWidget(self._replay_panel())
        self._ir_stack.addWidget(self._transmit_panel())
        self._ir_stack.addWidget(self._brute_panel())
        layout.addWidget(self._ir_stack)

    def _set_mode(self, mode):
        self._active = mode
        self._ir_stack.setCurrentIndex(list(self.SCRIPTS).index(mode))
        self._activate_mode_btn(
            self._mode_btns[list(self.SCRIPTS).index(mode)], self._mode_btns
        )

    def _get_script_args(self):
        if self._active == "Capture":
            return ["--protocol", self._cap_proto.currentText(),
                    "--output", "/tmp/ir_capture.json"]
        if self._active == "Replay":
            return ["--file", self._rfile.text().strip()]
        if self._active == "Transmit":
            return ["--code", self._code.text().strip(),
                    "--protocol", self._tx_proto.currentText()]
        if self._active == "Brute":
            return ["--device", self._dev.currentText().lower(),
                    "--start", str(self._bf_start.value()),
                    "--end",   str(self._bf_end.value())]
        return []

    def _capture_panel(self):
        w = QWidget(); v = QVBoxLayout(w); v.setContentsMargins(0, 4, 0, 0); v.setSpacing(6)
        i = QLabel("Point any IR remote at receiver and tap START.\nSignal saved to /tmp/ir_capture.json.")
        i.setObjectName("info_label"); i.setWordWrap(True); v.addWidget(i)
        v.addWidget(self._lbl("PROTOCOL"))
        self._cap_proto = QComboBox(); self._cap_proto.setObjectName("combo")
        self._cap_proto.addItems(PROTOCOLS); v.addWidget(self._cap_proto)
        return w

    def _replay_panel(self):
        w = QWidget(); v = QVBoxLayout(w); v.setContentsMargins(0, 4, 0, 0); v.setSpacing(6)
        i = QLabel("Replay a previously captured signal via the IR TX LED.")
        i.setObjectName("info_label"); v.addWidget(i)
        v.addWidget(self._lbl("CAPTURE FILE"))
        self._rfile = QLineEdit(); self._rfile.setObjectName("input_field")
        self._rfile.setPlaceholderText("/tmp/ir_capture.json"); v.addWidget(self._rfile)
        return w

    def _transmit_panel(self):
        w = QWidget(); v = QVBoxLayout(w); v.setContentsMargins(0, 4, 0, 0); v.setSpacing(6)
        v.addWidget(self._lbl("PROTOCOL"))
        self._tx_proto = QComboBox(); self._tx_proto.setObjectName("combo")
        self._tx_proto.addItems(PROTOCOLS); v.addWidget(self._tx_proto)
        v.addWidget(self._lbl("HEX CODE"))
        self._code = QLineEdit(); self._code.setObjectName("input_field")
        self._code.setPlaceholderText("0x20DF10EF"); v.addWidget(self._code)
        return w

    def _brute_panel(self):
        w = QWidget(); v = QVBoxLayout(w); v.setContentsMargins(0, 4, 0, 0); v.setSpacing(6)
        i = QLabel("Sends IR codes sequentially to find valid commands.")
        i.setObjectName("info_label"); i.setWordWrap(True); v.addWidget(i)
        v.addWidget(self._lbl("DEVICE TYPE"))
        self._dev = QComboBox(); self._dev.setObjectName("combo")
        self._dev.addItems(["TV", "AC", "Set-Top Box", "Projector", "Custom"])
        v.addWidget(self._dev)
        row = QHBoxLayout(); row.setSpacing(8)
        sb = QVBoxLayout(); sb.addWidget(self._lbl("START"))
        self._bf_start = QSpinBox()
        self._bf_start.setRange(0, 0xFFFF); self._bf_start.setValue(0)
        sb.addWidget(self._bf_start)
        eb = QVBoxLayout(); eb.addWidget(self._lbl("END"))
        self._bf_end = QSpinBox()
        self._bf_end.setRange(0, 0xFFFF); self._bf_end.setValue(255)
        eb.addWidget(self._bf_end)
        row.addLayout(sb); row.addLayout(eb); v.addLayout(row)
        return w
