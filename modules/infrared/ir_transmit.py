#!/usr/bin/env python3
"""SentinelPi — IR Transmit stub"""
import sys, time, argparse
parser = argparse.ArgumentParser()
parser.add_argument("--code", default="0x20DF10EF"); parser.add_argument("--protocol", default="NEC")
args = parser.parse_args()
print(f"[IR TX] Protocol : {args.protocol}")
print(f"[IR TX] Code     : {args.code}")
time.sleep(0.5); print("[IR TX] ✓ Transmitted.")
