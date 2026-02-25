# ui/pages/wireless.py
# Wireless attack screens.
# Add a new attack: write a method + add it to build_menu()

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QButtonGroup, QHBoxLayout
from ui.helpers import (title, divider, desc, warn, log_box, input_field,
                        exec_btn, stop_btn, save_btn, back_btn, bottom_bar)
from modules.wireless import channel_scan, jammer, packet_sniff, replay

PAGE_W = 800
PAGE_H = 444
M      = 10


class WirelessPage:
    def __init__(self, window):
        self.w = window

    def build_menu(self):
        self.w._attack_list("WIRELESS", [
            ("Channel Scan",  self._channel_scan),
            ("Packet Sniff",  self._packet_sniff),
            ("Replay Attack", self._replay),
            ("Jammer",        self._jammer),
        ])

    # ── Channel Scan ──────────────────────────────────────────────────

    def _channel_scan(self):
        page = QWidget(); page.setFixedSize(PAGE_W, PAGE_H)
        lay  = QVBoxLayout(page)
        lay.setContentsMargins(M, 8, M, 0)
        lay.setSpacing(6)

        lay.addWidget(title("CHANNEL SCAN"))
        lay.addWidget(desc("Scan 2.4 GHz channels for activity."))
        lay.addWidget(divider())

        log = log_box(310)
        lay.addWidget(log)
        lay.addStretch()

        run = exec_btn("SCAN")
        run.clicked.connect(lambda: self.w._run(channel_scan.run, {}, log, run))

        lay.addWidget(bottom_bar(run, save_btn(log, "channel_scan"), back_btn(self.w._pop)))
        self.w._push(page)

    # ── Packet Sniff ──────────────────────────────────────────────────

    def _packet_sniff(self):
        page = QWidget(); page.setFixedSize(PAGE_W, PAGE_H)
        lay  = QVBoxLayout(page)
        lay.setContentsMargins(M, 8, M, 0)
        lay.setSpacing(6)

        lay.addWidget(title("PACKET SNIFF"))
        lay.addWidget(divider())

        lbl_ch, f_ch = input_field("Channel (1-125)", "1", "1")
        lbl_n,  f_n  = input_field("Packet count (0 = unlimited)", "0", "0")
        lay.addWidget(lbl_ch); lay.addWidget(f_ch)
        lay.addWidget(lbl_n);  lay.addWidget(f_n)
        lay.addWidget(divider())

        log = log_box(220)
        lay.addWidget(log)
        lay.addStretch()

        run = exec_btn("START SNIFF")
        run.clicked.connect(lambda: self.w._run(packet_sniff.run, {}, log, run))

        lay.addWidget(bottom_bar(run, save_btn(log, "packet_sniff"), back_btn(self.w._pop)))
        self.w._push(page)

    # ── Replay Attack ─────────────────────────────────────────────────

    def _replay(self):
        page = QWidget(); page.setFixedSize(PAGE_W, PAGE_H)
        lay  = QVBoxLayout(page)
        lay.setContentsMargins(M, 8, M, 0)
        lay.setSpacing(6)

        lay.addWidget(title("REPLAY ATTACK"))
        lay.addWidget(desc("Load a saved capture file and replay it."))
        lay.addWidget(divider())

        lbl_f, f_file = input_field("Capture filename", "my_capture.txt")
        lbl_r, f_rep  = input_field("Repeat count", "1", "1")
        lay.addWidget(lbl_f); lay.addWidget(f_file)
        lay.addWidget(lbl_r); lay.addWidget(f_rep)
        lay.addWidget(divider())

        log = log_box(220)
        lay.addWidget(log)
        lay.addStretch()

        run = exec_btn("REPLAY")
        run.clicked.connect(lambda: self.w._run(replay.run, {}, log, run))

        lay.addWidget(bottom_bar(run, back_btn(self.w._pop)))
        self.w._push(page)

    # ── Jammer ────────────────────────────────────────────────────────

    def _jammer(self):
        page = QWidget(); page.setFixedSize(PAGE_W, PAGE_H)
        lay  = QVBoxLayout(page)
        lay.setContentsMargins(M, 8, M, 0)
        lay.setSpacing(6)

        lay.addWidget(title("JAMMER"))
        lay.addWidget(warn("Authorised lab use only."))
        lay.addWidget(divider())

        # ── Channel mode selector ──────────────────────────────────
        lay.addWidget(desc("Channel mode:"))
        mode_row = QHBoxLayout(); mode_row.setSpacing(6)
        btn_full = QPushButton("FULL (0-79)")
        btn_ble  = QPushButton("BLE (37,38,39)")
        btn_wifi = QPushButton("WIFI (1,6,11)")
        mode_btns = [btn_full, btn_ble, btn_wifi]
        for b in mode_btns:
            b.setObjectName("attackBtn"); b.setFixedHeight(44)
            b.setCheckable(True); mode_row.addWidget(b)
        mode_grp = QButtonGroup(); mode_grp.setExclusive(True)
        for i, b in enumerate(mode_btns): mode_grp.addButton(b, i)
        btn_full.setChecked(True)
        lay.addLayout(mode_row)

        # ── PA level selector ──────────────────────────────────────
        lay.addWidget(desc("Power level:"))
        pa_row = QHBoxLayout(); pa_row.setSpacing(6)
        btn_min  = QPushButton("MIN\ndesk")
        btn_low  = QPushButton("LOW\nroom")
        btn_high = QPushButton("HIGH\nwalls")
        btn_max  = QPushButton("MAX\noutdoor")
        pa_btns  = [btn_min, btn_low, btn_high, btn_max]
        for b in pa_btns:
            b.setObjectName("attackBtn"); b.setFixedHeight(44)
            b.setCheckable(True); pa_row.addWidget(b)
        pa_grp = QButtonGroup(); pa_grp.setExclusive(True)
        for i, b in enumerate(pa_btns): pa_grp.addButton(b, i)
        btn_low.setChecked(True)   # safe default for bench testing
        lay.addLayout(pa_row)

        lay.addWidget(divider())
        # ── end selectors ──────────────────────────────────────────

        log = log_box(140)
        lay.addWidget(log)
        lay.addStretch()

        start = exec_btn("START JAMMING")
        stop  = stop_btn("STOP")
        all_sel = mode_btns + pa_btns

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
            log.append(f"[*] Starting — mode:{get_mode()}  PA:{get_pa()}")
            self.w._run(jammer.run, {"mode": get_mode(), "pa_level": get_pa()}, log, start)
            stop.setEnabled(True)
            for b in all_sel: b.setEnabled(False)

        def do_stop():
            jammer.stop()
            stop.setEnabled(False)
            for b in all_sel: b.setEnabled(True)

        start.clicked.connect(do_start)
        stop.clicked.connect(do_stop)

        lay.addWidget(bottom_bar(start, stop, back_btn(self.w._pop)))
        self.w._push(page)
