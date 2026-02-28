# ui/pages/wireless.py
# All wireless attack screens.

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QPushButton,
                              QButtonGroup, QHBoxLayout)
from ui.helpers import (title, divider, desc, warn, log_box, input_field,
                        exec_btn, stop_btn, save_btn, back_btn, bottom_bar)
from modules.wireless import channel_scan, packet_sniff, replay, jammer, mousejack

PAGE_W = 800
PAGE_H = 444
M      = 10


class WirelessPage:
    def __init__(self, window):
        self.w = window

    def build_menu(self):
        self.w._attack_list("WIRELESS", [
            ("Channel Scan",   self._channel_scan),
            ("Packet Sniff",   self._packet_sniff),
            ("Replay Attack",  self._replay),
            ("MouseJack",      self._mousejack),
            ("Jammer",         self._jammer),
        ])

    def _channel_scan(self):
        page = QWidget(); page.setFixedSize(PAGE_W, PAGE_H)
        lay  = QVBoxLayout(page)
        lay.setContentsMargins(M, 8, M, 0); lay.setSpacing(6)

        lay.addWidget(title("CHANNEL SCAN"))
        lay.addWidget(desc("Detect 2.4GHz activity across all 126 channels."))
        lay.addWidget(divider())

        lbl_p, f_passes = input_field("Sample passes (more = accurate, slower)", "3", "3")
        lay.addWidget(lbl_p); lay.addWidget(f_passes)
        lay.addWidget(divider())

        log = log_box(260)
        lay.addWidget(log)
        lay.addStretch()

        run = exec_btn("SCAN")
        run.clicked.connect(lambda: self.w._run(
            channel_scan.run, {"passes": int(f_passes.text() or 3)}, log, run
        ))

        lay.addWidget(bottom_bar(run, save_btn(log, "channel_scan"), back_btn(self.w._pop)))
        self.w._push(page)

    def _packet_sniff(self):
        page = QWidget(); page.setFixedSize(PAGE_W, PAGE_H)
        lay  = QVBoxLayout(page)
        lay.setContentsMargins(M, 8, M, 0); lay.setSpacing(6)

        lay.addWidget(title("PACKET SNIFF"))
        lay.addWidget(desc("Capture raw packets on a channel."))
        lay.addWidget(divider())

        lbl_ch,   f_ch   = input_field("Channel (0-125)", "76", "76")
        lbl_addr, f_addr = input_field("Address (hex)", "E7E7E7E7E7", "E7E7E7E7E7")
        lbl_n,    f_n    = input_field("Packet count (0 = unlimited)", "0", "0")
        lay.addWidget(lbl_ch);   lay.addWidget(f_ch)
        lay.addWidget(lbl_addr); lay.addWidget(f_addr)
        lay.addWidget(lbl_n);    lay.addWidget(f_n)
        lay.addWidget(divider())

        log = log_box(140)
        lay.addWidget(log)
        lay.addStretch()

        start = exec_btn("START SNIFF")
        stop  = stop_btn("STOP")

        def do_start():
            self.w._run(packet_sniff.run, {
                "channel": int(f_ch.text() or 76),
                "address": f_addr.text() or "E7E7E7E7E7",
                "count":   int(f_n.text() or 0),
            }, log, start)
            stop.setEnabled(True)

        def do_stop():
            packet_sniff.stop()
            stop.setEnabled(False)
            start.setEnabled(True)

        start.clicked.connect(do_start)
        stop.clicked.connect(do_stop)

        lay.addWidget(bottom_bar(start, stop, save_btn(log, "packet_sniff"), back_btn(self.w._pop)))
        self.w._push(page)

    def _replay(self):
        page = QWidget(); page.setFixedSize(PAGE_W, PAGE_H)
        lay  = QVBoxLayout(page)
        lay.setContentsMargins(M, 8, M, 0); lay.setSpacing(6)

        lay.addWidget(title("REPLAY ATTACK"))
        lay.addWidget(desc("Capture a packet then retransmit it."))
        lay.addWidget(divider())

        lbl_ch,   f_ch   = input_field("Channel (0-125)", "76", "76")
        lbl_addr, f_addr = input_field("Address (hex)", "E7E7E7E7E7", "E7E7E7E7E7")
        lbl_rep,  f_rep  = input_field("Replay count", "5", "5")
        lbl_dly,  f_dly  = input_field("Delay between replays (s)", "0.5", "0.5")
        lay.addWidget(lbl_ch);   lay.addWidget(f_ch)
        lay.addWidget(lbl_addr); lay.addWidget(f_addr)
        lay.addWidget(lbl_rep);  lay.addWidget(f_rep)
        lay.addWidget(lbl_dly);  lay.addWidget(f_dly)
        lay.addWidget(divider())

        log = log_box(80)
        lay.addWidget(log)
        lay.addStretch()

        btn_cap = exec_btn("CAPTURE")
        btn_rep = QPushButton("REPLAY")
        btn_rep.setObjectName("execBtn"); btn_rep.setFixedHeight(40)
        btn_rep.setEnabled(False)

        def do_capture():
            self.w._run(replay.capture, {
                "channel": int(f_ch.text() or 76),
                "address": f_addr.text() or "E7E7E7E7E7",
            }, log, btn_cap)
            btn_rep.setEnabled(True)

        def do_replay():
            self.w._run(replay.replay, {
                "repeat": int(f_rep.text() or 5),
                "delay":  float(f_dly.text() or 0.5),
            }, log, btn_rep)

        btn_cap.clicked.connect(do_capture)
        btn_rep.clicked.connect(do_replay)

        lay.addWidget(bottom_bar(btn_cap, btn_rep, save_btn(log, "replay"), back_btn(self.w._pop)))
        self.w._push(page)

    def _mousejack(self):
        page = QWidget(); page.setFixedSize(PAGE_W, PAGE_H)
        lay  = QVBoxLayout(page)
        lay.setContentsMargins(M, 8, M, 0); lay.setSpacing(6)

        lay.addWidget(title("MOUSEJACK"))
        lay.addWidget(warn("Targets unencrypted wireless mice/keyboards only."))
        lay.addWidget(divider())

        lbl_ch,   f_ch   = input_field("Channel (from scan)", "62", "62")
        lbl_addr, f_addr = input_field("Target address (hex)", "DC8770D594")
        lbl_txt,  f_txt  = input_field("Text to inject", "calc.exe")
        lay.addWidget(lbl_ch);   lay.addWidget(f_ch)
        lay.addWidget(lbl_addr); lay.addWidget(f_addr)
        lay.addWidget(lbl_txt);  lay.addWidget(f_txt)
        lay.addWidget(divider())

        log = log_box(120)
        lay.addWidget(log)
        lay.addStretch()

        btn_scan   = exec_btn("SCAN FOR TARGETS")
        btn_inject = QPushButton("INJECT")
        btn_inject.setObjectName("execBtn"); btn_inject.setFixedHeight(40)
        btn_inject.setEnabled(False)

        def do_scan():
            self.w._run(mousejack.scan, {}, log, btn_scan)
            btn_inject.setEnabled(True)
            log.append("[*] Copy channel + address into fields above, then Inject.")

        def do_inject():
            self.w._run(mousejack.inject, {
                "channel": int(f_ch.text() or 62),
                "address": f_addr.text(),
                "text":    f_txt.text(),
            }, log, btn_inject)

        btn_scan.clicked.connect(do_scan)
        btn_inject.clicked.connect(do_inject)

        lay.addWidget(bottom_bar(btn_scan, btn_inject, back_btn(self.w._pop)))
        self.w._push(page)

    def _jammer(self):
        page = QWidget(); page.setFixedSize(PAGE_W, PAGE_H)
        lay  = QVBoxLayout(page)
        lay.setContentsMargins(M, 8, M, 0); lay.setSpacing(6)

        lay.addWidget(title("JAMMER"))
        lay.addWidget(warn("Authorised lab use only."))
        lay.addWidget(divider())

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

        lay.addWidget(desc("Power level:"))
        pa_row = QHBoxLayout(); pa_row.setSpacing(6)
        btn_min  = QPushButton("MIN\ndesk")
        btn_low  = QPushButton("LOW\nroom")
        btn_high = QPushButton("HIGH\nwalls")
        btn_max  = QPushButton("MAX\noutdoor")
        pa_btns = [btn_min, btn_low, btn_high, btn_max]
        for b in pa_btns:
            b.setObjectName("attackBtn"); b.setFixedHeight(44)
            b.setCheckable(True); pa_row.addWidget(b)
        pa_grp = QButtonGroup(); pa_grp.setExclusive(True)
        for i, b in enumerate(pa_btns): pa_grp.addButton(b, i)
        btn_low.setChecked(True)
        lay.addLayout(pa_row)

        lay.addWidget(divider())

        log = log_box(80)
        lay.addWidget(log)
        lay.addStretch()

        start    = exec_btn("START JAMMING")
        stop     = stop_btn("STOP")
        all_sels = mode_btns + pa_btns

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
            for b in all_sels: b.setEnabled(False)

        def do_stop():
            jammer.stop()
            stop.setEnabled(False)
            for b in all_sels: b.setEnabled(True)

        start.clicked.connect(do_start)
        stop.clicked.connect(do_stop)

        lay.addWidget(bottom_bar(start, stop, back_btn(self.w._pop)))
        self.w._push(page)
