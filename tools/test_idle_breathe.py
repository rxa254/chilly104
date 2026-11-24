#!/usr/bin/env python
"""Tests for idle_breathe.py's pure logic (no keyboard needed).

Run:  .conda/bin/python tools/test_idle_breathe.py
"""
import idle_breathe as ib


def test_frame():
    f = ib.set_frame(3, 4, 213, 255)
    assert len(f) == 32
    assert f[:5] == bytes([0x07, 3, 4, 213, 255]) and not any(f[5:])


def test_breathe_speed_hits_three_seconds():
    s = ib.breathe_speed(3.0)
    assert s == 88, s
    assert abs(ib.breathe_period_s(s) - 3.0) < 0.05
    # known points of the QMK formula: period = 32768 ms / (speed // 8)
    assert abs(ib.breathe_period_s(127) - 32.768 / 15) < 1e-9
    assert 8 <= ib.breathe_speed(1000) and ib.breathe_speed(0.01) <= 255


def test_mode():
    assert ib.mode_for(0.0, 5.0) == "typing"
    assert ib.mode_for(4.99, 5.0) == "typing"
    assert ib.mode_for(5.0, 5.0) == "idle"
    assert ib.mode_for(3600.0, 5.0) == "idle"


def test_rainbow_hue():
    assert ib.rainbow_hue(0.0, 4.0) == 0
    assert ib.rainbow_hue(1.0, 4.0) == 64
    assert ib.rainbow_hue(2.0, 4.0) == 128
    assert ib.rainbow_hue(4.0, 4.0) == 0            # wraps
    assert all(0 <= ib.rainbow_hue(t / 7, 4.0) <= 255 for t in range(200))


def test_mode_frames():
    idle = ib.frames_for("idle", 99)
    assert ib.set_frame(3, 2, ib.EFFECT_BREATHING) in idle
    assert ib.set_frame(3, 4, ib.RED_HUE, 255) in idle       # idle ignores the rainbow hue
    assert ib.set_frame(3, 3, ib.breathe_speed(ib.BREATHE_PERIOD_S)) in idle
    typing = ib.frames_for("typing", 99)
    assert ib.set_frame(3, 2, ib.EFFECT_REACTIVE) in typing
    assert ib.set_frame(3, 4, 99, 255) in typing
    assert ib.set_frame(3, 3, ib.TYPING_SPEED) in typing
    # nothing touches the underglow channel or sends a save
    assert all(f[0] == 0x07 and f[1] == 3 for f in idle + typing)


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
