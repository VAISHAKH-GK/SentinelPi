# ui/pages/badusb.py
# Bad USB attack screens.
# Add a new attack: write a method + add it to build_menu()

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton, QScrollArea, QFrame
from ui.keyboard import KeyboardTextEdit
from ui.helpers import (title, divider, desc, log_box, input_field,
                        exec_btn, save_btn, back_btn, bottom_bar)
from modules.badusb import custom_script, reverse_shell, send_payload

PAGE_W = 800
PAGE_H = 444
M      = 10    # margin


class BadUSBPage:
    def __init__(self, window):
        self.w = window

    def build_menu(self):
        self.w._attack_list("BAD USB", [
            ("Custom Script",  self._custom_script),
            ("Reverse Shell",  self._reverse_shell),
            ("Send Payload",   self._send_payload),
        ])

    # ── Custom Script ─────────────────────────────────────────────────

    def _custom_script(self):
        page = QWidget(); page.setFixedSize(PAGE_W, PAGE_H)
        lay  = QVBoxLayout(page)
        lay.setContentsMargins(M, 8, M, 0)
        lay.setSpacing(6)

        lay.addWidget(title("CUSTOM SCRIPT"))
        lay.addWidget(desc("Paste Ducky Script below, then Execute."))
        lay.addWidget(divider())

        script_box = QTextEdit()
        script_box.setObjectName("inputField")
        script_box.setPlaceholderText("STRING Hello World\nENTER")
        lay.addWidget(script_box)   # takes remaining space

        log = log_box(80)
        lay.addWidget(log)

        run = exec_btn("EXECUTE")
        run.clicked.connect(lambda: self.w._run(custom_script.run, {}, log, run))

        lay.addWidget(bottom_bar(run, back_btn(self.w._pop)))
        self.w._push(page)

    # ── Reverse Shell ─────────────────────────────────────────────────

    def _reverse_shell(self):
        page = QWidget(); page.setFixedSize(PAGE_W, PAGE_H)
        lay  = QVBoxLayout(page)
        lay.setContentsMargins(M, 8, M, 0)
        lay.setSpacing(6)

        lay.addWidget(title("REVERSE SHELL"))
        lay.addWidget(divider())

        lbl_ip,   f_ip   = input_field("Listener IP",   "192.168.1.10")
        lbl_port, f_port = input_field("Listener Port", "4444")
        lay.addWidget(lbl_ip);   lay.addWidget(f_ip)
        lay.addWidget(lbl_port); lay.addWidget(f_port)
        lay.addWidget(divider())

        log = log_box(200)
        lay.addWidget(log)
        lay.addStretch()

        run = exec_btn("EXECUTE")
        run.clicked.connect(lambda: self.w._run(
            reverse_shell.run,
            {},  # swap {} for {"ip": f_ip.text(), "port": f_port.text()} when run() accepts args
            log, run
        ))

        lay.addWidget(bottom_bar(run, back_btn(self.w._pop)))
        self.w._push(page)

    # ── Send Payload ──────────────────────────────────────────────────

    def _send_payload(self):
        page = QWidget(); page.setFixedSize(PAGE_W, PAGE_H)
        lay  = QVBoxLayout(page)
        lay.setContentsMargins(M, 8, M, 0)
        lay.setSpacing(6)

        lay.addWidget(title("SEND PAYLOAD"))
        lay.addWidget(desc("Select a pre-built payload to inject."))
        lay.addWidget(divider())

        log = log_box(110)

        # Add payload entries here
        payloads = [
            "Credential Harvest (demo)",
            "Disable Defender (demo)",
            "Exfil via DNS (demo)",
        ]
        for p in payloads:
            btn = QPushButton(p)
            btn.setObjectName("attackBtn")
            btn.setFixedHeight(52)
            def handler(checked, name=p, b=btn):
                log.append(f"[*] Sending: {name}")
                self.w._run(send_payload.run, {}, log, b)
            btn.clicked.connect(handler)
            lay.addWidget(btn)

        lay.addWidget(log)
        lay.addStretch()
        lay.addWidget(bottom_bar(back_btn(self.w._pop)))
        self.w._push(page)
