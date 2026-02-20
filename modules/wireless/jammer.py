#!/usr/bin/env python3
"""SentinelPi — Jammer Demo stub (SHIELDED LAB ONLY)"""
import sys, time
print("[RF JAM] ⚠  DEMO MODE — ensure shielded enclosure")
print("[RF JAM] Transmitting noise on all 2.4 GHz channels...")
try:
    i = 0
    while True:
        i += 1
        print(f"[RF JAM] Sweep {i:04d} complete")
        time.sleep(1)
except KeyboardInterrupt:
    print("\n[RF JAM] Stopped.")
