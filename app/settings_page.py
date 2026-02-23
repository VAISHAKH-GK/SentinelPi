"""SentinelPi — Settings Page (Touchscreen)"""

import os
import sys
import subprocess
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QScrollArea
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal


def _row(left_title, left_sub, right_widget=None):
    """A settings row with title, subtitle, optional right widget."""
    w = QWidget()
    w.setStyleSheet("background:#111; border-radius:5px;")
    w.setFixedHeight(58)
    hl = QHBoxLayout(w)
    hl.setContentsMargins(18, 0, 18, 0)
    hl.setSpacing(0)

    text = QVBoxLayout()
    text.setSpacing(2)
    t = QLabel(left_title)
    t.setObjectName("settings_row_label")
    text.addWidget(t)
    s = QLabel(left_sub)
    s.setObjectName("settings_row_value")
    text.addWidget(s)
    hl.addLayout(text)
    hl.addStretch()

    if right_widget:
        hl.addWidget(right_widget)
    return w


class SettingsPage(QWidget):
    back_requested = pyqtSignal()
    def __init__(self):
        super().__init__()
        
        self._build()
        QTimer.singleShot(100, self._load_info)

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        self.setObjectName("page_root")

        # Back
        back = QPushButton("◀   HOME")
        back.setObjectName("back_btn")
        back.setFixedHeight(42)
        back.setCursor(Qt.PointingHandCursor)
        back.clicked.connect(self.back_requested.emit)
        root.addWidget(back)

        # Header
        hdr = QWidget()
        hdr.setStyleSheet("background:#0e0e0e; border-bottom:1px solid #1a1a1a;")
        hdr.setFixedHeight(56)
        hl = QHBoxLayout(hdr)
        hl.setContentsMargins(20, 0, 20, 0)
        t = QLabel("SETTINGS")
        t.setObjectName("page_title")
        hl.addWidget(t)
        root.addWidget(hdr)

        # Scrollable content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("background:#0c0c0c;")

        content = QWidget()
        content.setStyleSheet("background:#0c0c0c;")
        vl = QVBoxLayout(content)
        vl.setContentsMargins(16, 16, 16, 16)
        vl.setSpacing(10)

        # ── System Info ──
        vl.addWidget(self._section("SYSTEM INFO"))

        self._platform_row = _row("Platform", "detecting…")
        vl.addWidget(self._platform_row)

        self._python_row = _row("Python", f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
        vl.addWidget(self._python_row)

        self._ip_row = _row("IP Address", "detecting…")
        vl.addWidget(self._ip_row)

        self._uptime_row = _row("Uptime", "detecting…")
        vl.addWidget(self._uptime_row)

        vl.addSpacing(6)

        # ── Hardware ──
        vl.addWidget(self._section("HARDWARE STATUS"))

        self._hw_rows = {}
        for key, label, iface in [
            ("nfc",      "NFC / RFID  (PN532)",      "SPI0.0"),
            ("wireless", "2.4 GHz RF  (nRF24)",      "SPI0.1"),
            ("badusb",   "Bad USB     (STM32)",       "USB/ACM"),
            ("infrared", "Infrared    (IR TX/RX)",    "GPIO"),
        ]:
            row_w = _row(label, iface, self._status_dot("checking"))
            self._hw_rows[key] = row_w
            vl.addWidget(row_w)

        vl.addSpacing(6)

        # ── Display ──
        vl.addWidget(self._section("DISPLAY"))
        vl.addWidget(_row("Resolution", "800 × 480"))
        vl.addWidget(_row("Display", "7\" HDMI Touchscreen"))

        vl.addSpacing(6)

        # ── Actions ──
        vl.addWidget(self._section("ACTIONS"))

        shutdown_btn = QPushButton("⏻   SHUTDOWN")
        shutdown_btn.setObjectName("settings_row_btn")
        shutdown_btn.setFixedHeight(56)
        shutdown_btn.setCursor(Qt.PointingHandCursor)
        shutdown_btn.clicked.connect(self._shutdown)
        vl.addWidget(shutdown_btn)

        reboot_btn = QPushButton("↺   REBOOT")
        reboot_btn.setObjectName("settings_row_btn")
        reboot_btn.setFixedHeight(56)
        reboot_btn.setCursor(Qt.PointingHandCursor)
        reboot_btn.clicked.connect(self._reboot)
        vl.addWidget(reboot_btn)

        vl.addStretch()
        scroll.setWidget(content)
        root.addWidget(scroll, 1)

    def _section(self, text):
        l = QLabel(text)
        l.setObjectName("section_label")
        l.setStyleSheet("color:#3a3a3a; font-size:9px; letter-spacing:3px; padding-top:4px;")
        return l

    def _status_dot(self, state):
        dot = QLabel("●")
        colors = {"ok": "#00ff88", "err": "#ff5522", "checking": "#555"}
        dot.setStyleSheet(f"color:{colors.get(state,'#555')}; font-size:18px;")
        dot._state = state
        return dot

    def _load_info(self):
        # Platform
        try:
            with open("/proc/device-tree/model", "r") as f:
                model = f.read().strip("\x00").strip()
        except Exception:
            import platform
            model = platform.node()
        self._update_row(self._platform_row, "Platform", model)

        # IP
        try:
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
        except Exception:
            ip = "No network"
        self._update_row(self._ip_row, "IP Address", ip)

        # Uptime
        try:
            with open("/proc/uptime") as f:
                secs = float(f.read().split()[0])
            h, rem = divmod(int(secs), 3600)
            m = rem // 60
            uptime = f"{h}h {m}m"
        except Exception:
            uptime = "—"
        self._update_row(self._uptime_row, "Uptime", uptime)

        # Hardware detection
        hw_checks = {
            "nfc":      lambda: os.path.exists("/dev/spidev0.0"),
            "wireless": lambda: os.path.exists("/dev/spidev0.0"),
            "badusb":   lambda: any(f.startswith("ttyACM") for f in os.listdir("/dev")) if os.path.exists("/dev") else False,
            "infrared": lambda: os.path.exists("/sys/class/gpio"),
        }
        for key, check in hw_checks.items():
            try:
                ok = check()
            except Exception:
                ok = False
            row_w = self._hw_rows[key]
            # Find and update the status dot (last widget in row's hbox)
            hl = row_w.layout()
            if hl and hl.count() > 0:
                last = hl.itemAt(hl.count() - 1).widget()
                if last:
                    last.setText("●")
                    last.setStyleSheet(
                        f"color:{'#00ff88' if ok else '#ff5522'}; font-size:18px;"
                    )

    def _update_row(self, row_w, title, subtitle):
        hl = row_w.layout()
        if hl and hl.count() > 0:
            text_layout = hl.itemAt(0).layout()
            if text_layout and text_layout.count() > 1:
                sub_label = text_layout.itemAt(1).widget()
                if sub_label:
                    sub_label.setText(subtitle)

    def _shutdown(self):
        try:
            subprocess.run(["sudo", "shutdown", "-h", "now"])
        except Exception:
            pass

    def _reboot(self):
        try:
            subprocess.run(["sudo", "reboot"])
        except Exception:
            pass
