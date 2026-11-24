#!/usr/bin/env python
"""Set the ND104 LCD clock to this Mac's local time, over USB.

Protocol from MrUrdam/chilkey_nd104_utilities (docs/protocol.md, and
nd104-protocol/src/{frame,time,checksum}.rs): a 32-byte `1C` frame sent to the
keyboard's vendor HID interface (usage page 0xFF60, usage 0x61), which forwards
it to the screen.

Run:  .conda/bin/python tools/set_time.py [--dry-run]
Needs: hidapi (pip package `hidapi`).
"""
import datetime
import sys

VID, PID = 0x6D67, 0x016C          # Chilkey's nd104_via_v3_1.json
USAGE_PAGE, USAGE = 0xFF60, 0x61   # protocol.md section 1
FRAME_LEN = 32                     # keyboard report size (protocol.md section 1)
READ_TIMEOUT_MS = 1000             # per read; the keyboard answers within a few ms
MAX_REPLIES = 6                    # ack + wrapped screen answer, plus slack for
                                   # the unsolicited reports protocol.md describes


def crc16(data):
    """CRC-16/CCITT-FALSE."""
    crc = 0xFFFF
    for b in data:
        crc ^= b << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021 if crc & 0x8000 else crc << 1) & 0xFFFF
    return crc


def with_crc(p):
    p = bytearray(p)
    p[6] = p[7] = 0
    c = crc16(p)
    p[6], p[7] = c & 0xFF, c >> 8
    return bytes(p)


def time_packet(t):
    payload = bytes([0x00, 0x01, t.year >> 8, t.year & 0xFF, t.month, t.day,
                     t.hour, t.minute, t.second, (t.weekday() + 1) % 7])  # 0 = Sunday
    p = bytearray(FRAME_LEN)
    p[0], p[1] = 0x1C, 0x03
    p[5] = len(payload) + 5
    p[8], p[9], p[11] = 0xA5, 0x38, len(payload)
    p[12:12 + len(payload)] = payload
    p[12 + len(payload)] = (sum(p[9:]) & 0xFF) ^ 0xFF
    return with_crc(p)


def version_query():
    p = bytearray(FRAME_LEN)
    p[0], p[1] = 0x11, 0x02
    return with_crc(p)


def self_test():
    """Check against the reference vectors in the upstream source."""
    assert crc16(b"123456789") == 0x29B1
    assert version_query()[6:8] == bytes([0xBC, 0x60])
    p = time_packet(datetime.datetime(2026, 10, 31, 14, 5, 9))  # a Saturday
    assert p[:6] == bytes([0x1C, 0x03, 0, 0, 0, 0x0F])
    assert p[8:22] == bytes([0xA5, 0x38, 0, 0x0A, 0, 1, 0x07, 0xEA, 10, 31, 14, 5, 9, 6])
    assert p[22] == (sum(p[9:22]) & 0xFF) ^ 0xFF and not any(p[23:])


def main():
    self_test()
    dry = "--dry-run" in sys.argv
    if dry:
        print("packet:", time_packet(datetime.datetime.now()).hex(" "))
        return 0

    import hid
    paths = [d["path"] for d in hid.enumerate(VID, PID)
             if d["usage_page"] == USAGE_PAGE and d["usage"] == USAGE]
    if not paths:
        print("ND104 vendor interface not found (is it on USB, in USB mode?)")
        return 1
    dev = hid.device()
    dev.open_path(paths[0])
    try:
        dev.write(b"\x00" + version_query())
        r = bytes(dev.read(FRAME_LEN, READ_TIMEOUT_MS))
        if r[:2] == b"\x11\x02":
            print("keyboard firmware:", r[8:8 + r[5]].decode("ascii", "replace"))
        else:
            print("unexpected version reply:", r.hex(" "))

        now = datetime.datetime.now()
        pkt = time_packet(now)
        dev.write(b"\x00" + pkt)
        print("sent", now.strftime("%Y-%m-%d %H:%M:%S %a"), "|", pkt.hex(" "))
        ok = False
        for _ in range(MAX_REPLIES):
            r = bytes(dev.read(FRAME_LEN, READ_TIMEOUT_MS))
            if not r:
                break
            print("reply:", r.hex(" "))
            if r[0] == 0x1C and r[8:10] == b"\xA5\x38":
                ok = r[12] == 0xFE
                break
        print("screen acknowledged: OK" if ok else "NO OK acknowledgement from screen")
        return 0 if ok else 2
    finally:
        dev.close()


if __name__ == "__main__":
    sys.exit(main())
