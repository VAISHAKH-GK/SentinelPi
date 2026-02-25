# ui/main_window.py
# Main window: status bar, main menu, and navigation helpers.
# Attack screens live in ui/pages/ — one file per module.

import os
import subprocess
from datetime import datetime

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStackedWidget, QScrollArea,
    QFrame, QGridLayout, QLineEdit, QTextEdit
)
from PyQt5.QtCore import QTimer, QThread, pyqtSignal

from ui.pages.badusb    import BadUSBPage
from ui.pages.infrared  import InfraredPage
from ui.pages.wireless  import WirelessPage
from ui.pages.nfc       import NFCPage

STYLE = """
QMainWindow, QWidget {
    background-color: #0d0f0e;
    color: #b8f5c8;
    font-family: 'Courier New', monospace;
}
#statusBar {
    background-color: #111411;
    border-bottom: 1px solid #1e3d2a;
}
#statusLabel { color: #4caf6e; font-size: 13px; }
#statusRight  { color: #2e7d4f; font-size: 13px; }
#pageTitle {
    color: #5dff8f;
    font-size: 20px;
    font-weight: bold;
    letter-spacing: 3px;
    padding: 8px 0 4px 0;
}
#moduleTile {
    background-color: #111714;
    border: 1px solid #1e3d2a;
    border-radius: 8px;
    color: #7dffaa;
    font-size: 17px;
    font-weight: bold;
    letter-spacing: 2px;
    padding: 28px 12px;
}
#moduleTile:pressed  { background-color: #1a2e20; border-color: #4caf6e; }
#attackBtn {
    background-color: #0f1a13;
    border: 1px solid #1e3d2a;
    border-radius: 6px;
    color: #9effc0;
    font-size: 15px;
    padding: 16px;
    text-align: left;
}
#attackBtn:pressed   { background-color: #172b1e; border-color: #4caf6e; }
#backBtn {
    background-color: #111411;
    border: 1px solid #1e3d2a;
    border-radius: 6px;
    color: #4caf6e;
    font-size: 14px;
    padding: 10px 20px;
}
#backBtn:pressed     { background-color: #1a2e20; }
#execBtn {
    background-color: #173a22;
    border: 1px solid #4caf6e;
    border-radius: 6px;
    color: #5dff8f;
    font-size: 15px;
    font-weight: bold;
    padding: 14px;
    letter-spacing: 1px;
}
#execBtn:pressed     { background-color: #1f5030; }
#saveBtn {
    background-color: #0f1a13;
    border: 1px solid #2e7d4f;
    border-radius: 6px;
    color: #4caf6e;
    font-size: 14px;
    padding: 14px;
}
#saveBtn:pressed     { background-color: #172b1e; }
#stopBtn {
    background-color: #1a0d0d;
    border: 1px solid #7d2e2e;
    border-radius: 6px;
    color: #ff6b6b;
    font-size: 15px;
    padding: 14px;
}
#stopBtn:pressed     { background-color: #2d1515; }
#dangerBtn {
    background-color: #1a0d0d;
    border: 1px solid #7d2e2e;
    border-radius: 6px;
    color: #ff6b6b;
    font-size: 13px;
    padding: 8px 14px;
}
#dangerBtn:pressed   { background-color: #2d1515; }
#settingsBtn {
    background-color: #111411;
    border: 1px solid #1e3d2a;
    border-radius: 6px;
    color: #4caf6e;
    font-size: 13px;
    padding: 8px 14px;
}
#settingsBtn:pressed { background-color: #1a2e20; }
#logBox {
    background-color: #080f0a;
    border: 1px solid #1e3d2a;
    border-radius: 6px;
    color: #7dffaa;
    font-size: 13px;
    font-family: 'Courier New', monospace;
    padding: 6px;
}
#inputField {
    background-color: #0f1a13;
    border: 1px solid #2e7d4f;
    border-radius: 6px;
    color: #9effc0;
    font-size: 15px;
    padding: 10px;
    font-family: 'Courier New', monospace;
}
#inputLabel { color: #4caf6e; font-size: 13px; padding-top: 4px; }
#descLabel  { color: #4caf6e; font-size: 13px; }
QFrame[frameShape="4"] { color: #1e3d2a; }
"""


class Worker(QThread):
    # line_ready fires for each live output line
    # done fires once when the function exits
    line_ready = pyqtSignal(str)
    done       = pyqtSignal(str)   # empty = clean exit, else error message

    def __init__(self, func, kwargs=None):
        super().__init__()
        self.func   = func
        self.kwargs = kwargs or {}

    def run(self):
        try:
            # Pass log=... so modules can stream lines live.
            # If the module does not accept log= yet it falls back gracefully.
            self.func(log=self.line_ready.emit, **self.kwargs)
            self.done.emit("")
        except TypeError:
            # Module run() does not accept log kwarg yet — call without it
            try:
                out = self.func(**self.kwargs)
                if out:
                    self.line_ready.emit(str(out))
                self.done.emit("")
            except Exception as e:
                self.done.emit(f"[ERROR] {e}")
        except Exception as e:
            self.done.emit(f"[ERROR] {e}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SentinelPi")
        self.setGeometry(0, 0, 800, 480)
        self.setStyleSheet(STYLE)
        self._worker = None

        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        self.setCentralWidget(root)

        root_layout.addWidget(self._build_status_bar())

        self.stack = QStackedWidget()
        root_layout.addWidget(self.stack)

        self.page_main = self._build_main_menu()
        self.stack.addWidget(self.page_main)
        self._show(self.page_main)

        self._clock = QTimer()
        self._clock.timeout.connect(self._refresh_status)
        self._clock.start(30_000)

    # ── Navigation ────────────────────────────────────────────────────────

    def _push(self, page):
        self.stack.addWidget(page)
        self.stack.setCurrentWidget(page)

    def _show(self, page):
        self.stack.setCurrentWidget(page)

    def _pop(self):
        current = self.stack.currentWidget()
        idx = self.stack.currentIndex()
        if idx > 0:
            self.stack.setCurrentIndex(idx - 1)
        self.stack.removeWidget(current)
        current.deleteLater()

    # ── Shared run helper (called by all page files via self.w._run) ──────

    def _run(self, func, kwargs, log_widget, btn_exec):
        log_widget.append("[*] Running...")
        btn_exec.setEnabled(False)
        self._worker = Worker(func, kwargs)

        # Each line the module emits via log() appears immediately
        self._worker.line_ready.connect(log_widget.append)

        def on_done(error_msg):
            if error_msg:
                log_widget.append(error_msg)
            else:
                log_widget.append("[*] Done.")
            if hasattr(self, "global_log"):
                ts = datetime.now().strftime("%H:%M:%S")
                log_widget_text = log_widget.toPlainText().strip().splitlines()
                last = log_widget_text[-1] if log_widget_text else ""
                self.global_log.append(f"[{ts}] {last[:80]}")
            btn_exec.setEnabled(True)

        self._worker.done.connect(on_done)
        self._worker.start()

    # ── Shared attack list builder (called by all page files) ─────────────

    def _attack_list(self, module_title, attacks):
        """
        Builds a scrollable list of attack buttons and pushes it.
        attacks = [("Button Label", callback_fn), ...]
        """
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(16, 10, 16, 10)
        lay.setSpacing(10)

        lbl = QLabel(module_title)
        lbl.setObjectName("pageTitle")
        lay.addWidget(lbl)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        lay.addWidget(line)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        inner = QWidget()
        inner_lay = QVBoxLayout(inner)
        inner_lay.setSpacing(8)

        for name, callback in attacks:
            btn = QPushButton(name)
            btn.setObjectName("attackBtn")
            btn.setMinimumHeight(60)
            # Use default argument to capture callback value, not reference
            btn.clicked.connect(lambda checked, cb=callback: cb())
            inner_lay.addWidget(btn)

        inner_lay.addStretch()
        scroll.setWidget(inner)
        lay.addWidget(scroll)

        back = QPushButton("BACK")
        back.setObjectName("backBtn")
        back.clicked.connect(lambda: self._show(self.page_main))
        lay.addWidget(back)

        self._push(page)

    # ── Status bar ────────────────────────────────────────────────────────

    def _build_status_bar(self):
        bar = QWidget()
        bar.setObjectName("statusBar")
        bar.setFixedHeight(38)
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(10, 0, 10, 0)

        self.lbl_status = QLabel("SENTINELPI  |  READY")
        self.lbl_status.setObjectName("statusLabel")
        lay.addWidget(self.lbl_status)
        lay.addStretch()

        self.lbl_time = QLabel()
        self.lbl_time.setObjectName("statusRight")
        self._refresh_status()
        lay.addWidget(self.lbl_time)

        # ── Remove these 4 lines to hide the settings button ──
        btn_set = QPushButton("SETTINGS")
        btn_set.setObjectName("settingsBtn")
        btn_set.setFixedHeight(28)
        btn_set.clicked.connect(self._settings_screen)
        lay.addWidget(btn_set)
        # ── end settings button ──

        btn_off = QPushButton("POWER OFF")
        btn_off.setObjectName("dangerBtn")
        btn_off.setFixedHeight(28)
        btn_off.clicked.connect(lambda: subprocess.call(["sudo", "poweroff"]))
        lay.addWidget(btn_off)

        return bar

    def _refresh_status(self):
        now = datetime.now().strftime("%H:%M")
        bat = "N/A"
        try:
            p = "/sys/class/power_supply/BAT0/capacity"
            if os.path.exists(p):
                bat = open(p).read().strip() + "%"
        except Exception:
            pass
        self.lbl_time.setText(f"BAT:{bat}  {now}    ")

    # ── Settings screen ── Remove this whole method if not needed ─────────
    def _settings_screen(self):
        from ui.helpers import CAPTURE_DIR
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(20, 10, 20, 10)
        lay.setSpacing(12)

        lbl = QLabel("SETTINGS")
        lbl.setObjectName("pageTitle")
        lay.addWidget(lbl)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        lay.addWidget(line)

        lay.addWidget(QLabel("Capture folder:", objectName="inputLabel"))
        path_field = QLineEdit(CAPTURE_DIR)
        path_field.setObjectName("inputField")
        lay.addWidget(path_field)

        lay.addStretch()

        back = QPushButton("BACK")
        back.setObjectName("backBtn")
        back.clicked.connect(lambda: self._show(self.page_main))
        lay.addWidget(back)

        self._push(page)
    # ── end settings ─────────────────────────────────────────────────────

    # ── Main menu ─────────────────────────────────────────────────────────

    def _build_main_menu(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(16, 10, 16, 10)
        lay.setSpacing(12)

        lbl = QLabel("SENTINELPI")
        lbl.setObjectName("pageTitle")
        lay.addWidget(lbl)

        # ── Module grid ──
        # To add a new module: add one row here, then create ui/pages/yourmodule.py
        grid = QGridLayout()
        grid.setSpacing(12)
        modules = [
            ("BAD USB",    lambda: BadUSBPage(self).build_menu()),
            ("INFRARED",   lambda: InfraredPage(self).build_menu()),
            ("WIRELESS",   lambda: WirelessPage(self).build_menu()),
            ("NFC / RFID", lambda: NFCPage(self).build_menu()),
        ]
        for i, (label, callback) in enumerate(modules):
            btn = QPushButton(label)
            btn.setObjectName("moduleTile")
            btn.setMinimumHeight(100)
            # Use default argument to capture callback value, not reference
            btn.clicked.connect(lambda checked, cb=callback: cb())
            grid.addWidget(btn, i // 2, i % 2)

        lay.addLayout(grid)
        lay.addStretch()

        # Small activity log at the bottom of the main menu
        self.global_log = QTextEdit()
        self.global_log.setObjectName("logBox")
        self.global_log.setReadOnly(True)
        self.global_log.setFixedHeight(60)
        lay.addWidget(self.global_log)

        return page
