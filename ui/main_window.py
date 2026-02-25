# ui/main_window.py
# Tuned for 800x480 Raspberry Pi touchscreen.
# Runs fullscreen. Close button in status bar.

import os
import subprocess
from datetime import datetime

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStackedWidget, QScrollArea,
    QFrame, QGridLayout, QLineEdit, QTextEdit, QSizePolicy
)
from PyQt5.QtCore import QTimer, QThread, pyqtSignal, Qt

from ui.pages.badusb    import BadUSBPage
from ui.pages.infrared  import InfraredPage
from ui.pages.wireless  import WirelessPage
from ui.pages.nfc       import NFCPage

# ── All sizes hardcoded for 800x480 ──────────────────────────────────────────
# Status bar:  36px
# Page area:   444px  (480 - 36)
# Margins:     10px each side
# Bottom bar (back/action buttons): always 52px fixed at bottom of each page

STYLE = """
QMainWindow, QWidget {
    background-color: #0d0f0e;
    color: #b8f5c8;
    font-family: 'Courier New', monospace;
    font-size: 14px;
}

/* ── Status bar ── */
#statusBar {
    background-color: #0a0f0b;
    border-bottom: 2px solid #1e3d2a;
}
#statusLabel {
    color: #4caf6e;
    font-size: 13px;
    font-weight: bold;
    letter-spacing: 1px;
}
#statusRight {
    color: #2e7d4f;
    font-size: 12px;
}

/* ── Page title ── */
#pageTitle {
    color: #5dff8f;
    font-size: 17px;
    font-weight: bold;
    letter-spacing: 2px;
}

/* ── Main menu module tiles ── */
#moduleTile {
    background-color: #111714;
    border: 1px solid #1e3d2a;
    border-radius: 6px;
    color: #7dffaa;
    font-size: 16px;
    font-weight: bold;
    letter-spacing: 1px;
}
#moduleTile:pressed { background-color: #1a2e20; border-color: #5dff8f; }

/* ── Attack list buttons ── */
#attackBtn {
    background-color: #0f1a13;
    border: 1px solid #1e3d2a;
    border-radius: 5px;
    color: #9effc0;
    font-size: 14px;
    padding: 0 12px;
    text-align: left;
}
#attackBtn:pressed   { background-color: #172b1e; border-color: #4caf6e; }
#attackBtn:checked   { background-color: #172b1e; border-color: #5dff8f; color: #5dff8f; }

/* ── Bottom action bar buttons ── */
#backBtn {
    background-color: #111411;
    border: 1px solid #1e3d2a;
    border-radius: 5px;
    color: #4caf6e;
    font-size: 13px;
    font-weight: bold;
}
#backBtn:pressed  { background-color: #1a2e20; }

#execBtn {
    background-color: #173a22;
    border: 1px solid #4caf6e;
    border-radius: 5px;
    color: #5dff8f;
    font-size: 14px;
    font-weight: bold;
    letter-spacing: 1px;
}
#execBtn:pressed  { background-color: #1f5030; }
#execBtn:disabled { background-color: #0f1a13; border-color: #1e3d2a; color: #2e7d4f; }

#saveBtn {
    background-color: #0f1a13;
    border: 1px solid #2e7d4f;
    border-radius: 5px;
    color: #4caf6e;
    font-size: 13px;
}
#saveBtn:pressed  { background-color: #172b1e; }

#stopBtn {
    background-color: #1a0d0d;
    border: 1px solid #7d2e2e;
    border-radius: 5px;
    color: #ff6b6b;
    font-size: 14px;
    font-weight: bold;
}
#stopBtn:pressed  { background-color: #2d1515; }
#stopBtn:disabled { background-color: #110808; border-color: #3d1515; color: #5d3030; }

/* ── Status bar buttons ── */
#closeBtn {
    background-color: #1a0d0d;
    border: 1px solid #7d2e2e;
    border-radius: 4px;
    color: #ff6b6b;
    font-size: 12px;
    font-weight: bold;
    padding: 4px 10px;
}
#closeBtn:pressed { background-color: #2d1515; }

#settingsBtn {
    background-color: #111411;
    border: 1px solid #1e3d2a;
    border-radius: 4px;
    color: #4caf6e;
    font-size: 12px;
    padding: 4px 10px;
}
#settingsBtn:pressed { background-color: #1a2e20; }

#powerBtn {
    background-color: #1a0d0d;
    border: 1px solid #5d2020;
    border-radius: 4px;
    color: #cc4444;
    font-size: 12px;
    padding: 4px 10px;
}
#powerBtn:pressed { background-color: #2d1515; }

/* ── Log output box ── */
#logBox {
    background-color: #060d07;
    border: 1px solid #1a3020;
    border-radius: 5px;
    color: #7dffaa;
    font-size: 12px;
    font-family: 'Courier New', monospace;
    padding: 4px;
}

/* ── Text inputs ── */
#inputField {
    background-color: #0f1a13;
    border: 1px solid #2e7d4f;
    border-radius: 5px;
    color: #9effc0;
    font-size: 14px;
    padding: 6px 8px;
    font-family: 'Courier New', monospace;
}
#inputLabel {
    color: #4caf6e;
    font-size: 12px;
}

/* ── Misc ── */
#descLabel  { color: #3d8f5f; font-size: 12px; }
#warnLabel  { color: #cc7700; font-size: 12px; }
QFrame[frameShape="4"] { color: #1a3020; max-height: 1px; }
QScrollArea { border: none; background: transparent; }
QScrollBar:vertical {
    background: #0d0f0e;
    width: 6px;
}
QScrollBar::handle:vertical {
    background: #1e3d2a;
    border-radius: 3px;
}
"""

# ─────────────────────────────────────────────────────────────────────────────
# Worker thread
# ─────────────────────────────────────────────────────────────────────────────
class Worker(QThread):
    line_ready = pyqtSignal(str)
    done       = pyqtSignal(str)

    def __init__(self, func, kwargs=None):
        super().__init__()
        self.func   = func
        self.kwargs = kwargs or {}

    def run(self):
        try:
            self.func(log=self.line_ready.emit, **self.kwargs)
            self.done.emit("")
        except TypeError:
            try:
                out = self.func(**self.kwargs)
                if out:
                    self.line_ready.emit(str(out))
                self.done.emit("")
            except Exception as e:
                self.done.emit(f"[ERROR] {e}")
        except Exception as e:
            self.done.emit(f"[ERROR] {e}")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN WINDOW
# ─────────────────────────────────────────────────────────────────────────────
class MainWindow(QMainWindow):

    # 800x480 layout constants
    STATUS_H  = 36     # status bar height
    PAGE_H    = 444    # 480 - 36
    MARGIN    = 10     # page content margins
    BTN_BAR_H = 52     # fixed bottom button bar on every page
    TILE_H    = 185    # module tile height  (2 rows fit in PAGE_H with title+log)
    ATTACK_H  = 54     # attack list row height
    INPUT_H   = 34     # text input height
    LABEL_H   = 20     # small label height
    DIV_H     = 10     # divider spacing

    def __init__(self):
        super().__init__()
        self.setWindowTitle("SentinelPi")
        self.setStyleSheet(STYLE)
        self._worker = None

        # ── Fullscreen ────────────────────────────────────────────────
        self.showFullScreen()

        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        self.setCentralWidget(root)

        root_layout.addWidget(self._build_status_bar())

        self.stack = QStackedWidget()
        self.stack.setFixedHeight(self.PAGE_H)
        root_layout.addWidget(self.stack)

        self.page_main = self._build_main_menu()
        self.stack.addWidget(self.page_main)
        self._show(self.page_main)

        self._clock = QTimer()
        self._clock.timeout.connect(self._refresh_status)
        self._clock.start(30_000)

    # ── Navigation ────────────────────────────────────────────────────

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

    # ── Run helper ────────────────────────────────────────────────────

    def _run(self, func, kwargs, log_widget, btn_exec):
        log_widget.append("[*] Running...")
        btn_exec.setEnabled(False)
        self._worker = Worker(func, kwargs)
        self._worker.line_ready.connect(log_widget.append)
        def on_done(err):
            if err:
                log_widget.append(err)
            else:
                log_widget.append("[*] Done.")
            if hasattr(self, "global_log"):
                lines = log_widget.toPlainText().strip().splitlines()
                last  = lines[-1] if lines else ""
                ts    = datetime.now().strftime("%H:%M:%S")
                self.global_log.append(f"[{ts}] {last[:90]}")
            btn_exec.setEnabled(True)
        self._worker.done.connect(on_done)
        self._worker.start()

    # ── Attack list page ──────────────────────────────────────────────

    def _attack_list(self, module_title, attacks):
        """
        Scrollable list of attack buttons.
        attacks = [("Name", callback), ...]
        """
        page = QWidget()
        page.setFixedSize(800, self.PAGE_H)
        outer = QVBoxLayout(page)
        outer.setContentsMargins(self.MARGIN, 8, self.MARGIN, 0)
        outer.setSpacing(6)

        # Title
        lbl = QLabel(module_title)
        lbl.setObjectName("pageTitle")
        lbl.setFixedHeight(28)
        outer.addWidget(lbl)

        line = QFrame(); line.setFrameShape(QFrame.HLine)
        outer.addWidget(line)

        # Scrollable button list
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        inner  = QWidget()
        inner_lay = QVBoxLayout(inner)
        inner_lay.setContentsMargins(0, 4, 0, 4)
        inner_lay.setSpacing(6)

        for name, callback in attacks:
            btn = QPushButton(name)
            btn.setObjectName("attackBtn")
            btn.setFixedHeight(self.ATTACK_H)
            btn.clicked.connect(lambda checked, cb=callback: cb())
            inner_lay.addWidget(btn)

        inner_lay.addStretch()
        scroll.setWidget(inner)
        outer.addWidget(scroll)

        # Bottom bar
        outer.addWidget(self._make_bottom_bar([
            self._mk_back(lambda: self._show(self.page_main))
        ]))

        self._push(page)

    # ── Widget factory helpers ─────────────────────────────────────────

    def _mk_back(self, fn=None):
        btn = QPushButton("BACK")
        btn.setObjectName("backBtn")
        btn.clicked.connect(fn if fn else self._pop)
        return btn

    def _mk_exec(self, label="EXECUTE"):
        btn = QPushButton(label)
        btn.setObjectName("execBtn")
        return btn

    def _mk_stop(self, label="STOP"):
        btn = QPushButton(label)
        btn.setObjectName("stopBtn")
        btn.setEnabled(False)
        return btn

    def _mk_save(self, log_widget, name):
        btn = QPushButton("SAVE")
        btn.setObjectName("saveBtn")
        def save():
            from ui.helpers import CAPTURE_DIR
            text = log_widget.toPlainText().strip()
            if not text:
                return
            ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = os.path.join(CAPTURE_DIR, f"{name}_{ts}.txt")
            with open(path, "w") as f:
                f.write(text)
            log_widget.append(f"[*] Saved → {path}")
        btn.clicked.connect(save)
        return btn

    def _make_bottom_bar(self, buttons):
        """Fixed-height bottom bar holding action buttons."""
        bar = QWidget()
        bar.setFixedHeight(self.BTN_BAR_H)
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(0, 6, 0, 6)
        lay.setSpacing(8)
        for b in buttons:
            b.setFixedHeight(40)
            lay.addWidget(b)
        return bar

    def _make_log(self, height):
        box = QTextEdit()
        box.setObjectName("logBox")
        box.setReadOnly(True)
        box.setFixedHeight(height)
        return box

    def _make_input(self, label_text, placeholder="", default=""):
        lbl   = QLabel(label_text)
        lbl.setObjectName("inputLabel")
        lbl.setFixedHeight(self.LABEL_H)
        field = QLineEdit(default)
        field.setObjectName("inputField")
        field.setPlaceholderText(placeholder)
        field.setFixedHeight(self.INPUT_H)
        return lbl, field

    def _make_divider(self):
        f = QFrame(); f.setFrameShape(QFrame.HLine)
        return f

    def _make_title(self, text):
        lbl = QLabel(text)
        lbl.setObjectName("pageTitle")
        lbl.setFixedHeight(28)
        return lbl

    # ── Status bar ────────────────────────────────────────────────────

    def _build_status_bar(self):
        bar = QWidget()
        bar.setObjectName("statusBar")
        bar.setFixedHeight(self.STATUS_H)
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(10, 0, 10, 0)
        lay.setSpacing(8)

        self.lbl_status = QLabel("SENTINELPI")
        self.lbl_status.setObjectName("statusLabel")
        lay.addWidget(self.lbl_status)

        lay.addStretch()

        self.lbl_time = QLabel()
        self.lbl_time.setObjectName("statusRight")
        self._refresh_status()
        lay.addWidget(self.lbl_time)

        # ── Remove these 4 lines to remove settings ──
        btn_set = QPushButton("SETTINGS")
        btn_set.setObjectName("settingsBtn")
        btn_set.setFixedHeight(26)
        btn_set.clicked.connect(self._settings_screen)
        lay.addWidget(btn_set)
        # ────────────────────────────────────────────

        btn_pwr = QPushButton("POWER OFF")
        btn_pwr.setObjectName("powerBtn")
        btn_pwr.setFixedHeight(26)
        btn_pwr.clicked.connect(lambda: subprocess.call(["sudo", "poweroff"]))
        lay.addWidget(btn_pwr)

        btn_close = QPushButton("CLOSE")
        btn_close.setObjectName("closeBtn")
        btn_close.setFixedHeight(26)
        btn_close.clicked.connect(self.close)
        lay.addWidget(btn_close)

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
        self.lbl_time.setText(f"BAT:{bat}  {now}  ")

    # ── Settings ── Remove this method if not needed ───────────────────
    def _settings_screen(self):
        from ui.helpers import CAPTURE_DIR
        page = QWidget()
        page.setFixedSize(800, self.PAGE_H)
        lay = QVBoxLayout(page)
        lay.setContentsMargins(self.MARGIN, 8, self.MARGIN, 0)
        lay.setSpacing(6)

        lay.addWidget(self._make_title("SETTINGS"))
        lay.addWidget(self._make_divider())

        lbl, f = self._make_input("Capture folder", CAPTURE_DIR, CAPTURE_DIR)
        lay.addWidget(lbl); lay.addWidget(f)
        lay.addStretch()

        lay.addWidget(self._make_bottom_bar([
            self._mk_back(lambda: self._show(self.page_main))
        ]))
        self._push(page)
    # ──────────────────────────────────────────────────────────────────

    # ══ MAIN MENU ═════════════════════════════════════════════════════

    def _build_main_menu(self):
        page = QWidget()
        page.setFixedSize(800, self.PAGE_H)
        lay = QVBoxLayout(page)
        lay.setContentsMargins(self.MARGIN, 8, self.MARGIN, 8)
        lay.setSpacing(8)

        lay.addWidget(self._make_title("SENTINELPI"))

        # 2x2 grid — each tile fills available height evenly
        grid = QGridLayout()
        grid.setSpacing(8)

        # To add a module: add one entry here + create ui/pages/yourmodule.py
        modules = [
            ("BAD USB",    lambda: BadUSBPage(self).build_menu()),
            ("INFRARED",   lambda: InfraredPage(self).build_menu()),
            ("WIRELESS",   lambda: WirelessPage(self).build_menu()),
            ("NFC / RFID", lambda: NFCPage(self).build_menu()),
        ]
        for i, (label, cb) in enumerate(modules):
            btn = QPushButton(label)
            btn.setObjectName("moduleTile")
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            btn.clicked.connect(lambda checked, c=cb: c())
            grid.addWidget(btn, i // 2, i % 2)

        # Give both rows equal stretch
        grid.setRowStretch(0, 1)
        grid.setRowStretch(1, 1)

        lay.addLayout(grid, stretch=1)

        # Small activity log at the bottom
        self.global_log = QTextEdit()
        self.global_log.setObjectName("logBox")
        self.global_log.setReadOnly(True)
        self.global_log.setFixedHeight(52)
        lay.addWidget(self.global_log)

        return page
