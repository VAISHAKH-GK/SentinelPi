#!/usr/bin/env python3
"""SentinelPi — NFC Emulate (stub)"""
import sys, time, argparse

parser = argparse.ArgumentParser()
parser.add_argument("--uid", default="04 AA BB CC")
args = parser.parse_args()

print(f"[NFC EMULATE] Emulating UID: {args.uid}")
print("[NFC EMULATE] Pi now appears as an NFC tag to readers.")
print("[NFC EMULATE] Press STOP to end emulation.")

try:
    while True:
        time.sleep(2)
        print("[NFC EMULATE] Listening for reader...")
except KeyboardInterrupt:
    print("\n[NFC EMULATE] Stopped.")
