# ui/helpers.py
# Shared widgets and utilities used across all pages.
# Import from here in every page file.

import os
from datetime import datetime
from PyQt5.QtWidgets import (
    QPushButton, QTextEdit, QLabel, QLineEdit, QFrame, QHBoxLayout
)

CAPTURE_DIR = os.path.expanduser("~/SentinelPi/captures")
os.makedirs(CAPTURE_DIR, exist_ok=True)


def title(text):
    lbl = QLabel(text)
    lbl.setObjectName("pageTitle")
    return lbl


def divider():
    line = QFrame()
    line.setFrameShape(QFrame.HLine)
    return line


def desc(text):
    lbl = QLabel(text)
    lbl.setObjectName("descLabel")
    lbl.setWordWrap(True)
    return lbl


def log_box(height=None):
    box = QTextEdit()
    box.setObjectName("logBox")
    box.setReadOnly(True)
    if height:
        box.setFixedHeight(height)
    return box


def input_field(label_text, placeholder="", default=""):
    """Returns (QLabel, QLineEdit)."""
    lbl = QLabel(label_text)
    lbl.setObjectName("inputLabel")
    field = QLineEdit(default)
    field.setObjectName("inputField")
    field.setPlaceholderText(placeholder)
    return lbl, field


def exec_btn(label="EXECUTE"):
    btn = QPushButton(label)
    btn.setObjectName("execBtn")
    btn.setMinimumHeight(52)
    return btn


def stop_btn(label="STOP"):
    btn = QPushButton(label)
    btn.setObjectName("stopBtn")
    btn.setMinimumHeight(52)
    btn.setEnabled(False)
    return btn


def save_btn(log_widget, name):
    btn = QPushButton("SAVE")
    btn.setObjectName("saveBtn")

    def save():
        text = log_widget.toPlainText().strip()
        if not text:
            return
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe = name.lower().replace(" ", "_")
        path = os.path.join(CAPTURE_DIR, f"{safe}_{ts}.txt")
        with open(path, "w") as f:
            f.write(text)
        log_widget.append(f"[*] Saved to {path}")

    btn.clicked.connect(save)
    return btn


def back_btn(navigate_fn):
    """navigate_fn is a callable — either window._pop or lambda: window._show(page)."""
    btn = QPushButton("BACK")
    btn.setObjectName("backBtn")
    btn.clicked.connect(navigate_fn)
    return btn


def btn_row(*buttons):
    """Pack buttons into a horizontal row layout."""
    row = QHBoxLayout()
    row.setSpacing(8)
    for b in buttons:
        row.addWidget(b)
    return row
