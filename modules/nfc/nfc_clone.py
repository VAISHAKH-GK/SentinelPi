#!/usr/bin/env python3
"""SentinelPi — NFC Clone (stub)"""
import sys, time

print("[NFC CLONE] Step 1: Place SOURCE tag near antenna...")
time.sleep(2)
print("[NFC CLONE] Source tag read: UID 04 A3 B1 22 C4")
print("[NFC CLONE] 16 blocks read successfully.")
print()
print("[NFC CLONE] Step 2: Replace with BLANK writable tag...")
time.sleep(3)
print("[NFC CLONE] Target tag detected.")
print("[NFC CLONE] Writing blocks...")
for i in range(16):
    time.sleep(0.1)
    print(f"[NFC CLONE]   Block {i:02d} ... OK")
print("[NFC CLONE] ✓ Clone complete.")
