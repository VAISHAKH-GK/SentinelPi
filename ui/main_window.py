import os
import subprocess
from datetime import datetime
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLabel, QStackedWidget,
    QLineEdit, QFrame, QGridLayout, QScrollArea, QSizePolicy
)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QColor

# Import modules
from modules.badusb import custom_script, reverse_shell, send_payload
from modules.infrared import ir_bruteforce, ir_capture, ir_relay, ir_transmission
from modules.wireless import channel_scan, jammer, packet_sniff, replay
from modules.nfc import clone, emulate, read, write

# ── Where captured data is saved ──────────────────────────────────────────────
CAPTURE_DIR = os.path.expanduser("~/SentinelPi/captures")
os.makedirs(CAPTURE_DIR, exist_ok=True)

STYLE = """
QMainWindow, QWidget {
    background-color: #0d0f0e;
    color: #b8f5c8;
    font-family: 'Courier New', monospace;
}

/* ── Status Bar ── */
#statusBar {
    background-color: #111411;
    border-bottom: 1px solid #1e3d2a;
    padding: 4px 12px;
}
#statusLabel {
    color: #4caf6e;
    font-size: 13px;
}
#statusRight {
    color: #2e7d4f;
    font-size: 13px;
}

/* ── Page title ── */
#pageTitle {
    color: #5dff8f;
    font-size: 22px;
    font-weight: bold;
    letter-spacing: 3px;
    padding: 10px 0 4px 0;
}

/* ── Module tile buttons (main menu) ── */
#moduleTile {
    background-color: #111714;
    border: 1px solid #1e3d2a;
    border-radius: 8px;
    color: #7dffaa;
    font-size: 18px;
    font-weight: bold;
    letter-spacing: 2px;
    padding: 28px 12px;
    text-align: center;
}
#moduleTile:pressed {
    background-color: #1a2e20;
    border-color: #4caf6e;
}

/* ── Attack list buttons ── */
#attackBtn {
    background-color: #0f1a13;
    border: 1px solid #1e3d2a;
    border-radius: 6px;
    color: #9effc0;
    font-size: 16px;
    padding: 18px 16px;
    text-align: left;
}
#attackBtn:pressed {
    background-color: #172b1e;
    border-color: #4caf6e;
}

/* ── Back button ── */
#backBtn {
    background-color: #111411;
    border: 1px solid #1e3d2a;
    border-radius: 6px;
    color: #4caf6e;
    font-size: 14px;
    padding: 10px 20px;
    max-width: 100px;
}
#backBtn:pressed {
    background-color: #1a2e20;
}

/* ── Execute / action buttons ── */
#execBtn {
    background-color: #173a22;
    border: 1px solid #4caf6e;
    border-radius: 6px;
    color: #5dff8f;
    font-size: 16px;
    font-weight: bold;
    padding: 16px;
    letter-spacing: 1px;
}
#execBtn:pressed {
    background-color: #1f5030;
}

/* ── Save button ── */
#saveBtn {
    background-color: #0f1a13;
    border: 1px solid #2e7d4f;
    border-radius: 6px;
    color: #4caf6e;
    font-size: 14px;
    padding: 10px 16px;
}
#saveBtn:pressed {
    background-color: #172b1e;
}

/* ── Danger/power button ── */
#dangerBtn {
    background-color: #1a0d0d;
    border: 1px solid #7d2e2e;
    border-radius: 6px;
    color: #ff6b6b;
    font-size: 13px;
    padding: 8px 14px;
}
#dangerBtn:pressed {
    background-color: #2d1515;
}

/* ── Settings button ── */
#settingsBtn {
    background-color: #111411;
    border: 1px solid #1e3d2a;
    border-radius: 6px;
    color: #4caf6e;
    font-size: 13px;
    padding: 8px 14px;
}
#settingsBtn:pressed {
    background-color: #1a2e20;
}

/* ── Output log ── */
#logBox {
    background-color: #080f0a;
    border: 1px solid #1e3d2a;
    border-radius: 6px;
    color: #7dffaa;
    font-size: 13px;
    font-family: 'Courier New', monospace;
    padding: 6px;
}

/* ── Text input ── */
#inputField {
    background-color: #0f1a13;
    border: 1px solid #2e7d4f;
    border-radius: 6px;
    color: #9effc0;
    font-size: 15px;
    padding: 10px;
    font-family: 'Courier New', monospace;
}

/* ── Divider ── */
QFrame[frameShape="4"] {
    color: #1e3d2a;
}

/* ── Attack title on exec screen ── */
#attackTitle {
    color: #5dff8f;
    font-size: 18px;
    font-weight: bold;
    letter-spacing: 2px;
}

/* ── Description label ── */
#descLabel {
    color: #4caf6e;
    font-size: 13px;
}
"""

# ─────────────────────────────────────────────────────────────────────────────
# Worker thread so the UI doesn't freeze during module execution
# ─────────────────────────────────────────────────────────────────────────────
class ModuleWorker(QThread):
    result = pyqtSignal(str)

    def __init__(self, func, kwargs=None):
        super().__init__()
        self.func = func
        self.kwargs = kwargs or {}

    def run(self):
        try:
            out = self.func(**self.kwargs)
            self.result.emit(str(out))
        except Exception as e:
            self.result.emit(f"[ERROR] {e}")


# ─────────────────────────────────────────────────────────────────────────────
# MODULES DEFINITION
# Each module: { "label": str, "attacks": [ { "name", "desc", "func", "inputs"? } ] }
# inputs: list of {"label": str, "key": str, "default": str}
# ─────────────────────────────────────────────────────────────────────────────
MODULES = [
    {
        "label": "BAD USB",
        "icon": "⚡",
        "attacks": [
            {"name": "Custom Script",  "desc": "Run a custom HID script on the target.",
             "func": custom_script.run,  "saves": False},
            {"name": "Reverse Shell",  "desc": "Simulate reverse shell injection (demo).",
             "func": reverse_shell.run, "saves": False},
            {"name": "Send Payload",   "desc": "Inject a predefined payload (demo).",
             "func": send_payload.run,  "saves": False},
        ]
    },
    {
        "label": "INFRARED",
        "icon": "📡",
        "attacks": [
            {"name": "IR Capture",      "desc": "Capture an IR signal from a remote.",
             "func": ir_capture.run,      "saves": True},
            {"name": "IR Transmission", "desc": "Transmit a saved or raw IR signal.",
             "func": ir_transmission.run, "saves": False},
            {"name": "IR Relay",        "desc": "Relay captured IR signal in real-time.",
             "func": ir_relay.run,        "saves": False},
            {"name": "IR Bruteforce",   "desc": "Bruteforce IR codes against a device.",
             "func": ir_bruteforce.run,   "saves": True},
        ]
    },
    {
        "label": "WIRELESS",
        "icon": "📶",
        "attacks": [
            {"name": "Channel Scan",  "desc": "Scan 2.4 GHz channels for activity.",
             "func": channel_scan.run, "saves": True},
            {"name": "Packet Sniff",  "desc": "Capture wireless packets (demo).",
             "func": packet_sniff.run, "saves": True},
            {"name": "Replay Attack", "desc": "Replay a captured wireless packet.",
             "func": replay.run,       "saves": False},
            {"name": "Jammer",        "desc": "Flood a channel with noise (demo).",
             "func": jammer.run,       "saves": False},
        ]
    },
    {
        "label": "NFC / RFID",
        "icon": "🔖",
        "attacks": [
            {"name": "Read Tag",   "desc": "Read data from an NFC/RFID tag.",
             "func": read.run,    "saves": True},
            {"name": "Clone Tag",  "desc": "Clone a tag to a writable blank.",
             "func": clone.run,   "saves": True},
            {"name": "Emulate",    "desc": "Emulate a stored tag.",
             "func": emulate.run, "saves": False},
            {"name": "Write Tag",  "desc": "Write custom data to an NFC tag.",
             "func": write.run,   "saves": False},
        ]
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# MAIN WINDOW
# ─────────────────────────────────────────────────────────────────────────────
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SentinelPi")
        self.setGeometry(0, 0, 800, 480)   # typical 7" display resolution
        self.setStyleSheet(STYLE)

        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        self.setCentralWidget(root)

        # ── Status bar (always visible) ───────────────────────────────────
        root_layout.addWidget(self._build_status_bar())

        # ── Page stack ───────────────────────────────────────────────────
        self.stack = QStackedWidget()
        root_layout.addWidget(self.stack)

        # Build pages
        self.page_main = self._build_main_menu()
        self.stack.addWidget(self.page_main)

        self._show(self.page_main)

        # Clock / battery refresh timer
        self._timer = QTimer()
        self._timer.timeout.connect(self._refresh_status)
        self._timer.start(30_000)   # every 30 s

    # ── Status bar ────────────────────────────────────────────────────────
    def _build_status_bar(self):
        bar = QWidget()
        bar.setObjectName("statusBar")
        bar.setFixedHeight(38)
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(10, 0, 10, 0)

        self.lbl_status = QLabel("◉ SENTINEL PI  |  READY")
        self.lbl_status.setObjectName("statusLabel")
        layout.addWidget(self.lbl_status)

        layout.addStretch()

        self.lbl_time = QLabel()
        self.lbl_time.setObjectName("statusRight")
        self._refresh_status()
        layout.addWidget(self.lbl_time)

        # ── Settings button (easy to remove: just delete these 3 lines) ──
        btn_settings = QPushButton("⚙")
        btn_settings.setObjectName("settingsBtn")
        btn_settings.setFixedSize(40, 28)
        btn_settings.clicked.connect(self._open_settings)
        layout.addWidget(btn_settings)
        # ── end settings button ──

        btn_power = QPushButton("⏻")
        btn_power.setObjectName("dangerBtn")
        btn_power.setFixedSize(40, 28)
        btn_power.clicked.connect(self._power_off)
        layout.addWidget(btn_power)

        return bar

    def _refresh_status(self):
        now = datetime.now().strftime("%H:%M")
        battery = self._read_battery()
        self.lbl_time.setText(f"🔋{battery}  {now}  ")

    def _read_battery(self):
        """Read Raspberry Pi battery percent if available, else show N/A."""
        try:
            path = "/sys/class/power_supply/BAT0/capacity"
            if os.path.exists(path):
                with open(path) as f:
                    return f.read().strip() + "%"
        except Exception:
            pass
        return "N/A"

    def _power_off(self):
        self._log_global("[SYSTEM] Shutting down...")
        subprocess.call(["sudo", "poweroff"])

    # ─── Settings (remove this whole method + the 3 lines above if not needed) ─
    def _open_settings(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(12)

        layout.addWidget(self._title("SETTINGS"))
        layout.addWidget(self._divider())

        # Placeholder setting items — add real ones here
        layout.addWidget(QLabel("Capture folder: " + CAPTURE_DIR))
        layout.addStretch()

        layout.addWidget(self._back_btn(self.page_main))
        self._push(page)
    # ─── end settings ──────────────────────────────────────────────────────

    # ── Main menu ─────────────────────────────────────────────────────────
    def _build_main_menu(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(16, 10, 16, 10)
        layout.setSpacing(12)

        layout.addWidget(self._title("[ SENTINELPI ]"))

        grid = QGridLayout()
        grid.setSpacing(12)
        for i, mod in enumerate(MODULES):
            btn = QPushButton(f"{mod['icon']}\n{mod['label']}")
            btn.setObjectName("moduleTile")
            btn.setMinimumHeight(100)
            btn.clicked.connect(lambda _, m=mod: self._open_module(m))
            grid.addWidget(btn, i // 2, i % 2)

        layout.addLayout(grid)
        layout.addStretch()

        self.global_log = QTextEdit()
        self.global_log.setObjectName("logBox")
        self.global_log.setReadOnly(True)
        self.global_log.setFixedHeight(70)
        layout.addWidget(self.global_log)
        return page

    def _log_global(self, text):
        ts = datetime.now().strftime("%H:%M:%S")
        self.global_log.append(f"[{ts}] {text}")

    # ── Module attack list ─────────────────────────────────────────────────
    def _open_module(self, mod):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(16, 10, 16, 10)
        layout.setSpacing(10)

        layout.addWidget(self._title(f"{mod['icon']}  {mod['label']}"))
        layout.addWidget(self._divider())

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        inner = QWidget()
        inner_layout = QVBoxLayout(inner)
        inner_layout.setSpacing(8)

        for attack in mod["attacks"]:
            btn = QPushButton(f"  {attack['name']}\n  {attack['desc']}")
            btn.setObjectName("attackBtn")
            btn.setMinimumHeight(64)
            btn.clicked.connect(lambda _, a=attack: self._open_attack(a))
            inner_layout.addWidget(btn)

        inner_layout.addStretch()
        scroll_area.setWidget(inner)
        layout.addWidget(scroll_area)

        layout.addWidget(self._back_btn(self.page_main))
        self._push(page)

    # ── Attack execution screen ────────────────────────────────────────────
    def _open_attack(self, attack):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(16, 10, 16, 10)
        layout.setSpacing(10)

        # Title + description
        lbl_title = QLabel(attack["name"])
        lbl_title.setObjectName("attackTitle")
        layout.addWidget(lbl_title)

        lbl_desc = QLabel(attack["desc"])
        lbl_desc.setObjectName("descLabel")
        lbl_desc.setWordWrap(True)
        layout.addWidget(lbl_desc)
        layout.addWidget(self._divider())

        # Optional user inputs — add entries to attack dict like:
        # "inputs": [{"label": "Target Channel", "key": "channel", "default": "1"}]
        input_widgets = {}
        for inp in attack.get("inputs", []):
            lbl = QLabel(inp["label"])
            lbl.setObjectName("descLabel")
            layout.addWidget(lbl)
            field = QLineEdit(inp.get("default", ""))
            field.setObjectName("inputField")
            layout.addWidget(field)
            input_widgets[inp["key"]] = field

        # Output log
        log = QTextEdit()
        log.setObjectName("logBox")
        log.setReadOnly(True)
        layout.addWidget(log)

        # Button row
        btn_row = QHBoxLayout()

        btn_exec = QPushButton("▶  EXECUTE")
        btn_exec.setObjectName("execBtn")

        def run_attack():
            kwargs = {k: w.text() for k, w in input_widgets.items()}
            log.append("[*] Running...")
            btn_exec.setEnabled(False)
            self._worker = ModuleWorker(attack["func"], kwargs)
            self._worker.result.connect(lambda r: self._on_result(r, log, attack, btn_exec))
            self._worker.start()

        btn_exec.clicked.connect(run_attack)
        btn_row.addWidget(btn_exec)

        if attack.get("saves"):
            btn_save = QPushButton("💾  SAVE")
            btn_save.setObjectName("saveBtn")
            btn_save.clicked.connect(lambda: self._save_result(log.toPlainText(), attack["name"]))
            btn_row.addWidget(btn_save)

        layout.addLayout(btn_row)
        layout.addWidget(self._back_btn(None))   # back to previous page

        self._push(page)

    def _on_result(self, result, log, attack, btn_exec):
        log.append(result)
        self._log_global(f"{attack['name']}: {result[:60]}")
        btn_exec.setEnabled(True)

    def _save_result(self, text, name):
        if not text.strip():
            return
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = name.lower().replace(" ", "_")
        path = os.path.join(CAPTURE_DIR, f"{safe_name}_{ts}.txt")
        with open(path, "w") as f:
            f.write(text)
        self._log_global(f"Saved → {path}")

    # ── Helpers ───────────────────────────────────────────────────────────
    def _title(self, text):
        lbl = QLabel(text)
        lbl.setObjectName("pageTitle")
        return lbl

    def _divider(self):
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        return line

    def _back_btn(self, target_page):
        """If target_page is None, pops the stack. Otherwise goes to target."""
        btn = QPushButton("← BACK")
        btn.setObjectName("backBtn")
        if target_page:
            btn.clicked.connect(lambda: self._show(target_page))
        else:
            btn.clicked.connect(self._pop)
        return btn

    def _show(self, page):
        self.stack.setCurrentWidget(page)

    def _push(self, page):
        self.stack.addWidget(page)
        self.stack.setCurrentWidget(page)

    def _pop(self):
        current = self.stack.currentWidget()
        index = self.stack.currentIndex()
        if index > 0:
            self.stack.setCurrentIndex(index - 1)
        self.stack.removeWidget(current)
        current.deleteLater()
