# modules/wireless/replay.py
# Capture a packet then replay it on demand.
# Works against unencrypted devices: garage doors, RC toys,
# wireless doorbells, cheap remote controls, etc.
#
# Two modes:
#   capture() — listen and save the first packet received
#   replay()  — retransmit the saved packet N times

import time
import os
import json
from datetime import datetime

_running    = False
_captured   = None     # stores last captured packet as dict

CAPTURE_DIR = os.path.expanduser("~/SentinelPi/captures")
os.makedirs(CAPTURE_DIR, exist_ok=True)


def stop():
    global _running
    _running = False


def capture(log=print, channel=76, address="E7E7E7E7E7", timeout=15):
    """
    Listen for the first packet and store it.
    timeout: seconds to wait before giving up (0 = wait forever)
    """
    global _running, _captured

    try:
        from pyrf24 import RF24, RF24_PA_LOW, RF24_1MBPS
    except ImportError:
        log("[ERROR] pyrf24 not installed.")
        return

    CE_PIN  = 22
    CSN_PIN = 0
    radio   = RF24(CE_PIN, CSN_PIN)

    if not radio.begin():
        log("[ERROR] nRF24L01 not detected.")
        return

    try:
        addr_bytes = bytes.fromhex(address)
    except ValueError:
        log(f"[ERROR] Invalid address: {address}")
        return

    radio.setChannel(channel)
    radio.setPayloadSize(32)
    radio.setAddressWidth(len(addr_bytes))
    radio.openReadingPipe(1, addr_bytes)
    radio.setAutoAck(False)
    radio.setPALevel(RF24_PA_LOW)
    radio.setDataRate(RF24_1MBPS)
    radio.startListening()

    freq = 2400 + channel
    log(f"[*] Listening on channel {channel} ({freq} MHz)")
    log(f"[*] Address: {address}")
    log(f"[*] Waiting for packet... (timeout: {timeout}s)" if timeout else "[*] Waiting for packet...")

    _running    = True
    start_time  = time.time()

    try:
        while _running:
            if timeout > 0 and (time.time() - start_time) > timeout:
                log("[!] Timeout — no packet received.")
                return

            if radio.available():
                payload   = radio.read(32)
                hex_data  = " ".join(f"{b:02X}" for b in payload)
                ts        = datetime.now().strftime("%H:%M:%S")

                _captured = {
                    "channel": channel,
                    "address": address,
                    "payload": list(payload),
                    "hex":     hex_data,
                    "captured_at": ts,
                }

                log(f"[+] Packet captured at {ts}!")
                log(f"    Channel : {channel} ({freq} MHz)")
                log(f"    Address : {address}")
                log(f"    Data    : {hex_data}")

                # Auto-save
                fname = os.path.join(CAPTURE_DIR, f"replay_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
                with open(fname, "w") as f:
                    json.dump(_captured, f, indent=2)
                log(f"[*] Saved to {fname}")
                return

            time.sleep(0.001)

    finally:
        radio.stopListening()
        radio.powerDown()


def replay(log=print, repeat=5, delay=0.5, file=None):
    """
    Retransmit the last captured packet (or load from file).
    repeat: how many times to transmit
    delay:  seconds between each transmission
    file:   path to a saved .json capture file (optional)
    """
    global _captured

    # Load from file if provided
    if file:
        try:
            with open(file) as f:
                _captured = json.load(f)
            log(f"[*] Loaded capture from {file}")
        except Exception as e:
            log(f"[ERROR] Could not load file: {e}")
            return

    if not _captured:
        log("[!] No packet captured yet. Run Capture first.")
        return

    try:
        from pyrf24 import RF24, RF24_PA_MAX, RF24_1MBPS
    except ImportError:
        log("[ERROR] pyrf24 not installed.")
        return

    channel    = _captured["channel"]
    address    = _captured["address"]
    payload    = bytes(_captured["payload"])
    hex_data   = _captured["hex"]

    CE_PIN  = 22
    CSN_PIN = 0
    radio   = RF24(CE_PIN, CSN_PIN)

    if not radio.begin():
        log("[ERROR] nRF24L01 not detected.")
        return

    addr_bytes = bytes.fromhex(address)

    radio.setChannel(channel)
    radio.setPayloadSize(32)
    radio.setAddressWidth(len(addr_bytes))
    radio.openWritingPipe(addr_bytes)
    radio.setAutoAck(False)
    radio.setRetries(0, 0)
    radio.setPALevel(RF24_PA_MAX)
    radio.setDataRate(RF24_1MBPS)
    radio.stopListening()

    freq = 2400 + channel
    log(f"[*] Replaying on channel {channel} ({freq} MHz)")
    log(f"[*] Address : {address}")
    log(f"[*] Payload : {hex_data}")
    log(f"[*] Sending {repeat}x with {delay}s delay...")

    success = 0
    for i in range(repeat):
        ok = radio.write(payload)
        if ok:
            success += 1
            log(f"  [{i+1}/{repeat}] Sent OK")
        else:
            log(f"  [{i+1}/{repeat}] Send failed")
        if i < repeat - 1:
            time.sleep(delay)

    radio.powerDown()
    log(f"[*] Replay complete — {success}/{repeat} successful.")


# ── run() is called by the UI ────────────────────────────────────────────────
# The UI has two buttons: Capture and Replay, each calling capture()/replay().
# This run() is kept for compatibility with the worker thread.

def run(log=print, mode="capture", channel=76, address="E7E7E7E7E7",
        repeat=5, delay=0.5, file=None, timeout=15):
    if mode == "capture":
        capture(log=log, channel=channel, address=address, timeout=timeout)
    else:
        replay(log=log, repeat=repeat, delay=delay, file=file)
