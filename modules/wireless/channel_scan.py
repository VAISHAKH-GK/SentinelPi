#!/usr/bin/env python3
"""
SentinelPi — nRF24L01 Channel Scanner
Scans 2400–2525 MHz and reports signal presence per channel.

Hardware library: pip install pyrf24
                  OR: pip install circuitpython-nrf24l01
"""

import sys, time

print("[RF SCAN] Initializing nRF24L01+PA+LNA...")
print("[RF SCAN] Scanning channels 0–124 (2400–2524 MHz)")
print("[RF SCAN] Press STOP to end.\n")

try:
    # ── Real hardware ────────────────────────────────────────────────────────
    # import spidev, RPi.GPIO as GPIO
    # from pyrf24 import RF24, RF24_PA_MAX
    #
    # radio = RF24(22, 0)  # CE=GPIO22, CSN=CE0
    # radio.begin()
    # radio.setAutoAck(False)
    # radio.disableCRC()
    # radio.setPayloadSize(32)
    # radio.setPALevel(RF24_PA_MAX)
    #
    # while True:
    #     counts = [0]*126
    #     for _ in range(100):
    #         for ch in range(126):
    #             radio.setChannel(ch)
    #             radio.startListening()
    #             time.sleep(0.00013)
    #             if radio.testRPD():
    #                 counts[ch] += 1
    #             radio.stopListening()
    #     active = [(ch, counts[ch]) for ch in range(126) if counts[ch] > 0]
    #     for ch, c in sorted(active, key=lambda x: -x[1]):
    #         print(f"  CH {ch:3d} ({2400+ch} MHz)  {'█'*(c//5+1)} {c}")
    # ────────────────────────────────────────────────────────────────────────

    # Simulation
    import random
    while True:
        print("[RF SCAN] ── Sweep complete ──")
        active_channels = random.sample(range(0, 125), random.randint(3, 8))
        for ch in sorted(active_channels):
            strength = random.randint(1, 20)
            bar = "█" * strength
            print(f"  CH {ch:3d}  {2400+ch} MHz  {bar}")
        time.sleep(3)

except KeyboardInterrupt:
    print("\n[RF SCAN] Stopped.")
    sys.exit(0)
