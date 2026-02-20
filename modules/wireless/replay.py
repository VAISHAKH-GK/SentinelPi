#!/usr/bin/env python3
"""SentinelPi — Replay stub"""
import sys, time, argparse

parser = argparse.ArgumentParser()
parser.add_argument("--file", default="")
args = parser.parse_args()
print(f"[RF REPLAY] File: {args.file or '(none specified)'}")
if not args.file:
    print("[RF REPLAY] Error: no capture file specified."); sys.exit(1)
print("[RF REPLAY] Transmitting captured packets...")
time.sleep(2)
print("[RF REPLAY] Done — 48 packets replayed.")
