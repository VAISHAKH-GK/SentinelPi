# ui/pages/nfc.py
# NFC / RFID attack screens for PN532 over I2C.

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QButtonGroup, QHBoxLayout
from ui.helpers import (title, divider, desc, warn, log_box, input_field,
                        exec_btn, stop_btn, save_btn, back_btn, bottom_bar)

from modules.nfc import read, clone, write, emulate

PAGE_W = 800
PAGE_H = 444
M      = 10


class NFCPage:
    def __init__(self, window):
        self.w = window

    def build_menu(self):
        self.w._attack_list("NFC / RFID", [
            ("Read Tag",   self._read),
            ("Clone Tag",  self._clone),
            ("Write Tag",  self._write),
            ("Emulate Tag", self._emulate),
        ])

    # ── Read Tag ──────────────────────────────────────────────────────

    def _read(self):
        page = QWidget(); page.setFixedSize(PAGE_W, PAGE_H)
        lay  = QVBoxLayout(page)
        lay.setContentsMargins(M, 8, M, 0); lay.setSpacing(6)

        lay.addWidget(title("READ TAG"))
        lay.addWidget(desc("Reads UID and tag type. Hold tag near PN532."))
        lay.addWidget(divider())

        lbl_t, f_timeout = input_field("Timeout (s)", "15", "15")
        lay.addWidget(lbl_t); lay.addWidget(f_timeout)
        lay.addWidget(divider())

        log = log_box(290)
        lay.addWidget(log)
        lay.addStretch()

        run = exec_btn("READ")
        run.clicked.connect(lambda: self.w._run(
            read.run, {"timeout": int(f_timeout.text() or 15)}, log, run
        ))

        lay.addWidget(bottom_bar(run, save_btn(log, "nfc_read"), back_btn(self.w._pop)))
        self.w._push(page)

    # ── Clone Tag ─────────────────────────────────────────────────────

    def _clone(self):
        page = QWidget(); page.setFixedSize(PAGE_W, PAGE_H)
        lay  = QVBoxLayout(page)
        lay.setContentsMargins(M, 8, M, 0); lay.setSpacing(6)

        lay.addWidget(title("CLONE TAG"))
        lay.addWidget(desc("Step 1: Read source.  Step 2: Swap to blank card.  Step 3: Write."))
        lay.addWidget(divider())

        # Info box
        info = desc("Requires blank writable 'magic' card (Gen1a/Gen2).")
        lay.addWidget(info)
        lay.addWidget(divider())

        log = log_box(240)
        lay.addWidget(log)
        lay.addStretch()

        btn_read  = exec_btn("READ SOURCE")
        btn_write = QPushButton("WRITE CLONE")
        btn_write.setObjectName("execBtn")
        btn_write.setFixedHeight(40)
        btn_write.setEnabled(False)   # enabled after read

        def do_read():
            self.w._run(clone.read_source, {}, log, btn_read)
            btn_write.setEnabled(True)

        def do_write():
            self.w._run(clone.write_clone, {}, log, btn_write)

        btn_read.clicked.connect(do_read)
        btn_write.clicked.connect(do_write)

        lay.addWidget(bottom_bar(btn_read, btn_write, save_btn(log, "nfc_clone"), back_btn(self.w._pop)))
        self.w._push(page)

    # ── Write Tag ─────────────────────────────────────────────────────

    def _write(self):
        page = QWidget(); page.setFixedSize(PAGE_W, PAGE_H)
        lay  = QVBoxLayout(page)
        lay.setContentsMargins(M, 8, M, 0); lay.setSpacing(6)

        lay.addWidget(title("WRITE TAG"))
        lay.addWidget(warn("This overwrites the tag's existing data."))
        lay.addWidget(divider())

        # Format selector
        lay.addWidget(desc("Format:"))
        fmt_row = QHBoxLayout(); fmt_row.setSpacing(6)
        btn_text = QPushButton("TEXT")
        btn_uri  = QPushButton("URI / URL")
        btn_raw  = QPushButton("RAW HEX")
        fmt_btns = [btn_text, btn_uri, btn_raw]
        for b in fmt_btns:
            b.setObjectName("attackBtn")
            b.setFixedHeight(40)
            b.setCheckable(True)
            fmt_row.addWidget(b)
        fmt_grp = QButtonGroup(); fmt_grp.setExclusive(True)
        for i, b in enumerate(fmt_btns): fmt_grp.addButton(b, i)
        btn_text.setChecked(True)
        lay.addLayout(fmt_row)

        lbl_d, f_data    = input_field("Data to write", "Hello SentinelPi", "Hello SentinelPi")
        lbl_t, f_timeout = input_field("Timeout (s)", "15", "15")
        lay.addWidget(lbl_d); lay.addWidget(f_data)
        lay.addWidget(lbl_t); lay.addWidget(f_timeout)
        lay.addWidget(divider())

        log = log_box(120)
        lay.addWidget(log)
        lay.addStretch()

        def get_fmt():
            if btn_uri.isChecked(): return "URI"
            if btn_raw.isChecked(): return "RAW"
            return "TEXT"

        run = exec_btn("WRITE")
        run.clicked.connect(lambda: self.w._run(
            write.run, {
                "data":    f_data.text(),
                "fmt":     get_fmt(),
                "timeout": int(f_timeout.text() or 15),
            }, log, run
        ))

        lay.addWidget(bottom_bar(run, back_btn(self.w._pop)))
        self.w._push(page)

    # ── Emulate Tag ───────────────────────────────────────────────────

    def _emulate(self):
        page = QWidget(); page.setFixedSize(PAGE_W, PAGE_H)
        lay  = QVBoxLayout(page)
        lay.setContentsMargins(M, 8, M, 0); lay.setSpacing(6)

        lay.addWidget(title("EMULATE TAG"))
        lay.addWidget(desc("PN532 presents itself as an NFC tag with the given UID."))
        lay.addWidget(warn("Works against readers that only check UID (most cheap access control)."))
        lay.addWidget(divider())

        lbl_uid, f_uid = input_field("UID to emulate (hex)", "04AABBCC", "04AABBCC")
        lay.addWidget(lbl_uid); lay.addWidget(f_uid)
        lay.addWidget(divider())

        log = log_box(210)
        lay.addWidget(log)
        lay.addStretch()

        start = exec_btn("START EMULATION")
        stop  = stop_btn("STOP")

        def do_start():
            self.w._run(emulate.run, {"uid": f_uid.text()}, log, start)
            stop.setEnabled(True)
            f_uid.setEnabled(False)

        def do_stop():
            emulate.stop()
            stop.setEnabled(False)
            start.setEnabled(True)
            f_uid.setEnabled(True)

        start.clicked.connect(do_start)
        stop.clicked.connect(do_stop)

        lay.addWidget(bottom_bar(start, stop, back_btn(self.w._pop)))
        self.w._push(page)
