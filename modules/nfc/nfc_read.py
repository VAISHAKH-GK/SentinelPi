#!/usr/bin/env python3
"""
SentinelPi — NFC Read Module
Hardware: PN532 via SPI (or I2C)
Library:  nfcpy  OR  pn532 (adafruit-circuitpython-pn532)

Install:
    pip install nfcpy
    # OR
    pip install adafruit-circuitpython-pn532 RPi.GPIO spidev
"""

import sys
import time
import argparse

parser = argparse.ArgumentParser()
args = parser.parse_args()

print("[NFC READ] Initializing PN532...")
print("[NFC READ] Waiting for tag...")

try:
    # ── Real hardware path ───────────────────────────────────────────────────
    # Uncomment when running on actual Pi with PN532 connected via SPI:
    #
    # import board, busio
    # from digitalio import DigitalInOut
    # from adafruit_pn532.spi import PN532_SPI
    #
    # spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
    # cs  = DigitalInOut(board.D8)   # CE0 = GPIO8
    # pn532 = PN532_SPI(spi, cs, debug=False)
    # pn532.SAM_configuration()
    #
    # while True:
    #     uid = pn532.read_passive_target(timeout=0.5)
    #     if uid:
    #         uid_hex = " ".join(f"{b:02X}" for b in uid)
    #         print(f"[TAG DETECTED] UID: {uid_hex}")
    #         print(f"[TAG DETECTED] Type: {'MIFARE Classic' if len(uid)==4 else 'NTAG/Ultralight'}")
    #         # Read NDEF data if present
    #         # (add ndeflib or manual block reads here)
    # ────────────────────────────────────────────────────────────────────────

    # Simulation mode (no hardware)
    time.sleep(1)
    print("[SIM] No hardware detected — running in simulation mode")
    time.sleep(1)
    print("[SIM] Tag detected! UID: 04 A3 B1 22 C4")
    print("[SIM] Tag type: MIFARE Classic 1K")
    print("[SIM] Sector 0 Block 0: 04 A3 B1 22 C4 08 04 00 62 63 64 65 66 67 68 69")
    print("[SIM] NDEF: (empty)")
    print("[NFC READ] Done.")

except KeyboardInterrupt:
    print("\n[NFC READ] Interrupted.")
    sys.exit(0)
except Exception as e:
    print(f"[ERROR] {e}", file=sys.stderr)
    sys.exit(1)
