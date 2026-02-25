import os
import subprocess
from datetime import datetime
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLabel, QStackedWidget,
    QLineEdit, QFrame, QGridLayout, QScrollArea
)
from PyQt5.QtCore import QTimer, QThread, pyqtSignal

from modules.badusb import custom_script, reverse_shell, send_payload
from modules.infrared import ir_bruteforce, ir_capture, ir_relay, ir_transmission
from modules.wireless import channel_scan, jammer, packet_sniff, replay
from modules.nfc import clone, emulate, read, write

CAPTURE_DIR = os.path.expanduser("~/SentinelPi/captures")
os.makedirs(CAPTURE_DIR, exist_ok=True)

STYLE = """
QMainWindow, QWidget {
    background-color: #0d0f0e;
    color: #b8f5c8;
    font-family: 'Courier New', monospace;
}
#statusBar {
    background-color: #111411;
    border-bottom: 1px solid #1e3d2a;
    padding: 4px 12px;
}
#statusLabel { color: #4caf6e; font-size: 13px; }
#statusRight  { color: #2e7d4f; font-size: 13px; }
#pageTitle {
    color: #5dff8f; font-size: 20px; font-weight: bold;
    letter-spacing: 3px; padding: 8px 0 4px 0;
}
#moduleTile {
    background-color: #111714; border: 1px solid #1e3d2a;
    border-radius: 8px; color: #7dffaa;
    font-size: 17px; font-weight: bold; letter-spacing: 2px; padding: 28px 12px;
}
#moduleTile:pressed { background-color: #1a2e20; border-color: #4caf6e; }
#attackBtn {
    background-color: #0f1a13; border: 1px solid #1e3d2a;
    border-radius: 6px; color: #9effc0;
    font-size: 15px; padding: 16px; text-align: left;
}
#attackBtn:pressed { background-color: #172b1e; border-color: #4caf6e; }
#backBtn {
    background-color: #111411; border: 1px solid #1e3d2a;
    border-radius: 6px; color: #4caf6e;
    font-size: 14px; padding: 10px 20px; max-width: 110px;
}
#backBtn:pressed { background-color: #1a2e20; }
#execBtn {
    background-color: #173a22; border: 1px solid #4caf6e;
    border-radius: 6px; color: #5dff8f;
    font-size: 15px; font-weight: bold; padding: 14px; letter-spacing: 1px;
}
#execBtn:pressed { background-color: #1f5030; }
#saveBtn {
    background-color: #0f1a13; border: 1px solid #2e7d4f;
    border-radius: 6px; color: #4caf6e; font-size: 14px; padding: 10px 16px;
}
#saveBtn:pressed { background-color: #172b1e; }
#stopBtn {
    background-color: #1a0d0d; border: 1px solid #7d2e2e;
    border-radius: 6px; color: #ff6b6b; font-size: 15px; padding: 14px;
}
#stopBtn:pressed { background-color: #2d1515; }
#dangerBtn {
    background-color: #1a0d0d; border: 1px solid #7d2e2e;
    border-radius: 6px; color: #ff6b6b; font-size: 13px; padding: 8px 14px;
}
#dangerBtn:pressed { background-color: #2d1515; }
#settingsBtn {
    background-color: #111411; border: 1px solid #1e3d2a;
    border-radius: 6px; color: #4caf6e; font-size: 13px; padding: 8px 14px;
}
#settingsBtn:pressed { background-color: #1a2e20; }
#logBox {
    background-color: #080f0a; border: 1px solid #1e3d2a;
    border-radius: 6px; color: #7dffaa;
    font-size: 13px; font-family: 'Courier New', monospace; padding: 6px;
}
#inputField {
    background-color: #0f1a13; border: 1px solid #2e7d4f;
    border-radius: 6px; color: #9effc0;
    font-size: 15px; padding: 10px; font-family: 'Courier New', monospace;
}
#inputLabel { color: #4caf6e; font-size: 13px; padding-top: 4px; }
#attackTitle { color: #5dff8f; font-size: 17px; font-weight: bold; letter-spacing: 2px; }
#descLabel   { color: #4caf6e; font-size: 13px; }
QFrame[frameShape="4"] { color: #1e3d2a; }
"""

# Worker thread so UI stays responsive
class Worker(QThread):
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

    # ── Widget helpers ────────────────────────────────────────────────────

    def _title(self, text):
        lbl = QLabel(text)
        lbl.setObjectName("pageTitle")
        return lbl

    def _divider(self):
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        return line

    def _back_btn(self, target=None):
        btn = QPushButton("← BACK")
        btn.setObjectName("backBtn")
        btn.clicked.connect(lambda: self._show(target) if target else self._pop())
        return btn

    def _exec_btn(self, label="▶  EXECUTE"):
        btn = QPushButton(label)
        btn.setObjectName("execBtn")
        return btn

    def _save_btn(self, log_widget, name):
        btn = QPushButton("💾  SAVE")
        btn.setObjectName("saveBtn")
        def save():
            text = log_widget.toPlainText().strip()
            if not text:
                return
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = os.path.join(CAPTURE_DIR, f"{name.lower().replace(' ','_')}_{ts}.txt")
            with open(path, "w") as f:
                f.write(text)
            self._log(f"Saved → {path}")
        btn.clicked.connect(save)
        return btn

    def _log(self, text):
        if hasattr(self, "global_log"):
            ts = datetime.now().strftime("%H:%M:%S")
            self.global_log.append(f"[{ts}] {text}")

    def _run(self, func, kwargs, log_widget, btn_exec):
        log_widget.append("[*] Running…")
        btn_exec.setEnabled(False)
        self._worker = Worker(func, kwargs)
        def done(r):
            log_widget.append(r)
            self._log(r[:80])
            btn_exec.setEnabled(True)
        self._worker.result.connect(done)
        self._worker.start()

    def _log_box(self, height=None):
        box = QTextEdit()
        box.setObjectName("logBox")
        box.setReadOnly(True)
        if height:
            box.setFixedHeight(height)
        return box

    def _input(self, label_text, placeholder="", default=""):
        lbl = QLabel(label_text)
        lbl.setObjectName("inputLabel")
        field = QLineEdit(default)
        field.setObjectName("inputField")
        field.setPlaceholderText(placeholder)
        return lbl, field

    # ── Status bar ────────────────────────────────────────────────────────

    def _build_status_bar(self):
        bar = QWidget()
        bar.setObjectName("statusBar")
        bar.setFixedHeight(38)
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(10, 0, 10, 0)

        self.lbl_status = QLabel("◉ SENTINELPI  |  READY")
        self.lbl_status.setObjectName("statusLabel")
        lay.addWidget(self.lbl_status)
        lay.addStretch()

        self.lbl_time = QLabel()
        self.lbl_time.setObjectName("statusRight")
        self._refresh_status()
        lay.addWidget(self.lbl_time)

        # ── Remove these 4 lines to remove settings button ──
        btn_set = QPushButton("⚙")
        btn_set.setObjectName("settingsBtn")
        btn_set.setFixedSize(40, 28)
        btn_set.clicked.connect(self._settings_screen)
        lay.addWidget(btn_set)
        # ────────────────────────────────────────────────────

        btn_off = QPushButton("⏻")
        btn_off.setObjectName("dangerBtn")
        btn_off.setFixedSize(40, 28)
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
        self.lbl_time.setText(f"🔋{bat}  {now}  ")

    # ── Settings ── Remove this whole method to remove settings ──────────
    def _settings_screen(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(20, 10, 20, 10)
        lay.setSpacing(12)
        lay.addWidget(self._title("SETTINGS"))
        lay.addWidget(self._divider())
        lay.addWidget(QLabel("Capture folder:"))
        path_field = QLineEdit(CAPTURE_DIR)
        path_field.setObjectName("inputField")
        lay.addWidget(path_field)
        lay.addStretch()
        lay.addWidget(self._back_btn(self.page_main))
        self._push(page)
    # ─────────────────────────────────────────────────────────────────────

    # ══ MAIN MENU ════════════════════════════════════════════════════════

    def _build_main_menu(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(16, 10, 16, 10)
        lay.setSpacing(12)
        lay.addWidget(self._title("[ SENTINELPI ]"))

        grid = QGridLayout()
        grid.setSpacing(12)
        modules = [
            ("⚡  BAD USB",   self._badusb_menu),
            ("📡  INFRARED",  self._infrared_menu),
            ("📶  WIRELESS",  self._wireless_menu),
            ("🔖  NFC/RFID",  self._nfc_menu),
        ]
        for i, (label, func) in enumerate(modules):
            btn = QPushButton(label)
            btn.setObjectName("moduleTile")
            btn.setMinimumHeight(100)
            btn.clicked.connect(func)
            grid.addWidget(btn, i // 2, i % 2)

        lay.addLayout(grid)
        lay.addStretch()

        self.global_log = self._log_box(60)
        lay.addWidget(self.global_log)
        return page

    def _attack_list_page(self, title, attacks):
        """Reusable attack list. attacks = [("Name", callback), ...]"""
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(16, 10, 16, 10)
        lay.setSpacing(10)
        lay.addWidget(self._title(title))
        lay.addWidget(self._divider())

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        inner = QWidget()
        inner_lay = QVBoxLayout(inner)
        inner_lay.setSpacing(8)
        for name, cb in attacks:
            btn = QPushButton(f"  {name}")
            btn.setObjectName("attackBtn")
            btn.setMinimumHeight(60)
            btn.clicked.connect(cb)
            inner_lay.addWidget(btn)
        inner_lay.addStretch()
        scroll.setWidget(inner)
        lay.addWidget(scroll)
        lay.addWidget(self._back_btn(self.page_main))
        self._push(page)

    # ══════════════════════════════════════════════════════════════════════
    # BAD USB
    # ══════════════════════════════════════════════════════════════════════

    def _badusb_menu(self):
        self._attack_list_page("⚡  BAD USB", [
            ("Custom Script",  self._badusb_custom),
            ("Reverse Shell",  self._badusb_reverse_shell),
            ("Send Payload",   self._badusb_send_payload),
        ])

    def _badusb_custom(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(16, 10, 16, 10)
        lay.setSpacing(8)
        lay.addWidget(self._title("CUSTOM SCRIPT"))
        lay.addWidget(QLabel("Paste your Ducky Script below, then hit Execute.", objectName="descLabel"))
        lay.addWidget(self._divider())

        script_box = QTextEdit()
        script_box.setObjectName("inputField")
        script_box.setPlaceholderText("STRING Hello World\nENTER")
        lay.addWidget(script_box)

        log = self._log_box(80)
        lay.addWidget(log)

        btn_exec = self._exec_btn()
        # When run() accepts the script, pass it: {"script": script_box.toPlainText()}
        btn_exec.clicked.connect(lambda: self._run(custom_script.run, {}, log, btn_exec))

        row = QHBoxLayout()
        row.addWidget(btn_exec)
        row.addWidget(self._back_btn())
        lay.addLayout(row)
        self._push(page)

    def _badusb_reverse_shell(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(16, 10, 16, 10)
        lay.setSpacing(8)
        lay.addWidget(self._title("REVERSE SHELL"))

        lbl_ip,   f_ip   = self._input("Listener IP",   "192.168.1.10")
        lbl_port, f_port = self._input("Listener Port", "4444")
        lay.addWidget(lbl_ip);   lay.addWidget(f_ip)
        lay.addWidget(lbl_port); lay.addWidget(f_port)
        lay.addWidget(self._divider())

        log = self._log_box(100)
        lay.addWidget(log)

        btn_exec = self._exec_btn()
        # When run() accepts args: {"ip": f_ip.text(), "port": f_port.text()}
        btn_exec.clicked.connect(lambda: self._run(reverse_shell.run, {}, log, btn_exec))

        row = QHBoxLayout()
        row.addWidget(btn_exec)
        row.addWidget(self._back_btn())
        lay.addLayout(row)
        self._push(page)

    def _badusb_send_payload(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(16, 10, 16, 10)
        lay.setSpacing(8)
        lay.addWidget(self._title("SEND PAYLOAD"))
        lay.addWidget(QLabel("Select a pre-built payload to inject.", objectName="descLabel"))
        lay.addWidget(self._divider())

        log = self._log_box(120)
        payloads = ["Credential Harvest (demo)", "Disable Defender (demo)", "Exfil via DNS (demo)"]
        for p in payloads:
            btn = QPushButton(f"  {p}")
            btn.setObjectName("attackBtn")
            btn.setMinimumHeight(52)
            # Store btn in closure properly
            def make_handler(name, b):
                def handler():
                    log.append(f"[*] Sending: {name}…")
                    self._run(send_payload.run, {}, log, b)
                return handler
            btn.clicked.connect(make_handler(p, btn))
            lay.addWidget(btn)

        lay.addWidget(log)
        lay.addWidget(self._back_btn())
        self._push(page)

    # ══════════════════════════════════════════════════════════════════════
    # INFRARED
    # ══════════════════════════════════════════════════════════════════════

    def _infrared_menu(self):
        self._attack_list_page("📡  INFRARED", [
            ("IR Capture",     self._ir_capture),
            ("IR Transmit",    self._ir_transmit),
            ("IR Relay",       self._ir_relay),
            ("IR Bruteforce",  self._ir_bruteforce),
        ])

    def _ir_capture(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(16, 10, 16, 10)
        lay.setSpacing(8)
        lay.addWidget(self._title("IR CAPTURE"))
        lay.addWidget(QLabel("Point remote at receiver and press Capture.", objectName="descLabel"))
        lay.addWidget(self._divider())

        log = self._log_box()
        lay.addWidget(log)

        btn_exec = self._exec_btn("⏺  CAPTURE")
        btn_exec.clicked.connect(lambda: self._run(ir_capture.run, {}, log, btn_exec))

        row = QHBoxLayout()
        row.addWidget(btn_exec)
        row.addWidget(self._save_btn(log, "ir_capture"))
        row.addWidget(self._back_btn())
        lay.addLayout(row)
        self._push(page)

    def _ir_transmit(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(16, 10, 16, 10)
        lay.setSpacing(8)
        lay.addWidget(self._title("IR TRANSMIT"))

        lbl_freq, f_freq = self._input("Frequency (kHz)", "38", "38")
        lbl_data, f_data = self._input("Signal Data (hex or raw)", "AA BB CC …")
        lay.addWidget(lbl_freq); lay.addWidget(f_freq)
        lay.addWidget(lbl_data); lay.addWidget(f_data)
        lay.addWidget(self._divider())

        log = self._log_box(100)
        lay.addWidget(log)

        btn_exec = self._exec_btn("📤  TRANSMIT")
        btn_exec.clicked.connect(lambda: self._run(ir_transmission.run, {}, log, btn_exec))

        row = QHBoxLayout()
        row.addWidget(btn_exec)
        row.addWidget(self._back_btn())
        lay.addLayout(row)
        self._push(page)

    def _ir_relay(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(16, 10, 16, 10)
        lay.setSpacing(8)
        lay.addWidget(self._title("IR RELAY"))
        lay.addWidget(QLabel("Captures and immediately re-transmits IR signals.", objectName="descLabel"))
        lay.addWidget(self._divider())

        log = self._log_box()
        lay.addWidget(log)

        btn_start = self._exec_btn("▶  START RELAY")
        btn_stop  = QPushButton("■  STOP")
        btn_stop.setObjectName("stopBtn")
        btn_stop.setEnabled(False)

        def start():
            self._run(ir_relay.run, {}, log, btn_start)
            btn_stop.setEnabled(True)
        def stop():
            if self._worker:
                self._worker.terminate()
            log.append("[*] Relay stopped.")
            btn_stop.setEnabled(False)
            btn_start.setEnabled(True)

        btn_start.clicked.connect(start)
        btn_stop.clicked.connect(stop)

        row = QHBoxLayout()
        row.addWidget(btn_start)
        row.addWidget(btn_stop)
        row.addWidget(self._back_btn())
        lay.addLayout(row)
        self._push(page)

    def _ir_bruteforce(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(16, 10, 16, 10)
        lay.setSpacing(8)
        lay.addWidget(self._title("IR BRUTEFORCE"))

        lbl_start, f_start = self._input("Start Code (hex)", "0x00", "0x00")
        lbl_end,   f_end   = self._input("End Code (hex)",   "0xFF", "0xFF")
        lbl_delay, f_delay = self._input("Delay between codes (ms)", "200", "200")
        lay.addWidget(lbl_start); lay.addWidget(f_start)
        lay.addWidget(lbl_end);   lay.addWidget(f_end)
        lay.addWidget(lbl_delay); lay.addWidget(f_delay)
        lay.addWidget(self._divider())

        log = self._log_box(80)
        lay.addWidget(log)

        btn_exec = self._exec_btn("▶  START")
        btn_exec.clicked.connect(lambda: self._run(ir_bruteforce.run, {}, log, btn_exec))

        row = QHBoxLayout()
        row.addWidget(btn_exec)
        row.addWidget(self._save_btn(log, "ir_bruteforce"))
        row.addWidget(self._back_btn())
        lay.addLayout(row)
        self._push(page)

    # ══════════════════════════════════════════════════════════════════════
    # WIRELESS
    # ══════════════════════════════════════════════════════════════════════

    def _wireless_menu(self):
        self._attack_list_page("📶  WIRELESS", [
            ("Channel Scan",  self._wireless_channel_scan),
            ("Packet Sniff",  self._wireless_packet_sniff),
            ("Replay Attack", self._wireless_replay),
            ("Jammer",        self._wireless_jammer),
        ])

    def _wireless_channel_scan(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(16, 10, 16, 10)
        lay.setSpacing(8)
        lay.addWidget(self._title("CHANNEL SCAN"))
        lay.addWidget(QLabel("Scan all 2.4 GHz channels for activity.", objectName="descLabel"))
        lay.addWidget(self._divider())

        log = self._log_box()
        lay.addWidget(log)

        btn_exec = self._exec_btn("📡  SCAN")
        btn_exec.clicked.connect(lambda: self._run(channel_scan.run, {}, log, btn_exec))

        row = QHBoxLayout()
        row.addWidget(btn_exec)
        row.addWidget(self._save_btn(log, "channel_scan"))
        row.addWidget(self._back_btn())
        lay.addLayout(row)
        self._push(page)

    def _wireless_packet_sniff(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(16, 10, 16, 10)
        lay.setSpacing(8)
        lay.addWidget(self._title("PACKET SNIFF"))

        lbl_ch, f_ch = self._input("Channel", "1–125", "1")
        lbl_n,  f_n  = self._input("Packet count (0 = unlimited)", "0", "0")
        lay.addWidget(lbl_ch); lay.addWidget(f_ch)
        lay.addWidget(lbl_n);  lay.addWidget(f_n)
        lay.addWidget(self._divider())

        log = self._log_box()
        lay.addWidget(log)

        btn_exec = self._exec_btn("▶  START SNIFF")
        btn_exec.clicked.connect(lambda: self._run(packet_sniff.run, {}, log, btn_exec))

        row = QHBoxLayout()
        row.addWidget(btn_exec)
        row.addWidget(self._save_btn(log, "packet_sniff"))
        row.addWidget(self._back_btn())
        lay.addLayout(row)
        self._push(page)

    def _wireless_replay(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(16, 10, 16, 10)
        lay.setSpacing(8)
        lay.addWidget(self._title("REPLAY ATTACK"))
        lay.addWidget(QLabel("Load a saved capture file and replay it.", objectName="descLabel"))
        lay.addWidget(self._divider())

        lbl_file, f_file = self._input("Capture file (from captures folder)", "filename.txt")
        lbl_rep,  f_rep  = self._input("Repeat count", "1", "1")
        lay.addWidget(lbl_file); lay.addWidget(f_file)
        lay.addWidget(lbl_rep);  lay.addWidget(f_rep)
        lay.addWidget(self._divider())

        log = self._log_box(100)
        lay.addWidget(log)

        btn_exec = self._exec_btn("📤  REPLAY")
        btn_exec.clicked.connect(lambda: self._run(replay.run, {}, log, btn_exec))

        row = QHBoxLayout()
        row.addWidget(btn_exec)
        row.addWidget(self._back_btn())
        lay.addLayout(row)
        self._push(page)

    def _wireless_jammer(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(16, 10, 16, 10)
        lay.setSpacing(8)
        lay.addWidget(self._title("JAMMER"))
        lay.addWidget(QLabel("⚠  Authorised lab use only.", objectName="descLabel"))
        lay.addWidget(self._divider())

        lbl_ch, f_ch = self._input("Target Channel", "1–125", "1")
        lay.addWidget(lbl_ch); lay.addWidget(f_ch)
        lay.addWidget(self._divider())

        log = self._log_box(100)
        lay.addWidget(log)

        btn_start = self._exec_btn("▶  START JAMMING")
        btn_stop  = QPushButton("■  STOP")
        btn_stop.setObjectName("stopBtn")
        btn_stop.setEnabled(False)

        def start():
            self._run(jammer.run, {}, log, btn_start)
            btn_stop.setEnabled(True)
        def stop():
            if self._worker:
                self._worker.terminate()
            log.append("[*] Jammer stopped.")
            btn_stop.setEnabled(False)
            btn_start.setEnabled(True)

        btn_start.clicked.connect(start)
        btn_stop.clicked.connect(stop)

        row = QHBoxLayout()
        row.addWidget(btn_start)
        row.addWidget(btn_stop)
        row.addWidget(self._back_btn())
        lay.addLayout(row)
        self._push(page)

    # ══════════════════════════════════════════════════════════════════════
    # NFC / RFID
    # ══════════════════════════════════════════════════════════════════════

    def _nfc_menu(self):
        self._attack_list_page("🔖  NFC/RFID", [
            ("Read Tag",   self._nfc_read),
            ("Clone Tag",  self._nfc_clone),
            ("Emulate",    self._nfc_emulate),
            ("Write Tag",  self._nfc_write),
        ])

    def _nfc_read(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(16, 10, 16, 10)
        lay.setSpacing(8)
        lay.addWidget(self._title("READ TAG"))
        lay.addWidget(QLabel("Hold tag near PN532 reader and press Read.", objectName="descLabel"))
        lay.addWidget(self._divider())

        log = self._log_box()
        lay.addWidget(log)

        btn_exec = self._exec_btn("📖  READ")
        btn_exec.clicked.connect(lambda: self._run(read.run, {}, log, btn_exec))

        row = QHBoxLayout()
        row.addWidget(btn_exec)
        row.addWidget(self._save_btn(log, "nfc_read"))
        row.addWidget(self._back_btn())
        lay.addLayout(row)
        self._push(page)

    def _nfc_clone(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(16, 10, 16, 10)
        lay.setSpacing(8)
        lay.addWidget(self._title("CLONE TAG"))
        lay.addWidget(QLabel("Step 1 → Read source.  Step 2 → Place blank.  Step 3 → Write.", objectName="descLabel"))
        lay.addWidget(self._divider())

        log = self._log_box()
        lay.addWidget(log)

        btn_read  = self._exec_btn("📖  READ SOURCE")
        btn_write = QPushButton("✏️  WRITE CLONE")
        btn_write.setObjectName("execBtn")
        btn_write.setEnabled(False)

        def do_read():
            self._run(read.run, {}, log, btn_read)
            btn_write.setEnabled(True)

        btn_read.clicked.connect(do_read)
        btn_write.clicked.connect(lambda: self._run(clone.run, {}, log, btn_write))

        row = QHBoxLayout()
        row.addWidget(btn_read)
        row.addWidget(btn_write)
        row.addWidget(self._save_btn(log, "nfc_clone"))
        row.addWidget(self._back_btn())
        lay.addLayout(row)
        self._push(page)

    def _nfc_emulate(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(16, 10, 16, 10)
        lay.setSpacing(8)
        lay.addWidget(self._title("EMULATE TAG"))

        lbl_uid,  f_uid  = self._input("UID to emulate (hex)", "04:AB:CD:EF")
        lbl_type, f_type = self._input("Tag type", "MIFARE Classic 1K")
        lay.addWidget(lbl_uid);  lay.addWidget(f_uid)
        lay.addWidget(lbl_type); lay.addWidget(f_type)
        lay.addWidget(self._divider())

        log = self._log_box(100)
        lay.addWidget(log)

        btn_start = self._exec_btn("▶  START EMULATION")
        btn_stop  = QPushButton("■  STOP")
        btn_stop.setObjectName("stopBtn")
        btn_stop.setEnabled(False)

        def start():
            self._run(emulate.run, {}, log, btn_start)
            btn_stop.setEnabled(True)
        def stop():
            if self._worker:
                self._worker.terminate()
            log.append("[*] Emulation stopped.")
            btn_stop.setEnabled(False)
            btn_start.setEnabled(True)

        btn_start.clicked.connect(start)
        btn_stop.clicked.connect(stop)

        row = QHBoxLayout()
        row.addWidget(btn_start)
        row.addWidget(btn_stop)
        row.addWidget(self._back_btn())
        lay.addLayout(row)
        self._push(page)

    def _nfc_write(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(16, 10, 16, 10)
        lay.setSpacing(8)
        lay.addWidget(self._title("WRITE TAG"))
        lay.addWidget(QLabel("⚠  This will overwrite the tag's data.", objectName="descLabel"))
        lay.addWidget(self._divider())

        lbl_data, f_data = self._input("Data to write (text or hex)", "Hello SentinelPi")
        lbl_fmt,  f_fmt  = self._input("Format", "NDEF / RAW", "NDEF")
        lay.addWidget(lbl_data); lay.addWidget(f_data)
        lay.addWidget(lbl_fmt);  lay.addWidget(f_fmt)
        lay.addWidget(self._divider())

        log = self._log_box(100)
        lay.addWidget(log)

        btn_exec = self._exec_btn("✏️  WRITE")
        btn_exec.clicked.connect(lambda: self._run(write.run, {}, log, btn_exec))

        row = QHBoxLayout()
        row.addWidget(btn_exec)
        row.addWidget(self._back_btn())
        lay.addLayout(row)
        self._push(page)
