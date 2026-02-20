#!/usr/bin/env python3
"""SentinelPi — Reverse Shell payload stub"""
import sys, time, argparse
parser = argparse.ArgumentParser()
parser.add_argument("--lhost", default=""); parser.add_argument("--lport", default="4444")
parser.add_argument("--os", default="linux")
args = parser.parse_args()
print(f"[BADUSB] Reverse shell payload — {args.os.upper()}")
print(f"[BADUSB] Listener: {args.lhost}:{args.lport}")
print("[BADUSB] ⚠  LAB USE ONLY")
time.sleep(1); print("[SIM] Payload injected via HID."); sys.exit(0)
