#!/usr/bin/env python
"""ND104 backlight: breathe red when idle, rainbow key-reactive while typing.

The firmware has no effect that does both, so this script watches the time
since the last keypress on this Mac and switches the per-key backlight between
two built-in effects over USB (VIA custom_set_value on the rgb_matrix channel):

  idle    effect 5  (breathing), red, speed chosen for a ~3 s period
  typing  effect 34 (dark board, pressed key lights and fades), with the base
          hue swept around the color wheel so successive keys differ in color

It never sends the VIA save command and never touches the underglow.
It only works while this script runs and the keyboard's vendor HID interface
is reachable. "Typing" means a keypress on any keyboard on this Mac.

Run:   .conda/bin/python tools/idle_breathe.py        (Ctrl-C to stop)
Tests: .conda/bin/python tools/test_idle_breathe.py
Needs: hidapi (pip package `hidapi`). macOS only.
"""
import signal
import sys
import time

VID, PID = 0x6D67, 0x016C          # Chilkey's nd104_via_v3_1.json
USAGE_PAGE, USAGE = 0xFF60, 0x61   # docs/community.md, "HID protocol"
FRAME_LEN = 32                     # keyboard report size, same source

VIA_SET = 0x07                     # VIA custom_set_value
CH_BACKLIGHT = 3                   # VIA channel for rgb_matrix (per-key backlight)
ID_EFFECT, ID_SPEED, ID_COLOR = 2, 3, 4

# Effect numbers follow QMK's full native rgb_matrix list. Found on this
# keyboard 2026-11-24: the firmware accepts 0-50, and 32/34/35/43 behaved as
# that list predicts (see docs/this-machine.md).
EFFECT_BREATHING = 5
EFFECT_REACTIVE = 34

RED_HUE = 0                        # QMK hue scale, 0-255 around the wheel
BREATHE_PERIOD_S = 3.0             # requested: "like a 3 second period breathing"
TYPING_SPEED = 127                 # the speed the keyboard was at when effect 34 was approved
IDLE_AFTER_S = 5.0                 # proposed to and accepted by the user, 2026-11-24
RAINBOW_PERIOD_S = 4.0             # one trip round the wheel; at ~5 keys/s that is ~20 keys per
                                   # rainbow, so neighbors in a word differ visibly. Tune by eye.
HUE_ACTIVE_S = 1.0                 # only sweep the hue this long after a keypress: a pressed key
                                   # fades in ~0.5 s at speed 127, so later writes would be unseen
HUE_UPDATE_S = 0.1                 # hue write interval while keys are lit: 256/40 = 6-hue steps
POLL_S = 0.05                      # how often to check for a keypress; bounds the wake-up lag
RECONNECT_S = 2.0                  # retry interval when the keyboard is absent
READ_TIMEOUT_MS = 100              # replies arrive in ~4 ms (measured 2026-11-24)


def set_frame(channel, value_id, *data):
    p = bytearray(FRAME_LEN)
    p[0], p[1], p[2] = VIA_SET, channel, value_id
    p[3:3 + len(data)] = bytes(data)
    return bytes(p)


def breathe_period_s(speed):
    """QMK's breathing effect: brightness = |sin8(t_ms * (speed // 8) / 256) - 128| * 2,
    which repeats every 128 counts, i.e. every 32768 / (speed // 8) ms."""
    return 32.768 / (speed // 8)


def breathe_speed(period_s):
    """Speed setting whose breathing period is closest to period_s."""
    step = min(31, max(1, round(32.768 / period_s)))
    return step * 8


def mode_for(idle_s, idle_after_s):
    return "idle" if idle_s >= idle_after_s else "typing"


def rainbow_hue(t_s, period_s):
    return int(256 * (t_s % period_s) / period_s) % 256


def frames_for(mode, hue):
    if mode == "idle":
        return [set_frame(CH_BACKLIGHT, ID_COLOR, RED_HUE, 255),
                set_frame(CH_BACKLIGHT, ID_SPEED, breathe_speed(BREATHE_PERIOD_S)),
                set_frame(CH_BACKLIGHT, ID_EFFECT, EFFECT_BREATHING)]
    return [set_frame(CH_BACKLIGHT, ID_COLOR, hue, 255),
            set_frame(CH_BACKLIGHT, ID_SPEED, TYPING_SPEED),
            set_frame(CH_BACKLIGHT, ID_EFFECT, EFFECT_REACTIVE)]


def seconds_since_keypress():
    """Seconds since the last key-down on this Mac. Needs no special permission."""
    global _cg
    if _cg is None:
        import ctypes
        import ctypes.util
        _cg = ctypes.CDLL(ctypes.util.find_library("ApplicationServices"))
        _cg.CGEventSourceSecondsSinceLastEventType.restype = ctypes.c_double
        _cg.CGEventSourceSecondsSinceLastEventType.argtypes = [ctypes.c_int32, ctypes.c_uint32]
    return _cg.CGEventSourceSecondsSinceLastEventType(0, 10)   # combined session state, keyDown


_cg = None


def open_keyboard():
    import hid
    paths = [d["path"] for d in hid.enumerate(VID, PID)
             if d["usage_page"] == USAGE_PAGE and d["usage"] == USAGE]
    if not paths:
        return None
    dev = hid.device()
    dev.open_path(paths[0])
    return dev


def send(dev, frame):
    if dev.write(b"\x00" + frame) < 0:
        raise OSError("HID write failed")
    dev.read(FRAME_LEN, READ_TIMEOUT_MS)   # drain the echo


def main():
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
    # hidapi opens the interface exclusively on macOS (seen 2026-11-24: a second
    # open fails), so the device is held only while there is something to send.
    # Otherwise tools/set_time.py could not run alongside this script.
    dev, mode, last_hue_write, reachable = None, None, 0.0, None

    def close():
        nonlocal dev
        if dev is not None:
            try:
                dev.close()
            except (OSError, ValueError):
                pass
            dev = None

    try:
        while True:
            now = time.monotonic()
            idle_s = seconds_since_keypress()
            want = mode_for(idle_s, IDLE_AFTER_S)
            hue = rainbow_hue(now, RAINBOW_PERIOD_S)
            sweeping = mode == "typing" and idle_s < HUE_ACTIVE_S
            if want != mode:
                frames = frames_for(want, hue)
            elif sweeping and now - last_hue_write >= HUE_UPDATE_S:
                frames = [set_frame(CH_BACKLIGHT, ID_COLOR, hue, 255)]
            else:
                frames = []
            if frames:
                try:
                    if dev is None:
                        dev = open_keyboard()
                    if dev is None:
                        raise OSError("vendor interface not found")
                    for f in frames:
                        send(dev, f)
                except (OSError, ValueError) as e:
                    close()
                    if reachable is not False:
                        print(time.strftime("%H:%M:%S"), "keyboard unreachable:", e, flush=True)
                    reachable, mode = False, None
                    time.sleep(RECONNECT_S)
                    continue
                reachable, last_hue_write = True, now
                if want != mode:
                    mode = want
                    print(time.strftime("%H:%M:%S"), mode, flush=True)
            elif not sweeping:
                close()
            time.sleep(POLL_S)
    except KeyboardInterrupt:
        pass
    finally:
        try:   # leave the board in the typing effect, not mid-breath
            if dev is None:
                dev = open_keyboard()
            if dev is not None:
                for f in frames_for("typing", rainbow_hue(time.monotonic(), RAINBOW_PERIOD_S)):
                    send(dev, f)
        except (OSError, ValueError):
            pass
        close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
