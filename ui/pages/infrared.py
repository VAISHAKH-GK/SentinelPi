# ui/pages/infrared.py
# Infrared attack screens.
# Add a new attack: write a method + add it to build_menu()

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton
from ui.helpers import (title, divider, desc, log_box, input_field,
                        exec_btn, stop_btn, save_btn, back_btn, bottom_bar)
from modules.infrared import ir_capture, ir_transmission, ir_relay, ir_bruteforce

PAGE_W = 800
PAGE_H = 444
M      = 10


class InfraredPage:
    def __init__(self, window):
        self.w = window

    def build_menu(self):
        self.w._attack_list("INFRARED", [
            ("IR Capture",    self._ir_capture),
            ("IR Transmit",   self._ir_transmit),
            ("IR Relay",      self._ir_relay),
            ("IR Bruteforce", self._ir_bruteforce),
        ])

    # ── IR Capture ────────────────────────────────────────────────────

    def _ir_capture(self):
        page = QWidget(); page.setFixedSize(PAGE_W, PAGE_H)
        lay  = QVBoxLayout(page)
        lay.setContentsMargins(M, 8, M, 0)
        lay.setSpacing(6)

        lay.addWidget(title("IR CAPTURE"))
        lay.addWidget(desc("Point remote at receiver and press Capture."))
        lay.addWidget(divider())

        log = log_box(300)
        lay.addWidget(log)
        lay.addStretch()

        run = exec_btn("CAPTURE")
        run.clicked.connect(lambda: self.w._run(ir_capture.run, {}, log, run))

        lay.addWidget(bottom_bar(run, save_btn(log, "ir_capture"), back_btn(self.w._pop)))
        self.w._push(page)

    # ── IR Transmit ───────────────────────────────────────────────────

    def _ir_transmit(self):
        page = QWidget(); page.setFixedSize(PAGE_W, PAGE_H)
        lay  = QVBoxLayout(page)
        lay.setContentsMargins(M, 8, M, 0)
        lay.setSpacing(6)

        lay.addWidget(title("IR TRANSMIT"))
        lay.addWidget(divider())

        lbl_freq, f_freq = input_field("Frequency (kHz)", "38", "38")
        lbl_data, f_data = input_field("Signal Data (hex or raw)", "AA BB CC ...")
        lay.addWidget(lbl_freq); lay.addWidget(f_freq)
        lay.addWidget(lbl_data); lay.addWidget(f_data)
        lay.addWidget(divider())

        log = log_box(220)
        lay.addWidget(log)
        lay.addStretch()

        run = exec_btn("TRANSMIT")
        run.clicked.connect(lambda: self.w._run(ir_transmission.run, {}, log, run))

        lay.addWidget(bottom_bar(run, back_btn(self.w._pop)))
        self.w._push(page)

    # ── IR Relay ──────────────────────────────────────────────────────

    def _ir_relay(self):
        page = QWidget(); page.setFixedSize(PAGE_W, PAGE_H)
        lay  = QVBoxLayout(page)
        lay.setContentsMargins(M, 8, M, 0)
        lay.setSpacing(6)

        lay.addWidget(title("IR RELAY"))
        lay.addWidget(desc("Captures and immediately re-transmits IR signals."))
        lay.addWidget(divider())

        log = log_box(300)
        lay.addWidget(log)
        lay.addStretch()

        start = exec_btn("START RELAY")
        stop  = stop_btn("STOP")

        def do_start():
            self.w._run(ir_relay.run, {}, log, start)
            stop.setEnabled(True)

        def do_stop():
            if self.w._worker:
                self.w._worker.terminate()
            log.append("[*] Relay stopped.")
            stop.setEnabled(False)
            start.setEnabled(True)

        start.clicked.connect(do_start)
        stop.clicked.connect(do_stop)

        lay.addWidget(bottom_bar(start, stop, back_btn(self.w._pop)))
        self.w._push(page)

    # ── IR Bruteforce ─────────────────────────────────────────────────

    def _ir_bruteforce(self):
        page = QWidget(); page.setFixedSize(PAGE_W, PAGE_H)
        lay  = QVBoxLayout(page)
        lay.setContentsMargins(M, 8, M, 0)
        lay.setSpacing(6)

        lay.addWidget(title("IR BRUTEFORCE"))
        lay.addWidget(divider())

        lbl_s, f_s = input_field("Start Code (hex)", "0x00", "0x00")
        lbl_e, f_e = input_field("End Code (hex)",   "0xFF", "0xFF")
        lbl_d, f_d = input_field("Delay per code (ms)", "200", "200")
        lay.addWidget(lbl_s); lay.addWidget(f_s)
        lay.addWidget(lbl_e); lay.addWidget(f_e)
        lay.addWidget(lbl_d); lay.addWidget(f_d)
        lay.addWidget(divider())

        log = log_box(160)
        lay.addWidget(log)
        lay.addStretch()

        run = exec_btn("START")
        run.clicked.connect(lambda: self.w._run(ir_bruteforce.run, {}, log, run))

        lay.addWidget(bottom_bar(run, save_btn(log, "ir_bruteforce"), back_btn(self.w._pop)))
        self.w._push(page)
