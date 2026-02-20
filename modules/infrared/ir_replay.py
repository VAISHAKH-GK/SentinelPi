#!/usr/bin/env python3
"""SentinelPi — IR Replay stub"""
import sys, time, argparse, json

parser = argparse.ArgumentParser()
parser.add_argument("--file", default="/tmp/ir_capture.json")
args = parser.parse_args()

print(f"[IR REPLAY] File: {args.file}")
try:
    with open(args.file) as f:
        data = json.load(f)
    print(f"[IR REPLAY] Protocol : {data.get('protocol','?')}")
    print(f"[IR REPLAY] Code     : {data.get('raw_code','?')}")
    # Real: use pigpio to replay data['pulses'] on GPIO17 (IR_OUT)
    time.sleep(1)
    print("[IR REPLAY] ✓ Signal transmitted.")
except FileNotFoundError:
    print(f"[IR REPLAY] File not found: {args.file}"); sys.exit(1)
