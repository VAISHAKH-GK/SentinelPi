# ui/pages/nfc.py
# NFC / RFID attack screens.
# Add a new attack: write a method + add it to build_menu()

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton
from ui.helpers import (title, divider, desc, warn, log_box, input_field,
                        exec_btn, stop_btn, save_btn, back_btn, bottom_bar)
from modules.nfc import clone, emulate, read, write

PAGE_W = 800
PAGE_H = 444
M      = 10


class NFCPage:
    def __init__(self, window):
        self.w = window

    def build_menu(self):
        self.w._attack_list("NFC / RFID", [
            ("Read Tag",  self._read),
            ("Clone Tag", self._clone),
            ("Emulate",   self._emulate),
            ("Write Tag", self._write),
        ])

    # ── Read Tag ──────────────────────────────────────────────────────

    def _read(self):
        page = QWidget(); page.setFixedSize(PAGE_W, PAGE_H)
        lay  = QVBoxLayout(page)
        lay.setContentsMargins(M, 8, M, 0)
        lay.setSpacing(6)

        lay.addWidget(title("READ TAG"))
        lay.addWidget(desc("Hold tag near PN532 reader and press Read."))
        lay.addWidget(divider())

        log = log_box(310)
        lay.addWidget(log)
        lay.addStretch()

        run = exec_btn("READ")
        run.clicked.connect(lambda: self.w._run(read.run, {}, log, run))

        lay.addWidget(bottom_bar(run, save_btn(log, "nfc_read"), back_btn(self.w._pop)))
        self.w._push(page)

    # ── Clone Tag ─────────────────────────────────────────────────────

    def _clone(self):
        page = QWidget(); page.setFixedSize(PAGE_W, PAGE_H)
        lay  = QVBoxLayout(page)
        lay.setContentsMargins(M, 8, M, 0)
        lay.setSpacing(6)

        lay.addWidget(title("CLONE TAG"))
        lay.addWidget(desc("Step 1: Read source.  Step 2: Place blank.  Step 3: Write."))
        lay.addWidget(divider())

        log = log_box(290)
        lay.addWidget(log)
        lay.addStretch()

        btn_read  = exec_btn("READ SOURCE")
        btn_write = QPushButton("WRITE CLONE")
        btn_write.setObjectName("execBtn")
        btn_write.setFixedHeight(40)
        btn_write.setEnabled(False)

        def do_read():
            self.w._run(read.run, {}, log, btn_read)
            btn_write.setEnabled(True)

        btn_read.clicked.connect(do_read)
        btn_write.clicked.connect(lambda: self.w._run(clone.run, {}, log, btn_write))

        lay.addWidget(bottom_bar(btn_read, btn_write, save_btn(log, "nfc_clone"), back_btn(self.w._pop)))
        self.w._push(page)

    # ── Emulate ───────────────────────────────────────────────────────

    def _emulate(self):
        page = QWidget(); page.setFixedSize(PAGE_W, PAGE_H)
        lay  = QVBoxLayout(page)
        lay.setContentsMargins(M, 8, M, 0)
        lay.setSpacing(6)

        lay.addWidget(title("EMULATE TAG"))
        lay.addWidget(divider())

        lbl_uid,  f_uid  = input_field("UID to emulate (hex)", "04:AB:CD:EF")
        lbl_type, f_type = input_field("Tag type", "MIFARE Classic 1K")
        lay.addWidget(lbl_uid);  lay.addWidget(f_uid)
        lay.addWidget(lbl_type); lay.addWidget(f_type)
        lay.addWidget(divider())

        log = log_box(220)
        lay.addWidget(log)
        lay.addStretch()

        start = exec_btn("START EMULATION")
        stop  = stop_btn("STOP")

        def do_start():
            self.w._run(emulate.run, {}, log, start)
            stop.setEnabled(True)

        def do_stop():
            if self.w._worker:
                self.w._worker.terminate()
            log.append("[*] Emulation stopped.")
            stop.setEnabled(False)
            start.setEnabled(True)

        start.clicked.connect(do_start)
        stop.clicked.connect(do_stop)

        lay.addWidget(bottom_bar(start, stop, back_btn(self.w._pop)))
        self.w._push(page)

    # ── Write Tag ─────────────────────────────────────────────────────

    def _write(self):
        page = QWidget(); page.setFixedSize(PAGE_W, PAGE_H)
        lay  = QVBoxLayout(page)
        lay.setContentsMargins(M, 8, M, 0)
        lay.setSpacing(6)

        lay.addWidget(title("WRITE TAG"))
        lay.addWidget(warn("This will overwrite the tag's existing data."))
        lay.addWidget(divider())

        lbl_d, f_data = input_field("Data to write (text or hex)", "Hello SentinelPi")
        lbl_f, f_fmt  = input_field("Format (NDEF / RAW)", "NDEF", "NDEF")
        lay.addWidget(lbl_d); lay.addWidget(f_data)
        lay.addWidget(lbl_f); lay.addWidget(f_fmt)
        lay.addWidget(divider())

        log = log_box(220)
        lay.addWidget(log)
        lay.addStretch()

        run = exec_btn("WRITE")
        run.clicked.connect(lambda: self.w._run(write.run, {}, log, run))

        lay.addWidget(bottom_bar(run, back_btn(self.w._pop)))
        self.w._push(page)
