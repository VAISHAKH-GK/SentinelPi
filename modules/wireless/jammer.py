# modules/wireless/jammer.py
# 2.4GHz jammer using nRF24L01+PA+LNA directly on Raspberry Pi via SPI.
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

_running = False

def stop():
    global _running
    _running = False


# PA level options passed in from the UI
PA_LEVELS = {
    "MIN":  0,   # RF24_PA_MIN  — same desk testing, lowest power
    "LOW":  1,   # RF24_PA_LOW  — same room testing
    "HIGH": 2,   # RF24_PA_HIGH — through walls
    "MAX":  3,   # RF24_PA_MAX  — outdoor / long range, needs good power supply
}


def run(log=print, mode="full", pa_level="LOW"):
    """
    mode:     'full' = sweep all 2.4GHz channels (0-79)
              'ble'  = BLE advertising channels only (37, 38, 39)
              'wifi' = common WiFi channels (1, 6, 11)

    pa_level: 'MIN' / 'LOW' / 'HIGH' / 'MAX'
              Use LOW for bench testing — more than enough at close range.
              Only use MAX outdoors with a proper power supply.
    """
    global _running

    try:
        from pyrf24 import RF24, RF24_2MBPS, RF24_CRC_DISABLED
        from pyrf24 import RF24_PA_MIN, RF24_PA_LOW, RF24_PA_HIGH, RF24_PA_MAX
    except ImportError:
        log("[ERROR] pyrf24 not installed. Run: pip install pyrf24")
        return

    # Map string → actual constant
    pa_map = {
        "MIN":  RF24_PA_MIN,
        "LOW":  RF24_PA_LOW,
        "HIGH": RF24_PA_HIGH,
        "MAX":  RF24_PA_MAX,
    }
    pa = pa_map.get(pa_level.upper(), RF24_PA_LOW)

    CE_PIN  = 22
    CSN_PIN = 0

    radio = RF24(CE_PIN, CSN_PIN)

    log("[*] Initialising radio...")
    if not radio.begin():
        log("[ERROR] nRF24L01 not detected. Check wiring and capacitors.")
        return

    log(f"[*] Radio initialised. PA level: {pa_level}")

    radio.setAutoAck(False)
    radio.stopListening()
    radio.setRetries(0, 0)
    radio.setPayloadSize(5)
    radio.setAddressWidth(3)
    radio.setPALevel(pa, True)
    radio.setDataRate(RF24_2MBPS)
    radio.setCRCLength(RF24_CRC_DISABLED)

    if mode == "ble":
        channels = [37, 38, 39]
        log("[*] Mode: BLE advertising channels (37, 38, 39)")
    elif mode == "wifi":
        channels = [1, 6, 11]
        log("[*] Mode: WiFi channels (1, 6, 11)")
    else:
        channels = list(range(0, 80))
        log("[*] Mode: Full sweep (channels 0-79)")

    log(f"[*] Starting constant carrier on channel {channels[0]}...")
    radio.startConstCarrier(pa, channels[0])

    _running = True
    log("[*] Jamming active. Press STOP to end.")

    sweep_count = 0
    try:
        while _running:
            for ch in channels:
                if not _running:
                    break
                radio.setChannel(ch)
                time.sleep(0.001)

            sweep_count += 1
            if sweep_count % 100 == 0:
                log(f"[~] Sweeping... ({sweep_count} passes)")
    finally:
        radio.stopConstCarrier()
        radio.powerDown()
        log("[*] Jammer stopped. Radio powered down.")
