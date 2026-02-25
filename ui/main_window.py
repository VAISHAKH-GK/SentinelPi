from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout,
    QPushButton, QTextEdit, QStackedWidget
)

# Import demo modules
from modules.badusb import custom_script, reverse_shell, send_payload
from modules.infrared import ir_bruteforce, ir_capture, ir_relay, ir_transmission
from modules.wireless import channel_scan, jammer, packet_sniff, replay
from modules.nfc import clone, emulate, read, write


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SentinelPi")
        self.setGeometry(100, 100, 600, 400)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)

        self.main_menu()
    
    def main_menu(self):
        widget = QWidget()
        layout = QVBoxLayout()

        layout.addWidget(self.button("BadUSB", self.badusb_menu))
        layout.addWidget(self.button("Infrared", self.infrared_menu))
        layout.addWidget(self.button("Wireless", self.wireless_menu))
        layout.addWidget(self.button("NFC/RFID", self.nfc_menu))
        layout.addWidget(self.log_output)

        widget.setLayout(layout)
        self.stack.addWidget(widget)
        self.stack.setCurrentWidget(widget)

    def button(self, name, func):
        btn = QPushButton(name)
        btn.clicked.connect(func)
        return btn

    def log(self, text):
        self.log_output.append(text)

    # ---------------- BADUSB ----------------
    def badusb_menu(self):
        self.module_menu("BadUSB", {
            "Custom Script": lambda: self.log(custom_script.run()),
            "Reverse Shell": lambda: self.log(reverse_shell.run()),
            "Send Payload": lambda: self.log(send_payload.run())
        })

    # ---------------- INFRARED ----------------
    def infrared_menu(self):
        self.module_menu("Infrared", {
            "IR Bruteforce": lambda: self.log(ir_bruteforce.run()),
            "IR Capture": lambda: self.log(ir_capture.run()),
            "IR Relay": lambda: self.log(ir_relay.run()),
            "IR Transmission": lambda: self.log(ir_transmission.run())
        })

    # ---------------- WIRELESS ----------------
    def wireless_menu(self):
        self.module_menu("Wireless", {
            "Channel Scan": lambda: self.log(channel_scan.run()),
            "Jammer": lambda: self.log(jammer.run()),
            "Packet Sniff": lambda: self.log(packet_sniff.run()),
            "Replay": lambda: self.log(replay.run())
        })

    # ---------------- NFC ----------------
    def nfc_menu(self):
        self.module_menu("NFC/RFID", {
            "Clone": lambda: self.log(clone.run()),
            "Emulate": lambda: self.log(emulate.run()),
            "Read": lambda: self.log(read.run()),
            "Write": lambda: self.log(write.run())
        })

    def module_menu(self, title, actions):
        widget = QWidget()
        layout = QVBoxLayout()

        for name, action in actions.items():
            btn = QPushButton(name)
            btn.clicked.connect(action)
            layout.addWidget(btn)

        layout.addWidget(self.log_output)

        widget.setLayout(layout)
        self.stack.addWidget(widget)
        self.stack.setCurrentWidget(widget)

