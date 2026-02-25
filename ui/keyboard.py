# ui/keyboard.py
# Onscreen keyboard manager.
# Supports matchbox-keyboard (X11) and squeekboard (Wayland).
# Called automatically when any input field is focused.

import subprocess
import os

# Auto-detect which keyboard to use based on session type
_SESSION = os.environ.get("XDG_SESSION_TYPE", "x11").lower()
_kb_proc = None


def show():
    """Show the onscreen keyboard."""
    global _kb_proc
    if _kb_proc and _kb_proc.poll() is None:
        return  # already running

    try:
        if _SESSION == "wayland":
            # squeekboard shows itself automatically on Wayland when an
            # input field is focused — nothing to launch manually.
            # If it's not appearing, run: sudo apt install squeekboard
            pass
        else:
            # X11 — launch matchbox-keyboard
            # sudo apt install matchbox-keyboard
            _kb_proc = subprocess.Popen(
                ["matchbox-keyboard"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
    except FileNotFoundError:
        # matchbox-keyboard not installed — silently ignore
        pass


def hide():
    """Hide the onscreen keyboard."""
    global _kb_proc
    if _kb_proc and _kb_proc.poll() is None:
        _kb_proc.terminate()
        _kb_proc = None


def toggle():
    if _kb_proc and _kb_proc.poll() is None:
        hide()
    else:
        show()


# ─────────────────────────────────────────────────────────────────────────────
# Drop-in widget replacements — use these instead of QLineEdit / QTextEdit
# and the keyboard appears/disappears automatically on focus.
# ─────────────────────────────────────────────────────────────────────────────

from PyQt5.QtWidgets import QLineEdit, QTextEdit
from PyQt5.QtCore import Qt


class KeyboardLineEdit(QLineEdit):
    """QLineEdit that shows the onscreen keyboard when tapped."""
    def focusInEvent(self, event):
        super().focusInEvent(event)
        show()

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        hide()


class KeyboardTextEdit(QTextEdit):
    """QTextEdit that shows the onscreen keyboard when tapped."""
    def focusInEvent(self, event):
        super().focusInEvent(event)
        show()

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        hide()
