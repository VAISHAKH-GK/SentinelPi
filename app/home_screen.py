"""
SentinelPi — Home Screen
Big tap tiles in a 2x2 + 1 settings strip layout.
Designed for 800x480 with 36px status bar = 444px usable height.
"""

from PyQt5.QtWidgets import (
    QWidget, QGridLayout, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QSizePolicy, QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal


# Module definitions: (key, icon, label, description, chip)
MODULES = [
    ("nfc",      "◈", "NFC / RFID",    "Read · Write · Emulate · Clone",  "PN532"),
    ("wireless", "◉", "WIRELESS",       "Scan · Sniff · Replay",            "nRF24L01"),
    ("badusb",   "▲", "BAD USB",        "HID Inject · Payloads",            "STM32"),
    ("infrared", "◐", "INFRARED",       "Capture · Replay · Brute",         "IR TX/RX"),
]


class TileButton(QWidget):
    """A big touchscreen tile with icon, label, description, and chip badge."""
    clicked = pyqtSignal(str)

    def __init__(self, key, icon, label, desc, chip, parent=None):
        super().__init__(parent)
        self._key = key
        self.setCursor(Qt.PointingHandCursor)
        self.setObjectName("tile_widget")
        self._pressed = False
        self._build(icon, label, desc, chip)

    def _build(self, icon, label, desc, chip):
        self.setStyleSheet("""
            QWidget#tile_widget {
                background-color: #0f0f0f;
                border: 1px solid #1e1e1e;
                border-radius: 8px;
            }
            QWidget#tile_widget:hover {
                background-color: #111;
                border: 1px solid #252525;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(4)

        # Top row: icon + chip badge
        top = QHBoxLayout()
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet("font-size:28px; color:#00ff88; background:transparent;")
        top.addWidget(icon_lbl)
        top.addStretch()
        chip_lbl = QLabel(chip)
        chip_lbl.setStyleSheet(
            "font-size:8px; color:#333; letter-spacing:1px; "
            "border:1px solid #1e1e1e; border-radius:2px; "
            "padding:2px 6px; background:#0a0a0a; font-family:'Courier New',monospace;"
        )
        top.addWidget(chip_lbl)
        layout.addLayout(top)

        layout.addStretch()

        # Label
        lbl = QLabel(label)
        lbl.setStyleSheet(
            "font-size:15px; font-weight:bold; color:#cccccc; "
            "letter-spacing:2px; background:transparent; "
            "font-family:'Courier New',monospace;"
        )
        layout.addWidget(lbl)

        # Description
        desc_lbl = QLabel(desc)
        desc_lbl.setStyleSheet(
            "font-size:9px; color:#393939; letter-spacing:1px; "
            "background:transparent; font-family:'Courier New',monospace;"
        )
        layout.addWidget(desc_lbl)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def mousePressEvent(self, event):
        self._pressed = True
        self.setStyleSheet("""
            QWidget#tile_widget {
                background-color: #001a0d;
                border: 1px solid #00ff88;
                border-radius: 8px;
            }
        """)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if self._pressed:
            self._pressed = False
            self.setStyleSheet("""
                QWidget#tile_widget {
                    background-color: #0f0f0f;
                    border: 1px solid #1e1e1e;
                    border-radius: 8px;
                }
            """)
            self.clicked.emit(self._key)
        super().mouseReleaseEvent(event)


class HomeScreen(QWidget):
    module_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("home")
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 8)
        root.setSpacing(8)

        # 2x2 grid of main tiles
        grid = QGridLayout()
        grid.setSpacing(8)

        for i, (key, icon, label, desc, chip) in enumerate(MODULES):
            tile = TileButton(key, icon, label, desc, chip)
            tile.clicked.connect(self.module_selected.emit)
            grid.addWidget(tile, i // 2, i % 2)

        root.addLayout(grid, 1)

        # Bottom strip: Settings button (shorter)
        bottom = QHBoxLayout()
        bottom.setSpacing(8)

        settings_btn = QPushButton("⚙   SETTINGS")
        settings_btn.setObjectName("tile_settings")
        settings_btn.setFixedHeight(46)
        settings_btn.setCursor(Qt.PointingHandCursor)
        settings_btn.clicked.connect(lambda: self.module_selected.emit("settings"))
        bottom.addWidget(settings_btn, 1)

        # Quick-glance info strip next to settings
        info_strip = QWidget()
        info_strip.setObjectName("tile_settings")
        info_strip.setFixedHeight(46)
        info_strip.setFixedWidth(160)
        il = QHBoxLayout(info_strip)
        il.setContentsMargins(12, 0, 12, 0)
        il.setSpacing(12)

        import os
        from datetime import datetime

        # SPI status
        spi = "SPI ●" if os.path.exists("/dev/spidev0.0") else "SPI ○"
        spi_color = "#00aa55" if os.path.exists("/dev/spidev0.0") else "#252525"
        spi_lbl = QLabel(spi)
        spi_lbl.setStyleSheet(f"font-size:9px; color:{spi_color}; letter-spacing:1px; background:transparent; font-family:'Courier New',monospace;")
        il.addWidget(spi_lbl)

        gpio = "GPIO ●"
        gpio_lbl = QLabel(gpio)
        gpio_lbl.setStyleSheet("font-size:9px; color:#00aa55; letter-spacing:1px; background:transparent; font-family:'Courier New',monospace;")
        il.addWidget(gpio_lbl)

        bottom.addWidget(info_strip)
        root.addLayout(bottom)
