# ui/pages/wireless.py
# All Wireless attack screens live here.
# To add a new attack:
#   1. Write a new method like _my_attack(self)
#   2. Add it to the list in build_menu()

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QButtonGroup, QHBoxLayout
from ui.helpers import title, divider, desc, log_box, input_field, exec_btn, stop_btn, save_btn, back_btn, btn_row

from modules.wireless import channel_scan, jammer, packet_sniff, replay


class WirelessPage:
    def __init__(self, window):
        self.w = window

    def build_menu(self):
        attacks = [
            ("Channel Scan",  self._channel_scan),
            ("Packet Sniff",  self._packet_sniff),
            ("Replay Attack", self._replay),
            ("Jammer",        self._jammer),
        ]
        self.w._attack_list("WIRELESS", attacks)

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

        # ── Mode selector ──────────────────────────────────────────────
        lay.addWidget(desc("Channel mode:"))
        mode_row = QHBoxLayout()
        mode_row.setSpacing(8)
        btn_full = QPushButton("FULL\n(0-79)")
        btn_ble  = QPushButton("BLE\n(37,38,39)")
        btn_wifi = QPushButton("WIFI\n(1,6,11)")
        for b in [btn_full, btn_ble, btn_wifi]:
            b.setObjectName("attackBtn")
            b.setMinimumHeight(56)
            b.setCheckable(True)
            mode_row.addWidget(b)
        mode_group = QButtonGroup()
        mode_group.addButton(btn_full, 0)
        mode_group.addButton(btn_ble,  1)
        mode_group.addButton(btn_wifi, 2)
        mode_group.setExclusive(True)
        btn_full.setChecked(True)
        lay.addLayout(mode_row)

        # ── PA level selector ──────────────────────────────────────────
        lay.addWidget(desc("Power level:"))
        pa_row = QHBoxLayout()
        pa_row.setSpacing(8)
        btn_min  = QPushButton("MIN\nsame desk")
        btn_low  = QPushButton("LOW\nsame room")
        btn_high = QPushButton("HIGH\nthrough walls")
        btn_max  = QPushButton("MAX\noutdoor")
        for b in [btn_min, btn_low, btn_high, btn_max]:
            b.setObjectName("attackBtn")
            b.setMinimumHeight(56)
            b.setCheckable(True)
            pa_row.addWidget(b)
        pa_group = QButtonGroup()
        pa_group.addButton(btn_min,  0)
        pa_group.addButton(btn_low,  1)
        pa_group.addButton(btn_high, 2)
        pa_group.addButton(btn_max,  3)
        pa_group.setExclusive(True)
        btn_low.setChecked(True)    # default = LOW, safe for bench testing
        lay.addLayout(pa_row)

        lay.addWidget(divider())
        # ── end selectors ──────────────────────────────────────────────

        log = log_box()
        lay.addWidget(log)

        start = exec_btn("START JAMMING")
        stop  = stop_btn("STOP")

        all_btns = [btn_full, btn_ble, btn_wifi, btn_min, btn_low, btn_high, btn_max]

        def get_mode():
            if btn_ble.isChecked():  return "ble"
            if btn_wifi.isChecked(): return "wifi"
            return "full"

        def get_pa():
            if btn_min.isChecked():  return "MIN"
            if btn_high.isChecked(): return "HIGH"
            if btn_max.isChecked():  return "MAX"
            return "LOW"

        def do_start():
            mode = get_mode()
            pa   = get_pa()
            log.append(f"[*] Starting — mode: {mode}  PA: {pa}")
            self.w._run(jammer.run, {"mode": mode, "pa_level": pa}, log, start)
            stop.setEnabled(True)
            for b in all_btns:
                b.setEnabled(False)

        def do_stop():
            jammer.stop()
            stop.setEnabled(False)
            for b in all_btns:
                b.setEnabled(True)

        start.clicked.connect(do_start)
        stop.clicked.connect(do_stop)

        lay.addLayout(btn_row(start, stop, back_btn(self.w._pop)))
        self.w._push(page)

