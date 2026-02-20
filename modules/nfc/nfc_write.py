#!/usr/bin/env python3
"""
SentinelPi — NFC Write Module
Writes data to a writable MIFARE/NTAG tag via PN532.
"""

import sys, time, argparse

parser = argparse.ArgumentParser()
parser.add_argument("--uid",  default="", help="Target UID (optional filter)")
parser.add_argument("--data", default="SentinelPi", help="Data to write")
args = parser.parse_args()

print(f"[NFC WRITE] Target UID : {args.uid or 'any'}")
print(f"[NFC WRITE] Data       : {args.data}")
print("[NFC WRITE] Place a writable tag near the antenna...")

try:
    # ── Real hardware ────────────────────────────────────────────────────────
    # pn532 = ...  (same init as nfc_read.py)
    # uid = pn532.read_passive_target(timeout=5)
    # if uid:
    #     if args.uid and " ".join(f"{b:02X}" for b in uid) != args.uid.upper():
    #         print("[NFC WRITE] UID mismatch — aborting")
    #         sys.exit(1)
    #     pn532.ntag2xx_write_block(4, args.data[:4].encode().ljust(4, b'\x00'))
    #     print("[NFC WRITE] Write successful")
    # ────────────────────────────────────────────────────────────────────────

    time.sleep(1.5)
    print("[SIM] Tag found: 04 A3 B1 22 C4")
    time.sleep(0.5)
    print(f"[SIM] Writing '{args.data}' to block 4...")
    time.sleep(0.8)
    print("[SIM] Verifying write...")
    time.sleep(0.3)
    print("[NFC WRITE] ✓ Write successful.")

except KeyboardInterrupt:
    print("\n[NFC WRITE] Interrupted.")
    sys.exit(0)
except Exception as e:
    print(f"[ERROR] {e}", file=sys.stderr)
    sys.exit(1)
