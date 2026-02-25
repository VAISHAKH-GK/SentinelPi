# ui/pages/badusb.py
# All Bad USB attack screens live here.
# To add a new attack:
#   1. Write a new method like _my_attack(self)
#   2. Add it to the list in build_menu()

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton, QScrollArea, QFrame
from ui.helpers import title, divider, desc, log_box, input_field, exec_btn, save_btn, back_btn, btn_row

from modules.badusb import custom_script, reverse_shell, send_payload


class BadUSBPage:
    """
    Usage in MainWindow:
        from ui.pages.badusb import BadUSBPage
        BadUSBPage(self).build_menu()
    """

    def __init__(self, window):
        self.w = window  # reference to MainWindow for navigation and _run()

    # ── Menu ─────────────────────────────────────────────────────────────

    def build_menu(self):
        attacks = [
            ("Custom Script",  self._custom_script),
            ("Reverse Shell",  self._reverse_shell),
            ("Send Payload",   self._send_payload),
        ]
        self.w._attack_list("BAD USB", attacks)

    # ── Attack screens ────────────────────────────────────────────────────

    def _custom_script(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(16, 10, 16, 10)
        lay.setSpacing(8)

        lay.addWidget(title("CUSTOM SCRIPT"))
        lay.addWidget(desc("Paste your Ducky Script below, then hit Execute."))
        lay.addWidget(divider())

        # Multi-line script input
        script_box = QTextEdit()
        script_box.setObjectName("inputField")
        script_box.setPlaceholderText("STRING Hello World\nENTER")
        lay.addWidget(script_box)

        log = log_box(80)
        lay.addWidget(log)

        run = exec_btn("EXECUTE")
        # When run() accepts the script text, change {} to {"script": script_box.toPlainText()}
        run.clicked.connect(lambda: self.w._run(custom_script.run, {}, log, run))

        lay.addLayout(btn_row(run, back_btn(self.w._pop)))
        self.w._push(page)

    def _reverse_shell(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(16, 10, 16, 10)
        lay.setSpacing(8)

        lay.addWidget(title("REVERSE SHELL"))
        lay.addWidget(divider())

        lbl_ip,   f_ip   = input_field("Listener IP",   "192.168.1.10")
        lbl_port, f_port = input_field("Listener Port", "4444")
        lay.addWidget(lbl_ip);   lay.addWidget(f_ip)
        lay.addWidget(lbl_port); lay.addWidget(f_port)
        lay.addWidget(divider())

        log = log_box(120)
        lay.addWidget(log)

        run = exec_btn("EXECUTE")
        # When run() accepts args, change {} to {"ip": f_ip.text(), "port": f_port.text()}
        run.clicked.connect(lambda: self.w._run(reverse_shell.run, {}, log, run))

        lay.addLayout(btn_row(run, back_btn(self.w._pop)))
        self.w._push(page)

    def _send_payload(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(16, 10, 16, 10)
        lay.setSpacing(8)

        lay.addWidget(title("SEND PAYLOAD"))
        lay.addWidget(desc("Select a pre-built payload to inject."))
        lay.addWidget(divider())

        log = log_box(130)

        # Add or remove payload entries here
        payloads = [
            "Credential Harvest (demo)",
            "Disable Defender (demo)",
            "Exfil via DNS (demo)",
        ]
        for p in payloads:
            btn = QPushButton(p)
            btn.setObjectName("attackBtn")
            btn.setMinimumHeight(52)
            def handler(checked, name=p, b=btn):
                log.append(f"[*] Sending: {name}")
                self.w._run(send_payload.run, {}, log, b)
            btn.clicked.connect(handler)
            lay.addWidget(btn)

        lay.addWidget(log)
        lay.addLayout(btn_row(back_btn(self.w._pop)))
        self.w._push(page)
