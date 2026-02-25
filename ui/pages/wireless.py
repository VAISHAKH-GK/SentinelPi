# ui/pages/wireless.py
# All Wireless attack screens live here.
# To add a new attack:
#   1. Write a new method like _my_attack(self)
#   2. Add it to the list in build_menu()

from PyQt5.QtWidgets import QWidget, QVBoxLayout
from ui.helpers import title, divider, desc, log_box, input_field, exec_btn, stop_btn, save_btn, back_btn, btn_row

from modules.wireless import channel_scan, jammer, packet_sniff, replay


class WirelessPage:
    def __init__(self, window):
        self.w = window

    # ── Menu ─────────────────────────────────────────────────────────────

    def build_menu(self):
        attacks = [
            ("Channel Scan",  self._channel_scan),
            ("Packet Sniff",  self._packet_sniff),
            ("Replay Attack", self._replay),
            ("Jammer",        self._jammer),
        ]
        self.w._attack_list("WIRELESS", attacks)

    # ── Attack screens ────────────────────────────────────────────────────

    def _channel_scan(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(16, 10, 16, 10)
        lay.setSpacing(8)

        lay.addWidget(title("CHANNEL SCAN"))
        lay.addWidget(desc("Scan all 2.4 GHz channels for activity."))
        lay.addWidget(divider())

        log = log_box()
        lay.addWidget(log)

        run = exec_btn("SCAN")
        run.clicked.connect(lambda: self.w._run(channel_scan.run, {}, log, run))

        lay.addLayout(btn_row(run, save_btn(log, "channel_scan"), back_btn(self.w._pop)))
        self.w._push(page)

    def _packet_sniff(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(16, 10, 16, 10)
        lay.setSpacing(8)

        lay.addWidget(title("PACKET SNIFF"))
        lay.addWidget(divider())

        lbl_ch, f_ch = input_field("Channel (1-125)", "1", "1")
        lbl_n,  f_n  = input_field("Packet count (0 = unlimited)", "0", "0")
        lay.addWidget(lbl_ch); lay.addWidget(f_ch)
        lay.addWidget(lbl_n);  lay.addWidget(f_n)
        lay.addWidget(divider())

        log = log_box()
        lay.addWidget(log)

        run = exec_btn("START SNIFF")
        # When run() accepts args: {"channel": f_ch.text(), "count": f_n.text()}
        run.clicked.connect(lambda: self.w._run(packet_sniff.run, {}, log, run))

        lay.addLayout(btn_row(run, save_btn(log, "packet_sniff"), back_btn(self.w._pop)))
        self.w._push(page)

    def _replay(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(16, 10, 16, 10)
        lay.setSpacing(8)

        lay.addWidget(title("REPLAY ATTACK"))
        lay.addWidget(desc("Load a saved capture file and replay it."))
        lay.addWidget(divider())

        lbl_file, f_file = input_field("Capture filename", "my_capture.txt")
        lbl_rep,  f_rep  = input_field("Repeat count", "1", "1")
        lay.addWidget(lbl_file); lay.addWidget(f_file)
        lay.addWidget(lbl_rep);  lay.addWidget(f_rep)
        lay.addWidget(divider())

        log = log_box(100)
        lay.addWidget(log)

        run = exec_btn("REPLAY")
        # When run() accepts args: {"file": f_file.text(), "repeat": f_rep.text()}
        run.clicked.connect(lambda: self.w._run(replay.run, {}, log, run))

        lay.addLayout(btn_row(run, back_btn(self.w._pop)))
        self.w._push(page)

    def _jammer(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(16, 10, 16, 10)
        lay.setSpacing(8)

        lay.addWidget(title("JAMMER"))
        lay.addWidget(desc("WARNING: Authorised lab use only."))
        lay.addWidget(divider())

        lbl_ch, f_ch = input_field("Target Channel (1-125)", "1", "1")
        lay.addWidget(lbl_ch); lay.addWidget(f_ch)
        lay.addWidget(divider())

        log = log_box(100)
        lay.addWidget(log)

        start = exec_btn("START JAMMING")
        stop  = stop_btn("STOP")

        def do_start():
            self.w._run(jammer.run, {}, log, start)
            stop.setEnabled(True)

        def do_stop():
            if self.w._worker:
                self.w._worker.terminate()
            log.append("[*] Jammer stopped.")
            stop.setEnabled(False)
            start.setEnabled(True)

        start.clicked.connect(do_start)
        stop.clicked.connect(do_stop)

        lay.addLayout(btn_row(start, stop, back_btn(self.w._pop)))
        self.w._push(page)
