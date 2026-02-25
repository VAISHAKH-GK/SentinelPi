# ui/pages/infrared.py
# All Infrared attack screens live here.
# To add a new attack:
#   1. Write a new method like _my_attack(self)
#   2. Add it to the list in build_menu()

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton
from ui.helpers import title, divider, desc, log_box, input_field, exec_btn, stop_btn, save_btn, back_btn, btn_row

from modules.infrared import ir_capture, ir_transmission, ir_relay, ir_bruteforce


class InfraredPage:
    def __init__(self, window):
        self.w = window

    # ── Menu ─────────────────────────────────────────────────────────────

    def build_menu(self):
        attacks = [
            ("IR Capture",    self._ir_capture),
            ("IR Transmit",   self._ir_transmit),
            ("IR Relay",      self._ir_relay),
            ("IR Bruteforce", self._ir_bruteforce),
        ]
        self.w._attack_list("INFRARED", attacks)

    # ── Attack screens ────────────────────────────────────────────────────

    def _ir_capture(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(16, 10, 16, 10)
        lay.setSpacing(8)

        lay.addWidget(title("IR CAPTURE"))
        lay.addWidget(desc("Point remote at receiver and press Capture."))
        lay.addWidget(divider())

        log = log_box()
        lay.addWidget(log)

        run = exec_btn("CAPTURE")
        run.clicked.connect(lambda: self.w._run(ir_capture.run, {}, log, run))

        lay.addLayout(btn_row(run, save_btn(log, "ir_capture"), back_btn(self.w._pop)))
        self.w._push(page)

    def _ir_transmit(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(16, 10, 16, 10)
        lay.setSpacing(8)

        lay.addWidget(title("IR TRANSMIT"))
        lay.addWidget(divider())

        lbl_freq, f_freq = input_field("Frequency (kHz)", "38", "38")
        lbl_data, f_data = input_field("Signal Data (hex or raw)", "AA BB CC ...")
        lay.addWidget(lbl_freq); lay.addWidget(f_freq)
        lay.addWidget(lbl_data); lay.addWidget(f_data)
        lay.addWidget(divider())

        log = log_box(100)
        lay.addWidget(log)

        run = exec_btn("TRANSMIT")
        # When run() accepts args: {"freq": f_freq.text(), "data": f_data.text()}
        run.clicked.connect(lambda: self.w._run(ir_transmission.run, {}, log, run))

        lay.addLayout(btn_row(run, back_btn(self.w._pop)))
        self.w._push(page)

    def _ir_relay(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(16, 10, 16, 10)
        lay.setSpacing(8)

        lay.addWidget(title("IR RELAY"))
        lay.addWidget(desc("Captures and immediately re-transmits IR signals."))
        lay.addWidget(divider())

        log = log_box()
        lay.addWidget(log)

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

        lay.addLayout(btn_row(start, stop, back_btn(self.w._pop)))
        self.w._push(page)

    def _ir_bruteforce(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(16, 10, 16, 10)
        lay.setSpacing(8)

        lay.addWidget(title("IR BRUTEFORCE"))
        lay.addWidget(divider())

        lbl_start, f_start = input_field("Start Code (hex)", "0x00", "0x00")
        lbl_end,   f_end   = input_field("End Code (hex)",   "0xFF", "0xFF")
        lbl_delay, f_delay = input_field("Delay between codes (ms)", "200", "200")
        lay.addWidget(lbl_start); lay.addWidget(f_start)
        lay.addWidget(lbl_end);   lay.addWidget(f_end)
        lay.addWidget(lbl_delay); lay.addWidget(f_delay)
        lay.addWidget(divider())

        log = log_box(80)
        lay.addWidget(log)

        run = exec_btn("START")
        run.clicked.connect(lambda: self.w._run(ir_bruteforce.run, {}, log, run))

        lay.addLayout(btn_row(run, save_btn(log, "ir_bruteforce"), back_btn(self.w._pop)))
        self.w._push(page)
