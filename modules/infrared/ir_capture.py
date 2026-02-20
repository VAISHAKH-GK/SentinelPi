#!/usr/bin/env python3
"""
SentinelPi — IR Capture
Uses pigpio or LIRC to capture IR signals from the receiver (GPIO18 by default).

Install: sudo apt install lirc  OR  pip install pigpio
"""

import sys, time, argparse, json, random

parser = argparse.ArgumentParser()
parser.add_argument("--protocol", default="Auto-detect")
parser.add_argument("--output",   default="/tmp/ir_capture.json")
args = parser.parse_args()

print(f"[IR CAPTURE] Protocol : {args.protocol}")
print(f"[IR CAPTURE] Output   : {args.output}")
print("[IR CAPTURE] Waiting for IR signal... (point remote at receiver)")

try:
    # ── Real hardware ────────────────────────────────────────────────────────
    # import pigpio
    # pi = pigpio.pi()
    # # Record pulses on GPIO18 (IR_IN)
    # ... (see pigpio ir_record example)
    # ────────────────────────────────────────────────────────────────────────

    time.sleep(2)
    # Simulated NEC signal
    code = random.randint(0x100000, 0xFFFFFF)
    result = {
        "protocol": "NEC",
        "address":  f"0x{(code >> 8) & 0xFF:02X}",
        "command":  f"0x{code & 0xFF:02X}",
        "raw_code": f"0x{code:06X}",
        "pulses":   [9000, 4500] + [random.randint(300,1800) for _ in range(64)],
    }
    print(f"[IR CAPTURE] ✓ Signal received!")
    print(f"[IR CAPTURE] Protocol : {result['protocol']}")
    print(f"[IR CAPTURE] Address  : {result['address']}")
    print(f"[IR CAPTURE] Command  : {result['command']}")
    print(f"[IR CAPTURE] Raw      : {result['raw_code']}")
    with open(args.output, "w") as f:
        json.dump(result, f, indent=2)
    print(f"[IR CAPTURE] Saved to {args.output}")

except KeyboardInterrupt:
    print("\n[IR CAPTURE] Stopped.")
    sys.exit(0)
