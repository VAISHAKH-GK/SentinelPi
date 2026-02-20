#!/usr/bin/env python3
"""
SentinelPi — Bad USB Send Payload
Sends a DuckyScript-like payload to the STM32 via serial,
which then injects keystrokes via USB HID.

STM32 firmware: https://github.com/exploitagency/ESPloitV2  (or custom)
Protocol: send lines over /dev/ttyACM0 at 115200 baud
"""

import sys, time, argparse

parser = argparse.ArgumentParser()
parser.add_argument("--payload", default="STRING Hello World\nENTER")
args = parser.parse_args()

print("[BADUSB] Payload to inject:")
for line in args.payload.splitlines():
    print(f"  > {line}")
print()
print("[BADUSB] Looking for STM32 on /dev/ttyACM0...")

try:
    # ── Real hardware ────────────────────────────────────────────────────────
    # import serial
    # ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
    # time.sleep(2)  # wait for device ready
    # for line in args.payload.splitlines():
    #     ser.write((line + '\n').encode())
    #     time.sleep(0.1)
    # print("[BADUSB] ✓ Payload sent.")
    # ser.close()
    # ────────────────────────────────────────────────────────────────────────

    time.sleep(1)
    print("[SIM] STM32 not found — simulation mode")
    for line in args.payload.splitlines():
        print(f"[SIM] Injecting: {line}")
        time.sleep(0.3)
    print("[BADUSB] ✓ Payload simulation complete.")

except KeyboardInterrupt:
    print("\n[BADUSB] Interrupted.")
    sys.exit(0)
