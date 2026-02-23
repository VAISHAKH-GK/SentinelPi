#!/usr/bin/env python3
"""
SentinelPi — Entry Point
Run: python3 app/main.py --windowed
"""
import sys
import os

APP_DIR = os.path.dirname(os.path.abspath(__file__))
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from PyQt5.QtWidgets import QApplication
from main_window import MainWindow


def main():
    os.environ.setdefault("QT_AUTO_SCREEN_SCALE_FACTOR", "1")
    app = QApplication(sys.argv)
    app.setApplicationName("SentinelPi")
    app.setStyle("Fusion")

    window = MainWindow()
    if "--windowed" in sys.argv:
        window.resize(800, 480)
        window.show()
    else:
        window.showFullScreen()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
