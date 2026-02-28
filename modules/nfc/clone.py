# modules/nfc/clone.py
# Clone a MIFARE Classic 1K tag to a blank writable card.
# Reads all 16 sectors from source, writes to destination.
#
# Requirements:
#   - Source: any MIFARE Classic 1K tag
#   - Destination: blank MIFARE Classic 1K (UID writable "magic" card
#                  also called "Chinese clone card" or "Gen1a" card)
#
# MIFARE Classic 1K layout:
#   16 sectors × 4 blocks × 16 bytes = 1024 bytes total
#   Block 0  = manufacturer data (UID, read-only on real cards)
#   Block 3,7,11... = sector trailers (keys A+B + access bits)

import time

# Default MIFARE Classic key A (factory default)
DEFAULT_KEY = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]

_source_data = None   # stores read data between capture and write steps


def _init_pn532(log):
    try:
        import board, busio
        from adafruit_pn532.i2c import PN532_I2C
        i2c   = busio.I2C(board.SCL, board.SDA)
        pn532 = PN532_I2C(i2c, debug=False)
        pn532.SAM_configuration()
        ic, ver, rev, support = pn532.firmware_version
        log(f"[*] PN532 ready — firmware v{ver}.{rev}")
        return pn532
    except ImportError:
        log("[ERROR] Run: pip install adafruit-circuitpython-pn532 adafruit-blinka")
        return None
    except Exception as e:
        log(f"[ERROR] PN532 init failed: {e}")
        return None


def read_source(log=print, timeout=15):
    """
    Step 1: Read all blocks from source MIFARE Classic 1K tag.
    Stores data in module-level _source_data for use by write_clone().
    """
    global _source_data

    pn532 = _init_pn532(log)
    if not pn532:
        return False

    log("[*] Place SOURCE tag on reader...")
    start = time.time()

    uid = None
    while not uid:
        if timeout > 0 and (time.time() - start) > timeout:
            log("[!] Timeout — no tag found.")
            return False
        uid = pn532.read_passive_target(timeout=0.5)

    uid_hex = ":".join(f"{b:02X}" for b in uid)
    log(f"[+] Source tag: {uid_hex}")
    log(f"[*] Reading 16 sectors (64 blocks)...")

    blocks = {}
    failed = []

    for sector in range(16):
        block_num = sector * 4
        # Authenticate sector with default key A
        try:
            auth = pn532.mifare_classic_authenticate_block(
                uid, block_num, 0x60, DEFAULT_KEY  # 0x60 = key A
            )
            if not auth:
                log(f"  Sector {sector:2d}: Auth FAILED (non-default key)")
                failed.append(sector)
                continue
        except Exception as e:
            log(f"  Sector {sector:2d}: Auth error — {e}")
            failed.append(sector)
            continue

        # Read 4 blocks in this sector
        sector_blocks = []
        for b in range(4):
            try:
                data = pn532.mifare_classic_read_block(block_num + b)
                sector_blocks.append(list(data) if data else [0]*16)
                hex_str = " ".join(f"{x:02X}" for x in (data or []))
                log(f"  Sector {sector:2d} Block {block_num+b}: {hex_str}")
            except Exception as e:
                log(f"  Sector {sector:2d} Block {block_num+b}: Read error — {e}")
                sector_blocks.append([0] * 16)

        blocks[sector] = sector_blocks

    if failed:
        log(f"[!] {len(failed)} sectors failed (encrypted): {failed}")
        log("[!] Clone will be partial — failed sectors will use zeroes.")

    _source_data = {"uid": list(uid), "uid_hex": uid_hex, "blocks": blocks}
    log(f"[+] Read complete — {len(blocks)} sectors captured.")
    return True


def write_clone(log=print, timeout=15):
    """
    Step 2: Write captured data to a blank magic/writable card.
    Must call read_source() first.
    """
    global _source_data

    if not _source_data:
        log("[!] No source data. Run READ SOURCE first.")
        return False

    pn532 = _init_pn532(log)
    if not pn532:
        return False

    log("[*] Remove source tag. Place BLANK writable card on reader...")
    # Brief pause so user can swap cards
    time.sleep(2)

    start = time.time()
    uid   = None
    while not uid:
        if timeout > 0 and (time.time() - start) > timeout:
            log("[!] Timeout — no card found.")
            return False
        uid = pn532.read_passive_target(timeout=0.5)

    uid_hex = ":".join(f"{b:02X}" for b in uid)
    log(f"[+] Blank card detected: {uid_hex}")
    log(f"[*] Writing {len(_source_data['blocks'])} sectors...")

    success = 0
    failed  = []

    for sector, sector_blocks in _source_data["blocks"].items():
        block_num = sector * 4
        try:
            auth = pn532.mifare_classic_authenticate_block(
                uid, block_num, 0x60, DEFAULT_KEY
            )
            if not auth:
                log(f"  Sector {sector:2d}: Auth FAILED")
                failed.append(sector)
                continue
        except Exception as e:
            log(f"  Sector {sector:2d}: Auth error — {e}")
            failed.append(sector)
            continue

        for b in range(4):
            # Skip sector trailer (last block) — it contains keys
            # Writing wrong access bits can permanently lock the card
            if b == 3:
                continue
            # Skip block 0 on magic cards — handle separately
            if sector == 0 and b == 0:
                continue
            try:
                data = bytes(sector_blocks[b])
                pn532.mifare_classic_write_block(block_num + b, data)
                hex_str = " ".join(f"{x:02X}" for x in data)
                log(f"  Sector {sector:2d} Block {block_num+b}: {hex_str} ✓")
                success += 1
            except Exception as e:
                log(f"  Sector {sector:2d} Block {block_num+b}: Write error — {e}")
                failed.append(f"{sector}:{b}")

    log("")
    log(f"[+] Clone complete — {success} blocks written.")
    if failed:
        log(f"[!] Failed: {failed}")
    log(f"[*] Source UID was: {_source_data['uid_hex']}")
    log(f"[*] Clone card UID: {uid_hex}")
    if _source_data['uid_hex'] != uid_hex:
        log("[!] UIDs differ — full emulation may not work.")
        log("[!] Use a Gen1a/Gen2 magic card to clone the UID too.")
    return True


def run(log=print, mode="read", timeout=15):
    """Called by UI worker. mode = 'read' or 'write'"""
    if mode == "read":
        read_source(log=log, timeout=timeout)
    else:
        write_clone(log=log, timeout=timeout)
