"""
SentinelPi — Main Window (Touchscreen)
StatusBar (36px top) + QStackedWidget (rest).
No navigate_fn — pages emit back_requested signal.
"""

from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QStackedWidget
from PyQt5.QtCore import Qt

from style import STYLESHEET
from status_bar import StatusBar
from home_screen import HomeScreen
from nfc_page import NfcPage
from wireless_page import WirelessPage
from badusb_page import BadUsbPage
from infrared_page import InfraredPage
from settings_page import SettingsPage

PAGE_HOME     = 0
PAGE_NFC      = 1
PAGE_WIRELESS = 2
PAGE_BADUSB   = 3
PAGE_INFRARED = 4
PAGE_SETTINGS = 5

MODULE_MAP = {
    "nfc":      PAGE_NFC,
    "wireless": PAGE_WIRELESS,
    "badusb":   PAGE_BADUSB,
    "infrared": PAGE_INFRARED,
    "settings": PAGE_SETTINGS,
}


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SentinelPi")
        self.setStyleSheet(STYLESHEET)
        self._build()

    def _build(self):
        root = QWidget(); root.setObjectName("root")
        self.setCentralWidget(root)
        vl = QVBoxLayout(root)
        vl.setContentsMargins(0, 0, 0, 0)
        vl.setSpacing(0)

        self._statusbar = StatusBar()
        vl.addWidget(self._statusbar)

        self._stack = QStackedWidget()
        vl.addWidget(self._stack, 1)

        # Home screen (index 0)
        self._home = HomeScreen()
        self._home.module_selected.connect(self._navigate_to)
        self._stack.addWidget(self._home)

        # Module pages (indices 1-5)
        for key, cls in [
            ("nfc",      NfcPage),
            ("wireless", WirelessPage),
            ("badusb",   BadUsbPage),
            ("infrared", InfraredPage),
            ("settings", SettingsPage),
        ]:
            page = cls()
            page.back_requested.connect(self._go_home)
            self._stack.addWidget(page)

        self._stack.setCurrentIndex(PAGE_HOME)

    def _navigate_to(self, key: str):
        self._stack.setCurrentIndex(MODULE_MAP.get(key, PAGE_HOME))

    def _go_home(self):
        self._stack.setCurrentIndex(PAGE_HOME)

    def closeEvent(self, event):
        from process_manager import process_manager
        process_manager.stop_all()
        event.accept()
