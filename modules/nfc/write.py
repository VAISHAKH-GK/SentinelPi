# modules/nfc/write.py
# Write data to NFC tags using PN532 over I2C.
# Supports:
#   NDEF text record → NTAG213/215/216, MIFARE Ultralight
#   NDEF URI record  → same tags
#   Raw block write  → MIFARE Classic (with auth)

import time


def _init_pn532(log):
    try:
        import board, busio
        from adafruit_pn532.i2c import PN532_I2C
        i2c   = busio.I2C(board.SCL, board.SDA)
        pn532 = PN532_I2C(i2c, debug=False)
        pn532.SAM_configuration()
        ic, ver, rev, _ = pn532.firmware_version
        log(f"[*] PN532 ready — firmware v{ver}.{rev}")
        return pn532
    except ImportError:
        log("[ERROR] Run: pip install adafruit-circuitpython-pn532 adafruit-blinka")
        return None
    except Exception as e:
        log(f"[ERROR] PN532 init: {e}")
        return None


def _make_ndef_text(text, lang="en"):
    """Build a minimal NDEF text record payload."""
    lang_bytes    = lang.encode("ascii")
    text_bytes    = text.encode("utf-8")
    payload       = bytes([len(lang_bytes)]) + lang_bytes + text_bytes
    record_header = bytes([
        0xD1,            # MB=1 ME=1 SR=1 TNF=0x01 (Well-known)
        0x01,            # Type length = 1
        len(payload),    # Payload length
        0x54,            # Type = "T" (text)
    ])
    ndef_msg = record_header + payload
    # TLV wrapper: 0x03 = NDEF, length, data, 0xFE = terminator
    return bytes([0x03, len(ndef_msg)]) + ndef_msg + bytes([0xFE])


def _make_ndef_uri(uri):
    """Build a minimal NDEF URI record payload."""
    # URI prefix codes
    prefixes = {
        "http://www.": 0x01, "https://www.": 0x02,
        "http://": 0x03,     "https://": 0x04,
    }
    prefix_code = 0x00
    uri_str     = uri
    for prefix, code in prefixes.items():
        if uri.startswith(prefix):
            prefix_code = code
            uri_str     = uri[len(prefix):]
            break

    payload       = bytes([prefix_code]) + uri_str.encode("utf-8")
    record_header = bytes([
        0xD1, 0x01, len(payload), 0x55  # Type = "U" (URI)
    ])
    ndef_msg = record_header + payload
    return bytes([0x03, len(ndef_msg)]) + ndef_msg + bytes([0xFE])


def run(log=print, data="Hello SentinelPi", fmt="TEXT", timeout=15):
    """
    fmt:  'TEXT' = NDEF text record
          'URI'  = NDEF URI record (data should be a URL)
          'RAW'  = raw hex bytes to write to block 4 onwards
    """
    pn532 = _init_pn532(log)
    if not pn532:
        return

    log(f"[*] Format : {fmt}")
    log(f"[*] Data   : {data}")
    log("[*] Place tag on reader...")

    start = time.time()
    uid   = None
    while not uid:
        if timeout > 0 and (time.time() - start) > timeout:
            log("[!] Timeout — no tag found.")
            return
        uid = pn532.read_passive_target(timeout=0.5)

    uid_hex = ":".join(f"{b:02X}" for b in uid)
    log(f"[+] Tag detected: {uid_hex}")

    # Build payload
    try:
        if fmt == "URI":
            payload = _make_ndef_uri(data)
        elif fmt == "RAW":
            payload = bytes.fromhex(data.replace(" ", ""))
        else:
            payload = _make_ndef_text(data)
    except Exception as e:
        log(f"[ERROR] Failed to build payload: {e}")
        return

    log(f"[*] Payload: {payload.hex().upper()} ({len(payload)} bytes)")

    # Pad to 4-byte blocks
    while len(payload) % 4:
        payload += b"\x00"

    # Write starting at page 4 (first user page on NTAG/Ultralight)
    # Each page = 4 bytes on Ultralight/NTAG
    pages_needed = len(payload) // 4
    log(f"[*] Writing {pages_needed} pages...")

    try:
        for i in range(pages_needed):
            page   = 4 + i
            chunk  = payload[i*4:(i+1)*4]
            pn532.ntag2xx_write_block(page, chunk)
            log(f"  Page {page}: {chunk.hex().upper()} ✓")
        log(f"[+] Write complete — {len(payload)} bytes written.")
    except Exception as e:
        log(f"[ERROR] Write failed at page {4+i}: {e}")
        log("[!] Make sure tag is NTAG213/215/216 or MIFARE Ultralight.")
        log("[!] MIFARE Classic needs block write — use RAW mode.")
