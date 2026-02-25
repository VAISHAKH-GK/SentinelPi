# ui/pages/nfc.py
# All NFC / RFID attack screens live here.
# To add a new attack:
#   1. Write a new method like _my_attack(self)
#   2. Add it to the list in build_menu()

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton
from ui.helpers import title, divider, desc, log_box, input_field, exec_btn, stop_btn, save_btn, back_btn, btn_row

from modules.nfc import clone, emulate, read, write


class NFCPage:
    def __init__(self, window):
        self.w = window

    # ── Menu ─────────────────────────────────────────────────────────────

    def build_menu(self):
        attacks = [
            ("Read Tag",  self._read),
            ("Clone Tag", self._clone),
            ("Emulate",   self._emulate),
            ("Write Tag", self._write),
        ]
        self.w._attack_list("NFC / RFID", attacks)

    # ── Attack screens ────────────────────────────────────────────────────

    def _read(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(16, 10, 16, 10)
        lay.setSpacing(8)

        lay.addWidget(title("READ TAG"))
        lay.addWidget(desc("Hold tag near PN532 reader and press Read."))
        lay.addWidget(divider())

        log = log_box()
        lay.addWidget(log)

        run = exec_btn("READ")
        run.clicked.connect(lambda: self.w._run(read.run, {}, log, run))

        lay.addLayout(btn_row(run, save_btn(log, "nfc_read"), back_btn(self.w._pop)))
        self.w._push(page)

    def _clone(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(16, 10, 16, 10)
        lay.setSpacing(8)

        lay.addWidget(title("CLONE TAG"))
        lay.addWidget(desc("Step 1: Read source tag.  Step 2: Place blank tag.  Step 3: Write."))
        lay.addWidget(divider())

        log = log_box()
        lay.addWidget(log)

        btn_read  = exec_btn("READ SOURCE")
        btn_write = QPushButton("WRITE CLONE")
        btn_write.setObjectName("execBtn")
        btn_write.setMinimumHeight(52)
        btn_write.setEnabled(False)   # only enabled after a read

        def do_read():
            self.w._run(read.run, {}, log, btn_read)
            btn_write.setEnabled(True)

        btn_read.clicked.connect(do_read)
        btn_write.clicked.connect(lambda: self.w._run(clone.run, {}, log, btn_write))

        lay.addLayout(btn_row(btn_read, btn_write, save_btn(log, "nfc_clone"), back_btn(self.w._pop)))
        self.w._push(page)

    def _emulate(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(16, 10, 16, 10)
        lay.setSpacing(8)

        lay.addWidget(title("EMULATE TAG"))
        lay.addWidget(divider())

        lbl_uid,  f_uid  = input_field("UID to emulate (hex)", "04:AB:CD:EF")
        lbl_type, f_type = input_field("Tag type", "MIFARE Classic 1K")
        lay.addWidget(lbl_uid);  lay.addWidget(f_uid)
        lay.addWidget(lbl_type); lay.addWidget(f_type)
        lay.addWidget(divider())

        log = log_box(100)
        lay.addWidget(log)

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

        lay.addLayout(btn_row(start, stop, back_btn(self.w._pop)))
        self.w._push(page)

    def _write(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(16, 10, 16, 10)
        lay.setSpacing(8)

        lay.addWidget(title("WRITE TAG"))
        lay.addWidget(desc("WARNING: This will overwrite the tag's existing data."))
        lay.addWidget(divider())

        lbl_data, f_data = input_field("Data to write (text or hex)", "Hello SentinelPi")
        lbl_fmt,  f_fmt  = input_field("Format (NDEF / RAW)", "NDEF", "NDEF")
        lay.addWidget(lbl_data); lay.addWidget(f_data)
        lay.addWidget(lbl_fmt);  lay.addWidget(f_fmt)
        lay.addWidget(divider())

        log = log_box(100)
        lay.addWidget(log)

        run = exec_btn("WRITE")
        # When run() accepts args: {"data": f_data.text(), "fmt": f_fmt.text()}
        run.clicked.connect(lambda: self.w._run(write.run, {}, log, run))

        lay.addLayout(btn_row(run, back_btn(self.w._pop)))
        self.w._push(page)
