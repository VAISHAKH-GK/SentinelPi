"""SentinelPi — Dashboard Page"""

import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QFrame
)
from PyQt5.QtCore import Qt, QTimer


def _card(title, value, status, ok):
    card = QWidget()
    card.setObjectName("dash_card")
    card.setFixedHeight(90)
    vl = QVBoxLayout(card)
    vl.setContentsMargins(16, 14, 16, 14)
    vl.setSpacing(4)
    t = QLabel(title.upper()); t.setObjectName("dash_card_title"); vl.addWidget(t)
    v = QLabel(value);         v.setObjectName("dash_card_value"); vl.addWidget(v)
    s = QLabel(status.upper())
    s.setObjectName("dash_card_status_ok" if ok else "dash_card_status_off")
    vl.addWidget(s)
    return card


class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()
        self._build_ui()
        self._timer = QTimer()
        self._timer.timeout.connect(self._probe_hardware)
        self._timer.start(3000)
        self._probe_hardware()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(0)

        title = QLabel("DASHBOARD"); title.setObjectName("page_title"); root.addWidget(title)
        sub = QLabel("SYSTEM STATUS OVERVIEW"); sub.setObjectName("page_sub"); root.addWidget(sub)
        root.addSpacing(4)
        d = QFrame(); d.setObjectName("divider"); d.setFixedHeight(1); root.addWidget(d)
        root.addSpacing(24)

        sec = QLabel("HARDWARE MODULES"); sec.setObjectName("section_label"); root.addWidget(sec)
        root.addSpacing(10)

        self._grid = QGridLayout()
        self._grid.setSpacing(10)
        self._cards = {}
        for i, (key, title_text, chip) in enumerate([
            ("nfc",      "NFC / RFID",  "PN532"),
            ("wireless", "2.4 GHz RF",  "nRF24L01+PA+LNA"),
            ("badusb",   "BAD USB",     "STM32 BluePill"),
            ("infrared", "INFRARED",    "IR TX/RX"),
        ]):
            c = _card(title_text, chip, "CHECKING…", False)
            self._cards[key] = c
            self._grid.addWidget(c, i // 2, i % 2)
        root.addLayout(self._grid)
        root.addSpacing(24)

        sec2 = QLabel("SYSTEM"); sec2.setObjectName("section_label"); root.addWidget(sec2)
        root.addSpacing(10)

        import sys
        ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        sys_row = QHBoxLayout(); sys_row.setSpacing(10)
        for c in [_card("PLATFORM","Raspberry Pi 3B+","CONTROLLER",True),
                  _card("PYTHON", ver, "ACTIVE", True),
                  _card("DISPLAY","7\" HDMI Touch","CONNECTED",True)]:
            sys_row.addWidget(c)
        root.addLayout(sys_row)
        root.addSpacing(24)

        warn = QWidget(); warn.setObjectName("warn_banner")
        wl = QHBoxLayout(warn); wl.setContentsMargins(16, 10, 16, 10)
        wt = QLabel("⚠  AUTHORIZED USE ONLY — For academic research and controlled lab environments only.")
        wt.setObjectName("warn_text"); wt.setWordWrap(True)
        wl.addWidget(wt)
        root.addWidget(warn)
        root.addStretch()

    def _probe_hardware(self):
        nfc_ok = os.path.exists("/dev/spidev0.0")
        self._update_card("nfc", "NFC / RFID", "PN532",
                          "ONLINE" if nfc_ok else "NOT DETECTED", nfc_ok, 0, 0)

        rf_ok = os.path.exists("/dev/spidev0.1") or os.path.exists("/dev/spidev0.0")
        self._update_card("wireless", "2.4 GHz RF", "nRF24L01+PA+LNA",
                          "SPI READY" if rf_ok else "NOT DETECTED", rf_ok, 0, 1)

        stm_ok = any(f.startswith(("ttyACM","hidraw"))
                     for f in os.listdir("/dev")) if os.path.exists("/dev") else False
        self._update_card("badusb", "BAD USB", "STM32 BluePill",
                          "ONLINE" if stm_ok else "NOT DETECTED", stm_ok, 1, 0)

        ir_ok = os.path.exists("/sys/class/gpio")
        self._update_card("infrared", "INFRARED", "IR TX/RX",
                          "GPIO READY" if ir_ok else "NOT AVAILABLE", ir_ok, 1, 1)

    def _update_card(self, key, title, chip, status, ok, row, col):
        old = self._cards.get(key)
        if old:
            self._grid.removeWidget(old)
            old.deleteLater()
        new = _card(title, chip, status, ok)
        self._cards[key] = new
        self._grid.addWidget(new, row, col)
