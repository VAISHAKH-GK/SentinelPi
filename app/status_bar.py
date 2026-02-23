"""
SentinelPi — Status Bar
Persistent top strip: device name | hw indicators | time | battery
"""

import os
import subprocess
from datetime import datetime

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QFrame
from PyQt5.QtCore import Qt, QTimer


def _get_battery():
    """Read battery % from /sys (works on Pi with UPS hat or similar)."""
    paths = [
        "/sys/class/power_supply/BAT0/capacity",
        "/sys/class/power_supply/BAT1/capacity",
        "/sys/class/power_supply/battery/capacity",
    ]
    for p in paths:
        try:
            return int(open(p).read().strip())
        except Exception:
            pass
    return None


def _get_charging():
    paths = [
        "/sys/class/power_supply/BAT0/status",
        "/sys/class/power_supply/BAT1/status",
        "/sys/class/power_supply/battery/status",
    ]
    for p in paths:
        try:
            return open(p).read().strip() == "Charging"
        except Exception:
            pass
    return False


def _hw_present(checks):
    return any(os.path.exists(p) for p in checks)


class StatusBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("statusbar")
        self.setFixedHeight(36)
        self._build()

        self._timer = QTimer()
        self._timer.timeout.connect(self._update)
        self._timer.start(2000)
        self._update()

    def _build(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 0, 14, 0)
        layout.setSpacing(0)

        # Left: device name
        name = QLabel("SENTINEL Pi")
        name.setObjectName("sb_device")
        layout.addWidget(name)

        layout.addSpacing(16)
        self._div()

        # HW indicators
        layout.addSpacing(12)
        self._nfc_dot  = self._dot("NFC")
        self._rf_dot   = self._dot("RF")
        self._usb_dot  = self._dot("USB")
        self._ir_dot   = self._dot("IR")
        for d in [self._nfc_dot, self._rf_dot, self._usb_dot, self._ir_dot]:
            layout.addWidget(d)
            layout.addSpacing(8)

        layout.addStretch()

        # Center: time
        self._time_label = QLabel()
        self._time_label.setObjectName("sb_time")
        self._time_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._time_label)

        layout.addStretch()

        # Right: CPU temp + battery
        self._temp_label = QLabel()
        self._temp_label.setObjectName("sb_info")
        layout.addWidget(self._temp_label)

        layout.addSpacing(12)
        self._divider()

        layout.addSpacing(12)

        self._bat_label = QLabel()
        self._bat_label.setObjectName("sb_battery_ok")
        layout.addWidget(self._bat_label)

    def _dot(self, text):
        """Small hardware indicator badge."""
        l = QLabel(text)
        l.setObjectName("sb_info")
        l.setStyleSheet(
            "font-size:8px; letter-spacing:1px; color:#222; "
            "border:1px solid #1a1a1a; border-radius:2px; "
            "padding:1px 4px; background:#0c0c0c;"
        )
        return l

    def _divider(self):
        f = QFrame()
        f.setFrameShape(QFrame.VLine)
        f.setStyleSheet("color:#1e1e1e; background:#1e1e1e;")
        f.setFixedWidth(1)
        self.layout().addWidget(f)

    def _div(self):
        self._divider()

    def _update(self):
        # Clock
        self._time_label.setText(datetime.now().strftime("%H:%M  %a %d %b"))

        # CPU temp
        try:
            temp_raw = open("/sys/class/thermal/thermal_zone0/temp").read().strip()
            temp = int(temp_raw) / 1000
            color = "#ff5522" if temp > 75 else "#ffaa00" if temp > 60 else "#444"
            self._temp_label.setText(f"{temp:.0f}°C")
            self._temp_label.setStyleSheet(f"color:{color}; font-size:11px;")
        except Exception:
            self._temp_label.setText("")

        # Battery
        pct = _get_battery()
        charging = _get_charging()
        if pct is not None:
            icon = "⚡" if charging else ("▓" if pct > 60 else "▒" if pct > 20 else "░")
            text = f"{icon} {pct}%"
            if pct > 50 or charging:
                obj = "sb_battery_ok"
            elif pct > 20:
                obj = "sb_battery_med"
            else:
                obj = "sb_battery_low"
            self._bat_label.setText(text)
            self._bat_label.setObjectName(obj)
            self._bat_label.style().unpolish(self._bat_label)
            self._bat_label.style().polish(self._bat_label)
        else:
            # No battery detected (powered via USB) — show power icon
            self._bat_label.setText("⏻  PWR")
            self._bat_label.setObjectName("sb_info")
            self._bat_label.style().unpolish(self._bat_label)
            self._bat_label.style().polish(self._bat_label)

        # HW indicators
        self._set_dot(self._nfc_dot,  "NFC",
                      _hw_present(["/dev/spidev0.0"]))
        self._set_dot(self._rf_dot,   "RF",
                      _hw_present(["/dev/spidev0.1", "/dev/spidev1.0"]))
        self._set_dot(self._usb_dot,  "USB",
                      any(f.startswith("ttyACM") or f.startswith("hidraw")
                          for f in os.listdir("/dev")) if os.path.exists("/dev") else False)
        self._set_dot(self._ir_dot,   "IR",
                      _hw_present(["/sys/class/gpio"]))

    def _set_dot(self, label, text, active):
        if active:
            label.setStyleSheet(
                "font-size:8px; letter-spacing:1px; color:#00ff88; "
                "border:1px solid #00aa55; border-radius:2px; "
                "padding:1px 4px; background:#001a0d;"
            )
        else:
            label.setStyleSheet(
                "font-size:8px; letter-spacing:1px; color:#222; "
                "border:1px solid #1a1a1a; border-radius:2px; "
                "padding:1px 4px; background:#0c0c0c;"
            )
