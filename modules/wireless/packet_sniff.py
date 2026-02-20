#!/usr/bin/env python3
"""SentinelPi — Packet Sniffer stub"""
import sys, time, argparse, random

parser = argparse.ArgumentParser()
parser.add_argument("--channel", type=int, default=76)
parser.add_argument("--address", default=None)
args = parser.parse_args()

print(f"[RF SNIFF] Channel : {args.channel} ({2400+args.channel} MHz)")
print(f"[RF SNIFF] Address : {args.address or 'promiscuous'}")
print("[RF SNIFF] Listening for packets...\n")

try:
    pkt_id = 0
    while True:
        time.sleep(random.uniform(0.3, 1.5))
        pkt_id += 1
        size   = random.randint(4, 32)
        data   = " ".join(f"{random.randint(0,255):02X}" for _ in range(size))
        print(f"[PKT #{pkt_id:04d}] len={size:2d}  {data}")
except KeyboardInterrupt:
    print(f"\n[RF SNIFF] Captured {pkt_id} packets.")
    sys.exit(0)
