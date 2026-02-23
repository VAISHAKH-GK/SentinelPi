"""
SentinelPi — Base Module Page (Touchscreen)
No navigate_fn. Uses pyqtSignal back_requested instead.
All touch targets >= 44px.
"""

import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTextEdit, QFrame, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtGui import QTextCursor

from process_manager import process_manager


class _Sig(QObject):
    output   = pyqtSignal(str)
    finished = pyqtSignal(int)


class BaseModulePage(QWidget):
    back_requested = pyqtSignal()

    PAGE_TITLE = "MODULE"
    PAGE_CHIP  = "HARDWARE"
    MODULE_KEY = "module"

    def __init__(self):
        super().__init__()
        self.setObjectName("module_page")
        self._sig = _Sig()
        self._sig.output.connect(self._append_output)
        self._sig.finished.connect(self._on_finished)
        self._build_base()

    def _build_base(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 10, 12, 10)
        root.setSpacing(8)

        # Header
        header = QHBoxLayout(); header.setSpacing(10)
        btn_back = QPushButton("←")
        btn_back.setObjectName("btn_back")
        btn_back.setFixedSize(44, 44)
        btn_back.setCursor(Qt.PointingHandCursor)
        btn_back.clicked.connect(self.back_requested.emit)
        header.addWidget(btn_back)

        title_col = QVBoxLayout(); title_col.setSpacing(1)
        t = QLabel(self.PAGE_TITLE);  t.setObjectName("page_title");  title_col.addWidget(t)
        c = QLabel(self.PAGE_CHIP);   c.setObjectName("page_chip");   title_col.addWidget(c)
        header.addLayout(title_col)
        header.addStretch()

        self._status_label = QLabel("● IDLE")
        self._status_label.setObjectName("status_idle")
        header.addWidget(self._status_label)
        root.addLayout(header)

        div = QFrame(); div.setObjectName("divider"); div.setFixedHeight(1)
        root.addWidget(div)

        # Mode bar
        mode_row = QHBoxLayout(); mode_row.setSpacing(6)
        self._build_mode_bar(mode_row)
        if mode_row.count() > 0:
            root.addLayout(mode_row)

        # Controls
        ctrl = QWidget()
        ctrl_layout = QVBoxLayout(ctrl)
        ctrl_layout.setContentsMargins(0, 0, 0, 0)
        ctrl_layout.setSpacing(8)
        self._build_controls(ctrl_layout)
        root.addWidget(ctrl)

        # Action row
        action = QHBoxLayout(); action.setSpacing(8)

        self._btn_start = QPushButton("▶  START")
        self._btn_start.setObjectName("btn_start")
        self._btn_start.setFixedHeight(52)
        self._btn_start.setCursor(Qt.PointingHandCursor)
        self._btn_start.clicked.connect(self._start)
        action.addWidget(self._btn_start, 3)

        self._btn_stop = QPushButton("■  STOP")
        self._btn_stop.setObjectName("btn_stop")
        self._btn_stop.setFixedHeight(52)
        self._btn_stop.setEnabled(False)
        self._btn_stop.setCursor(Qt.PointingHandCursor)
        self._btn_stop.clicked.connect(self._stop)
        action.addWidget(self._btn_stop, 3)

        btn_clr = QPushButton("CLR")
        btn_clr.setObjectName("btn_clear")
        btn_clr.setFixedHeight(52)
        btn_clr.setFixedWidth(58)
        btn_clr.setCursor(Qt.PointingHandCursor)
        btn_clr.clicked.connect(self._clear)
        action.addWidget(btn_clr)
        root.addLayout(action)

        out_lbl = QLabel("OUTPUT"); out_lbl.setObjectName("section_label")
        root.addWidget(out_lbl)

        self._terminal = QTextEdit()
        self._terminal.setObjectName("terminal")
        self._terminal.setReadOnly(True)
        self._terminal.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        root.addWidget(self._terminal, 1)

        self._log_sys("Ready — tap START to begin.")

    def _build_mode_bar(self, layout): pass
    def _build_controls(self, layout): pass
    def _get_script_args(self): return []
    def SCRIPT_PATH(self): return ""

    def _start(self):
        path = self.SCRIPT_PATH() if callable(self.SCRIPT_PATH) else self.SCRIPT_PATH
        if not path or not os.path.exists(path):
            self._log_err(f"Script not found: {path}"); return
        ok, msg = process_manager.start(
            name=self.MODULE_KEY, script_path=path, args=self._get_script_args(),
            on_output=lambda l: self._sig.output.emit(l),
            on_exit=lambda c: self._sig.finished.emit(c),
        )
        if ok:
            self._log_sys(f"Started — {msg}"); self._set_running(True)
        else:
            self._log_err(f"Failed: {msg}")

    def _stop(self):
        process_manager.stop(self.MODULE_KEY)
        self._set_running(False); self._log_sys("Stopped.")

    def _set_running(self, running):
        self._btn_start.setEnabled(not running)
        self._btn_stop.setEnabled(running)
        obj  = "status_running" if running else "status_idle"
        text = "● RUNNING"      if running else "● IDLE"
        self._status_label.setText(text)
        self._status_label.setObjectName(obj)
        self._status_label.style().unpolish(self._status_label)
        self._status_label.style().polish(self._status_label)

    def _append_output(self, line):
        self._terminal.append(f"  {line}")
        self._terminal.moveCursor(QTextCursor.End)

    def _log_sys(self, msg):
        self._terminal.append(f'<span style="color:#2a2a2a;">── {msg}</span>')
        self._terminal.moveCursor(QTextCursor.End)

    def _log_err(self, msg):
        self._terminal.append(f'<span style="color:#ff5522;">✗ {msg}</span>')
        self._terminal.moveCursor(QTextCursor.End)

    def _log_ok(self, msg):
        self._terminal.append(f'<span style="color:#00ff88;">✓ {msg}</span>')
        self._terminal.moveCursor(QTextCursor.End)

    def _clear(self):
        self._terminal.clear(); self._log_sys("Cleared.")

    def _on_finished(self, code):
        if code == 0: self._log_ok("Done.")
        elif code != -15: self._log_err(f"Exited with code {code}.")
        self._set_running(False)

    def _lbl(self, text):
        l = QLabel(text); l.setObjectName("section_label"); return l

    def _make_mode_btn(self, label, callback):
        btn = QPushButton(label)
        btn.setObjectName("mode_btn")
        btn.setFixedHeight(40)
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(callback)
        return btn

    def _activate_mode_btn(self, active_btn, all_btns):
        for btn in all_btns:
            btn.setProperty("active", "true" if btn is active_btn else "false")
            btn.style().unpolish(btn); btn.style().polish(btn)
