"""
SentinelPi — Base Module Page
All module pages inherit from this.
"""

import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTextEdit, QFrame, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtGui import QTextCursor

from process_manager import process_manager


class _Signaller(QObject):
    output   = pyqtSignal(str)
    finished = pyqtSignal(int)


class BaseModulePage(QWidget):
    PAGE_TITLE    = "MODULE"
    PAGE_SUBTITLE = "description"
    MODULE_KEY    = "module"
    SCRIPT_PATH   = ""

    def __init__(self):
        super().__init__()
        self._sig = _Signaller()
        self._sig.output.connect(self._append_output)
        self._sig.finished.connect(self._on_finished)
        self._build_base_ui()

    def _build_base_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(0)

        # Header
        header = QHBoxLayout()
        title_block = QVBoxLayout()
        title_block.setSpacing(2)
        title = QLabel(self.PAGE_TITLE)
        title.setObjectName("page_title")
        title_block.addWidget(title)
        sub = QLabel(self.PAGE_SUBTITLE.upper())
        sub.setObjectName("page_sub")
        title_block.addWidget(sub)
        header.addLayout(title_block)
        header.addStretch()
        self._status_label = QLabel("● IDLE")
        self._status_label.setObjectName("status_idle")
        self._status_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        header.addWidget(self._status_label)
        root.addLayout(header)
        root.addSpacing(4)

        d = QFrame(); d.setObjectName("divider"); d.setFixedHeight(1)
        root.addWidget(d)
        root.addSpacing(20)

        # Module-specific controls
        self._controls_widget = QWidget()
        controls_layout = QVBoxLayout(self._controls_widget)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(12)
        self._build_controls(controls_layout)
        root.addWidget(self._controls_widget)
        root.addSpacing(20)

        # Start / Stop / Clear row
        btn_row = QHBoxLayout()
        self._btn_start = QPushButton("▶  START")
        self._btn_start.setObjectName("btn_start")
        self._btn_start.setCursor(Qt.PointingHandCursor)
        self._btn_start.clicked.connect(self._start)
        btn_row.addWidget(self._btn_start)

        self._btn_stop = QPushButton("■  STOP")
        self._btn_stop.setObjectName("btn_stop")
        self._btn_stop.setCursor(Qt.PointingHandCursor)
        self._btn_stop.setEnabled(False)
        self._btn_stop.clicked.connect(self._stop)
        btn_row.addWidget(self._btn_stop)

        btn_row.addStretch()

        btn_clear = QPushButton("CLEAR")
        btn_clear.setObjectName("btn_clear")
        btn_clear.setCursor(Qt.PointingHandCursor)
        btn_clear.clicked.connect(self._clear_terminal)
        btn_row.addWidget(btn_clear)
        root.addLayout(btn_row)
        root.addSpacing(16)

        # Terminal
        term_label = QLabel("OUTPUT")
        term_label.setObjectName("section_label")
        root.addWidget(term_label)
        root.addSpacing(6)

        self._terminal = QTextEdit()
        self._terminal.setObjectName("terminal")
        self._terminal.setReadOnly(True)
        self._terminal.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        root.addWidget(self._terminal, 1)

        self._log_system("Module ready. Press START to begin.")

    def _build_controls(self, layout: QVBoxLayout):
        """Override in subclass to add controls above the terminal."""
        pass

    def _get_script_args(self) -> list:
        return []

    def _start(self):
        script = self.SCRIPT_PATH
        if callable(script):
            script = script()
        if not script or not os.path.exists(script):
            self._log_error(f"Script not found: {script}")
            return
        ok, msg = process_manager.start(
            name=self.MODULE_KEY,
            script_path=script,
            args=self._get_script_args(),
            on_output=lambda line: self._sig.output.emit(line),
            on_exit=lambda code: self._sig.finished.emit(code),
        )
        if ok:
            self._log_system(f"Started — {msg}")
            self._set_running(True)
        else:
            self._log_error(f"Failed to start: {msg}")

    def _stop(self):
        process_manager.stop(self.MODULE_KEY)
        self._set_running(False)
        self._log_system("Stopped by user.")

    def _set_running(self, running: bool):
        self._btn_start.setEnabled(not running)
        self._btn_stop.setEnabled(running)
        name = "status_running" if running else "status_idle"
        text = "● RUNNING"       if running else "● IDLE"
        self._status_label.setText(text)
        self._status_label.setObjectName(name)
        self._status_label.style().unpolish(self._status_label)
        self._status_label.style().polish(self._status_label)

    def _append_output(self, line: str):
        self._terminal.append(f"  {line}")
        self._terminal.moveCursor(QTextCursor.End)

    def _log_system(self, msg: str):
        self._terminal.append(f'<span style="color:#444;">── {msg}</span>')
        self._terminal.moveCursor(QTextCursor.End)

    def _log_error(self, msg: str):
        self._terminal.append(f'<span style="color:#ff5522;">✗ {msg}</span>')
        self._terminal.moveCursor(QTextCursor.End)

    def _log_success(self, msg: str):
        self._terminal.append(f'<span style="color:#00ff88;">✓ {msg}</span>')
        self._terminal.moveCursor(QTextCursor.End)

    def _clear_terminal(self):
        self._terminal.clear()
        self._log_system("Terminal cleared.")

    def _on_finished(self, returncode: int):
        if returncode == 0:
            self._log_success("Process completed successfully.")
        elif returncode != -15:  # -15 = SIGTERM (user stopped)
            self._log_error(f"Process exited with code {returncode}.")
        self._set_running(False)
