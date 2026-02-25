# ui/helpers.py
# Shared widget helpers used by all page files.
# All sizes are tuned for 800x480.

import os
from datetime import datetime
from PyQt5.QtWidgets import (
    QPushButton, QTextEdit, QLabel, QLineEdit, QFrame, QHBoxLayout
)
from ui.keyboard import KeyboardLineEdit

CAPTURE_DIR = os.path.expanduser("~/SentinelPi/captures")
os.makedirs(CAPTURE_DIR, exist_ok=True)

# ── Size constants (match main_window.py) ─────────────────────────────────────
BTN_H    = 40    # action buttons in bottom bar
INPUT_H  = 34    # text input fields
LABEL_H  = 20    # input labels
ATTACK_H = 54    # attack list rows


def title(text):
    lbl = QLabel(text)
    lbl.setObjectName("pageTitle")
    lbl.setFixedHeight(28)
    return lbl


def divider():
    line = QFrame()
    line.setFrameShape(QFrame.HLine)
    return line


def desc(text):
    lbl = QLabel(text)
    lbl.setObjectName("descLabel")
    lbl.setWordWrap(True)
    lbl.setFixedHeight(18)
    return lbl


def warn(text):
    lbl = QLabel(text)
    lbl.setObjectName("warnLabel")
    lbl.setWordWrap(True)
    lbl.setFixedHeight(18)
    return lbl


def log_box(height=120):
    box = QTextEdit()
    box.setObjectName("logBox")
    box.setReadOnly(True)
    box.setFixedHeight(height)
    return box


def input_field(label_text, placeholder="", default=""):
    """Returns (QLabel, QLineEdit) both with fixed heights."""
    lbl = QLabel(label_text)
    lbl.setObjectName("inputLabel")
    lbl.setFixedHeight(LABEL_H)
    field = KeyboardLineEdit(default)
    field.setObjectName("inputField")
    field.setPlaceholderText(placeholder)
    field.setFixedHeight(INPUT_H)
    return lbl, field


def exec_btn(label="EXECUTE"):
    btn = QPushButton(label)
    btn.setObjectName("execBtn")
    btn.setFixedHeight(BTN_H)
    return btn


def stop_btn(label="STOP"):
    btn = QPushButton(label)
    btn.setObjectName("stopBtn")
    btn.setFixedHeight(BTN_H)
    btn.setEnabled(False)
    return btn


def save_btn(log_widget, name):
    btn = QPushButton("SAVE")
    btn.setObjectName("saveBtn")
    btn.setFixedHeight(BTN_H)
    def save():
        text = log_widget.toPlainText().strip()
        if not text:
            return
        ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe = name.lower().replace(" ", "_")
        path = os.path.join(CAPTURE_DIR, f"{safe}_{ts}.txt")
        with open(path, "w") as f:
            f.write(text)
        log_widget.append(f"[*] Saved → {path}")
    btn.clicked.connect(save)
    return btn


def back_btn(navigate_fn):
    btn = QPushButton("BACK")
    btn.setObjectName("backBtn")
    btn.setFixedHeight(BTN_H)
    btn.clicked.connect(navigate_fn)
    return btn


def bottom_bar(*buttons):
    """
    Fixed-height 52px bar for action buttons at the bottom of every page.
    Pass button widgets as arguments.
    """
    bar = QFrame()
    bar.setFixedHeight(52)
    lay = QHBoxLayout(bar)
    lay.setContentsMargins(0, 6, 0, 6)
    lay.setSpacing(8)
    for b in buttons:
        b.setFixedHeight(BTN_H)
        lay.addWidget(b)
    return bar
