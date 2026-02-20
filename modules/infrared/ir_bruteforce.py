#!/usr/bin/env python3
"""SentinelPi — IR Brute Force stub"""
import sys, time, argparse
parser = argparse.ArgumentParser()
parser.add_argument("--device", default="tv"); parser.add_argument("--start", type=int, default=0)
parser.add_argument("--end", type=int, default=255)
args = parser.parse_args()
print(f"[IR BRUTE] Device: {args.device.upper()}  Range: {args.start:#04x}–{args.end:#04x}")
print("[IR BRUTE] ⚠  Point at target device. Starting in 3s..."); time.sleep(3)
try:
    for code in range(args.start, args.end + 1):
        print(f"[IR BRUTE] TX {code:#06x}", end="\r", flush=True)
        time.sleep(0.08)
    print(f"\n[IR BRUTE] Done — {args.end - args.start + 1} codes sent.")
except KeyboardInterrupt:
    print("\n[IR BRUTE] Stopped.")
