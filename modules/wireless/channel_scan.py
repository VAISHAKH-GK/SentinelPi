# modules/wireless/channel_scan.py
# Scans all 126 nRF24L01 channels and reports signal strength.
# Uses carrier detection (testRPD) — detects any 2.4GHz energy on each channel.
#
# Covers:
#   WiFi ch 1  → nRF ch 5
#   WiFi ch 6  → nRF ch 30
#   WiFi ch 11 → nRF ch 55
#   BLE adv    → nRF ch 37, 38, 39
#   Full 2.4G  → nRF ch 0-125

import time

_running = False

def stop():
    global _running
    _running = False

def run(log=print, passes=3):
    """
    passes: how many times to sample each channel before reporting.
            More passes = more accurate but slower scan.
    """
    global _running

    try:
        from pyrf24 import RF24, RF24_PA_LOW, RF24_2MBPS, RF24_CRC_DISABLED
    except ImportError:
        log("[ERROR] pyrf24 not installed. Run: pip install pyrf24")
        return

    CE_PIN  = 22
    CSN_PIN = 0
    radio   = RF24(CE_PIN, CSN_PIN)

    log("[*] Initialising radio...")
    if not radio.begin():
        log("[ERROR] nRF24L01 not detected. Check wiring.")
        return

    radio.setAutoAck(False)
    radio.startListening()
    radio.setPALevel(RF24_PA_LOW)
    radio.setDataRate(RF24_2MBPS)
    radio.setCRCLength(RF24_CRC_DISABLED)

    log(f"[*] Scanning 126 channels ({passes} passes each)...")
    log("-" * 50)

    _running = True
    hits = [0] * 126   # signal hit count per channel

    try:
        for p in range(passes):
            if not _running:
                break
            for ch in range(126):
                if not _running:
                    break
                radio.setChannel(ch)
                radio.startListening()
                time.sleep(0.0001)    # 128us dwell time
                if radio.testRPD():   # returns True if signal detected
                    hits[ch] += 1
                radio.stopListening()

        if not _running:
            log("[*] Scan cancelled.")
            return

        log("[*] Results (channel : signal hits / passes):")
        log("")

        active = []
        for ch in range(126):
            if hits[ch] > 0:
                bar     = "█" * hits[ch] + "░" * (passes - hits[ch])
                freq_mhz = 2400 + ch
                # Tag known channels
                tag = ""
                if ch in [37, 38, 39]:   tag = " ← BLE advertising"
                elif ch == 5:            tag = " ← WiFi ch 1"
                elif ch == 30:           tag = " ← WiFi ch 6"
                elif ch == 55:           tag = " ← WiFi ch 11"
                elif ch == 80:           tag = " ← WiFi ch 16"
                log(f"  CH {ch:3d} ({freq_mhz} MHz) [{bar}]{tag}")
                active.append(ch)

        log("")
        if active:
            log(f"[*] Active channels: {active}")
        else:
            log("[*] No signal detected on any channel.")

    finally:
        radio.stopListening()
        radio.powerDown()
        log("[*] Scan complete.")
