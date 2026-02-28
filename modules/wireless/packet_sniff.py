# modules/wireless/packet_sniff.py
# Sniffs raw nRF24L01 packets on a given channel.
# Works best against unencrypted nRF24 devices (cheap RC toys,
# wireless sensors, keyboards, mice, etc.)
#
# Note: nRF24L01 needs a matching address width and payload size
# to actually receive packets. The defaults here are broad but
# you may need to tune them for specific target devices.

import time
from datetime import datetime

_running = False

def stop():
    global _running
    _running = False

def run(log=print, channel=76, count=0, address="E7E7E7E7E7"):
    """
    channel: nRF24 channel to listen on (0-125)
             Common targets:
               76  = default nRF24 channel used by many cheap devices
               1   = some RC toys
               100 = some wireless mice
    count:   number of packets to capture (0 = unlimited until stopped)
    address: listening address in hex string, 3-5 bytes
             E7E7E7E7E7 = broadcast address most devices respond to
    """
    global _running

    try:
        from pyrf24 import RF24, RF24_PA_LOW, RF24_1MBPS, RF24_2MBPS
    except ImportError:
        log("[ERROR] pyrf24 not installed.")
        return

    CE_PIN  = 22
    CSN_PIN = 0
    radio   = RF24(CE_PIN, CSN_PIN)

    log("[*] Initialising radio...")
    if not radio.begin():
        log("[ERROR] nRF24L01 not detected.")
        return

    # Parse address
    try:
        addr_bytes = bytes.fromhex(address)
    except ValueError:
        log(f"[ERROR] Invalid address: {address}. Use hex like E7E7E7E7E7")
        return

    radio.setChannel(channel)
    radio.setPayloadSize(32)          # max payload — catches most devices
    radio.setAddressWidth(len(addr_bytes))
    radio.openReadingPipe(1, addr_bytes)
    radio.setAutoAck(False)
    radio.setPALevel(RF24_PA_LOW)
    radio.setDataRate(RF24_1MBPS)     # 1Mbps catches more devices than 2Mbps
    radio.startListening()

    freq = 2400 + channel
    log(f"[*] Listening on channel {channel} ({freq} MHz)")
    log(f"[*] Address: {address}  |  {'Unlimited' if count == 0 else count} packets")
    log(f"[*] Press STOP to end capture.")
    log("-" * 50)

    _running = True
    captured = 0
    start_time = time.time()

    try:
        while _running:
            if count > 0 and captured >= count:
                break

            if radio.available():
                payload = radio.read(32)
                captured += 1
                ts       = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                hex_data = " ".join(f"{b:02X}" for b in payload)
                # Try to show printable ASCII alongside hex
                ascii_data = "".join(chr(b) if 32 <= b < 127 else "." for b in payload)
                log(f"[{ts}] PKT #{captured:04d}  {hex_data}")
                log(f"           ASCII: {ascii_data}")
            else:
                time.sleep(0.001)

    finally:
        elapsed = time.time() - start_time
        radio.stopListening()
        radio.powerDown()
        log("-" * 50)
        log(f"[*] Captured {captured} packets in {elapsed:.1f}s")
        log("[*] Sniff ended.")
