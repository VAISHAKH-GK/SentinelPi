"""
SentinelPi — Main Window
Sidebar navigation + stacked content pages.
"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QStackedWidget, QFrame
)
from PyQt5.QtCore import Qt, QTimer
from datetime import datetime

from style import STYLESHEET
from dashboard import DashboardPage
from nfc_page import NfcPage
from wireless_page import WirelessPage
from badusb_page import BadUsbPage
from infrared_page import InfraredPage


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SentinelPi")
        self.setStyleSheet(STYLESHEET)
        self._build_ui()
        self._clock_timer = QTimer()
        self._clock_timer.timeout.connect(self._update_clock)
        self._clock_timer.start(1000)
        self._update_clock()

    def _build_ui(self):
        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)
        layout = QHBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._build_sidebar())
        layout.addWidget(self._build_content(), 1)

    def _build_sidebar(self):
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(180)
        vl = QVBoxLayout(sidebar)
        vl.setContentsMargins(0, 0, 0, 0)
        vl.setSpacing(0)

        # Logo
        logo_block = QWidget()
        logo_block.setStyleSheet("padding: 20px 16px 16px 16px;")
        lb = QVBoxLayout(logo_block)
        lb.setContentsMargins(0, 0, 0, 0)
        lb.setSpacing(2)
        logo = QLabel("SENTINEL")
        logo.setObjectName("logo")
        lb.addWidget(logo)
        logo2 = QLabel("Pi")
        logo2.setObjectName("logo")
        logo2.setStyleSheet("font-size:13px; color:#00aa55; letter-spacing:5px;")
        lb.addWidget(logo2)
        sub = QLabel("SECURITY PLATFORM")
        sub.setObjectName("logo_sub")
        lb.addWidget(sub)
        vl.addWidget(logo_block)

        d = QFrame(); d.setObjectName("divider"); d.setFixedHeight(1)
        vl.addWidget(d)
        vl.addSpacing(8)

        # Nav
        self._nav_buttons = []
        nav_items = [
            ("⬡  DASHBOARD", 0),
            ("◈  NFC / RFID", 1),
            ("◉  WIRELESS",   2),
            ("▲  BAD USB",    3),
            ("◐  INFRARED",   4),
        ]
        for label, idx in nav_items:
            btn = QPushButton(label)
            btn.setObjectName("nav_btn")
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda _, i=idx: self._navigate(i))
            vl.addWidget(btn)
            self._nav_buttons.append(btn)

        vl.addStretch()

        self._clock_label = QLabel()
        self._clock_label.setAlignment(Qt.AlignCenter)
        self._clock_label.setStyleSheet(
            "font-size:10px; color:#333; padding:12px 0px; letter-spacing:1px;"
        )
        vl.addWidget(self._clock_label)
        return sidebar

    def _build_content(self):
        content = QWidget()
        content.setObjectName("content")
        vl = QVBoxLayout(content)
        vl.setContentsMargins(0, 0, 0, 0)
        vl.setSpacing(0)
        self._stack = QStackedWidget()
        for page in [DashboardPage(), NfcPage(), WirelessPage(), BadUsbPage(), InfraredPage()]:
            self._stack.addWidget(page)
        vl.addWidget(self._stack)
        self._navigate(0)
        return content

    def _navigate(self, index: int):
        self._stack.setCurrentIndex(index)
        for i, btn in enumerate(self._nav_buttons):
            btn.setProperty("active", "true" if i == index else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def _update_clock(self):
        self._clock_label.setText(datetime.now().strftime("%H:%M:%S\n%Y-%m-%d"))

    def closeEvent(self, event):
        from process_manager import process_manager
        process_manager.stop_all()
        event.accept()
