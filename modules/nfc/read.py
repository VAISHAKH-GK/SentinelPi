# modules/nfc/read.py
# Read NFC/RFID tags using PN532 over I2C.
# Supports: MIFARE Classic, MIFARE Ultralight, NTAG, ISO14443A
#
# Wiring:
#   VCC → 3.3V (Pin 1)
#   GND → GND  (Pin 6)
#   SDA → GPIO2 (Pin 3)
#   SCL → GPIO3 (Pin 5)
#   PN532 switches: SEL0=ON, SEL1=OFF  (I2C mode)
#
# pip install adafruit-circuitpython-pn532 adafruit-blinka

import time

_running = False

def stop():
    global _running
    _running = False


def _init_pn532(log):
    """Initialise PN532 over I2C. Returns pn532 object or None."""
    try:
        import board
        import busio
        from adafruit_pn532.i2c import PN532_I2C
    except ImportError:
        log("[ERROR] Library missing. Run: pip install adafruit-circuitpython-pn532 adafruit-blinka")
        return None

    try:
        i2c = busio.I2C(board.SCL, board.SDA)
        pn532 = PN532_I2C(i2c, debug=False)
        pn532.SAM_configuration()
        ic, ver, rev, support = pn532.firmware_version
        log(f"[*] PN532 ready — firmware v{ver}.{rev}")
        return pn532
    except Exception as e:
        log(f"[ERROR] PN532 init failed: {e}")
        log("[!] Check wiring and I2C is enabled (raspi-config)")
        return None


def _uid_to_hex(uid):
    return ":".join(f"{b:02X}" for b in uid)


def _detect_tag_type(uid_len):
    if uid_len == 4:  return "MIFARE Classic / MIFARE Ultralight"
    if uid_len == 7:  return "MIFARE Ultralight / NTAG"
    if uid_len == 10: return "MIFARE DESFire"
    return "Unknown"


def run(log=print, timeout=15):
    """
    Wait for a tag and read its UID + basic info.
    timeout: seconds to wait (0 = wait forever)
    """
    global _running

    pn532 = _init_pn532(log)
    if not pn532:
        return

    log(f"[*] Waiting for tag... (timeout: {timeout}s)" if timeout else "[*] Waiting for tag...")

    _running   = True
    start_time = time.time()

    try:
        while _running:
            if timeout > 0 and (time.time() - start_time) > timeout:
                log("[!] Timeout — no tag detected.")
                return

            uid = pn532.read_passive_target(timeout=0.5)

            if uid:
                uid_hex  = _uid_to_hex(uid)
                tag_type = _detect_tag_type(len(uid))
                log(f"[+] Tag detected!")
                log(f"    UID      : {uid_hex}")
                log(f"    UID len  : {len(uid)} bytes")
                log(f"    Type     : {tag_type}")
                log(f"    Raw      : {list(uid)}")
                return uid

    except Exception as e:
        log(f"[ERROR] {e}")
    finally:
        log("[*] Read complete.")
