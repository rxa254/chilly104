# chilly104

Notes and small macOS tools for the **[Chilkey ND104](https://chilkey.com/products/nd104-keyboard)**, a full-size (104-key) tri-mode mechanical keyboard with a knob and an LCD calculator/clock screen.

The ND104 ships with a scanned manual, a Chrome-only web driver, and closed firmware. This repo is what one owner worked out while setting it up on a Mac:

- **Set the LCD clock from the terminal**, without opening the web driver.
- **A backlight that breathes red when you stop typing** and lights each key in a moving rainbow while you type.
- **Control the lighting over USB** with plain VIA packets, including the effect numbers the firmware really uses.
- **A searchable transcription of the manual's shortcuts**, since the official PDF is images only.
- **A firmware update done from macOS with `dfu-util`**, written down step by step with what went wrong.
- **Troubleshooting notes**, including the flat-battery-after-a-weekend problem and what fixed it.

Everything here was checked on one keyboard (firmware V3.0.14, screen V1.2.4) on one Mac. Where something is taken from a review or recalled from documentation and not tested, the notes say so.

## Contents

- [Install](#install)
- [Tools](#tools)
  - [`set_time.py`: set the LCD clock](#set_timepy-set-the-lcd-clock)
  - [`idle_breathe.py`: breathe when idle, rainbow when typing](#idle_breathepy-breathe-when-idle-rainbow-when-typing)
- [Lighting over USB](#lighting-over-usb)
- [Quick setup on macOS](#quick-setup-on-macos)
- [Most useful shortcuts](#most-useful-shortcuts)
- [Documentation](#documentation)
- [What is not in this repo](#what-is-not-in-this-repo)
- [Confidence notes](#confidence-notes)
- [Credits](#credits)

## Install

The tools are single-file Python scripts. They need Python 3 and the [`hidapi`](https://pypi.org/project/hidapi/) package, and they talk to the keyboard over **USB** (press `Fn + Space` for USB mode).

```sh
git clone https://github.com/rxa254/chilly104.git
cd chilly104
python3 -m venv .venv
.venv/bin/pip install hidapi
```

The examples below use `.venv/bin/python`. On the author's machine the environment is a conda prefix at `.conda/` instead; any Python with `hidapi` works. On macOS the keyboard's vendor HID interface opens without any special permission.

## Tools

### `set_time.py`: set the LCD clock

The keyboard never syncs its clock by itself, and it forgets the time when the battery runs flat. This pushes the Mac's local time to the screen.

```sh
.venv/bin/python tools/set_time.py            # set the clock
.venv/bin/python tools/set_time.py --dry-run  # print the packet, send nothing
```

It prints the keyboard's firmware version and the screen's acknowledgement, and exits non-zero if the screen does not confirm. The packet format comes from [MrUrdam's protocol notes](https://github.com/MrUrdam/chilkey_nd104_utilities); the script checks itself against that project's reference vectors on every run.

### `idle_breathe.py`: breathe when idle, rainbow when typing

The firmware has reactive effects and a breathing effect, but nothing that combines them. This script watches the time since your last keypress and switches the per-key backlight between two built-in effects:

| State | What the backlight does |
|---|---|
| Idle (5 s without a keypress) | Breathes red, with a period of about 3 s |
| Typing | Board is dark; each pressed key lights and fades, and the color sweeps around the wheel every 4 s so successive keys differ |

```sh
.venv/bin/python tools/idle_breathe.py        # Ctrl-C to stop
.venv/bin/python tools/test_idle_breathe.py   # logic tests, no keyboard needed
```

The behavior is set by named constants at the top of the file:

| Constant | Default | Meaning |
|---|---|---|
| `IDLE_AFTER_S` | 5.0 | Seconds without a keypress before breathing starts |
| `BREATHE_PERIOD_S` | 3.0 | Breathing period; converted to an effect speed with QMK's formula |
| `RED_HUE` | 0 | Breathing color, on a 0–255 hue wheel |
| `RAINBOW_PERIOD_S` | 4.0 | Time for the typing color to go once around the wheel |
| `TYPING_SPEED` | 127 | Effect speed while typing; higher fades pressed keys faster |

Things to know before you run it:

- It works only while the script is running and the keyboard is on USB. It does not change what the keyboard does on another computer.
- It reacts to keypresses on **any** keyboard attached to the Mac, including a laptop's built-in one.
- It never sends the VIA save command, so the keyboard's stored lighting settings are untouched. It does not touch the underglow.
- While you type it sends a color update 10 times a second. Those return as fast as a read (4 ms), which suggests they are not written to flash, but that is not proven on this closed firmware.
- The 3 s breathing period is calculated, not measured with a stopwatch.

## Lighting over USB

The keyboard answers plain VIA packets on its vendor HID interface (usage page `0xFF60`, usage `0x61`, 32-byte reports). That is enough to script the lighting.

| Packet | Meaning |
|---|---|
| `08 <channel> <id>` | Read a value; the answer echoes the packet with the value from byte 3 |
| `07 <channel> <id> <value…>` | Set a value (not saved across a power cycle unless you also send a save) |

| Channel | Zone | | Id | Value |
|---|---|---|---|---|
| `02` | Underglow | | `01` | Brightness, 0–255 |
| `03` | Per-key backlight | | `02` | Effect number |
| | | | `03` | Effect speed, 0–255 |
| | | | `04` | Hue, saturation (0–255 each) |

For example, solid magenta on the backlight:

```python
import hid

dev = hid.device()
dev.open_path(next(d["path"] for d in hid.enumerate(0x6D67, 0x016C)
                   if d["usage_page"] == 0xFF60 and d["usage"] == 0x61))

def via_set(channel, value_id, *data):
    frame = bytes([0x07, channel, value_id, *data]).ljust(32, b"\x00")
    dev.write(b"\x00" + frame)
    return bytes(dev.read(32, 1000))

via_set(3, 2, 1)           # effect 1: solid color
via_set(3, 4, 213, 255)    # hue 213 (magenta), full saturation
dev.close()
```

**Backlight effect numbers.** The firmware accepts effects 0–50. They follow QMK's full native rgb_matrix effect list, **not** the shorter list in VIA's lighting menu, so the numbers VIA guides give are wrong for this board. Seen on this keyboard:

| Effect | What it does |
|---|---|
| 1 | Solid color |
| 5 | Breathing |
| 13 | The default after the V3.0.14 flash (appearance not recorded) |
| 32 | Typing heatmap; changes little with normal typing |
| 34 | Dark board; the pressed key lights in the base color and fades |
| 35 | Whole board in the base color; pressed keys shift hue |
| 39 | One-color ripples from each key |
| 43 | Rainbow ripples from each key |

Two practical findings:

- **The underglow is dim by hardware.** It was already at brightness 255 when it looked almost invisible. A fully saturated primary color lights one of the three emitters per LED; magenta, cyan, yellow, or white are brighter.
- **Reactive effects look dim** because the board is dark except near recent keypresses.

Details and the as-found settings are in [`docs/this-machine.md`](docs/this-machine.md).

## Quick setup on macOS

1. **Use a wired connection for setup.** The web driver and all firmware work need USB. Plug the cable **directly into the Mac**, not through a hub or dock. Chilkey says this, and a reviewer reported hub/dock conflicts on a MacBook. Press `Fn + Space` to put the keyboard in USB mode; the cable must be connected.
2. **Switch to the Mac layout.** Hold `Fn + W` for 3 seconds. The default is Windows. The LCD shows the switch (observed on this keyboard on 2026-11-02; Gadgetoid's review said there was no confirmation, so newer firmware may have added it). To go back to Windows, hold `Fn + Q` for 3 seconds. This swaps the Win/Alt behavior but does not include Mac keycaps.
3. **Customize in the official web driver.** Open https://nd104.chilkey.com/ in **Chrome or Edge** (Firefox and Safari lack WebHID/WebUSB) and click Connect. It handles key remapping, RGB, macros, the screen image/GIF, and time/weather sync. Known bug: the driver refuses to work unless the LCD screen is connected, because the screen is a separate USB device.
4. **Or use VIA.** Go to https://usevia.app in Chrome, open Settings, turn on "Show Design tab", then load Chilkey's `nd104_via_v3_1.json` (link in [`SOURCES.md`](SOURCES.md)) on the Design tab. The board has 6 layers.
   - In VIA, Chilkey's `CUSTOM(0)` Mission Control and `CUSTOM(1)` Launchpad keys reportedly don't work (Gadgetoid, Nov 2025). The workaround is the **Any** key with `0xc1` for Mission Control and `0xc2` for Launchpad.
   - The default Fn layer is missing Mac media, brightness, and Mission Control on the F-row. Add them yourself.
5. **Set the clock.** Run `tools/set_time.py` (above), or use web driver → Screen → "Update Time" / "Update Weather".
6. **Bluetooth (optional, after setup).** Hold `Fn + Z` (or `X`, `C`) for 3–5 s until that key flashes fast, then pick **"ND104 BT1"** (or BT2/BT3) in macOS Bluetooth settings. Short-press the same combo later to switch to that channel. 2.4 GHz: hold `Fn + V` until V flashes purple, then plug in the receiver, which is stored in the compartment on the back.

## Most useful shortcuts

| Keys | Action |
|---|---|
| `Fn + W` (hold 3 s) / `Fn + Q` (hold 3 s) | Mac / Windows layout |
| `Fn + Space` | USB mode |
| `Fn + Z/X/C` short / hold 3–5 s | BT 1/2/3 switch / pair |
| `Fn + V` short / hold | 2.4 GHz switch / pair |
| `Space + Backspace` (hold >5 s) | Factory reset of key settings (Fn LED flashes purple) |
| `Fn + Backspace` (hold) | Battery level on keys 1–0 (1 = 10 %, 0 = 100 %) |
| `Fn + Caps Lock` (hold 5–8 s) | Deep sleep (on battery) |
| `Fn + ]` / `Fn + Shift + ]` | Next backlight / underglow effect |
| `Fn + Shift + H` | Backlight cap on battery: 50 % (default) ↔ 100 % |
| `Fn + N` | Toggle 6KRO / NKRO (default 6KRO) |
| `Fn + Win` | Lock/unlock the left Win (Cmd) key |
| `Fn + Shift + Delete` | Turn off the on-screen keypress display |
| `Fn + F13` (hold) | Screen DFU mode. **Don't do this by accident.** |

The full list, including every lighting and screen shortcut, is in [`docs/manual-reference.md`](docs/manual-reference.md).

## Documentation

| File | Read it when |
|---|---|
| [`docs/manual-reference.md`](docs/manual-reference.md) | You want a shortcut or procedure from the official manual, as searchable text |
| [`docs/troubleshooting.md`](docs/troubleshooting.md) | Something is wrong: not detected, Bluetooth won't pair, web driver won't connect, screen blank, battery flat |
| [`docs/community.md`](docs/community.md) | You want the HID protocol, the `dfu-util` firmware procedure (and how it went on macOS), other people's tools, or review notes |
| [`docs/this-machine.md`](docs/this-machine.md) | You want real readings from one keyboard: USB topology, firmware versions before and after the update, sleep settings, lighting settings |
| [`SOURCES.md`](SOURCES.md) | You want the links: every URL consulted, including the ones that failed to load |

## What is not in this repo

- **Chilkey's own files:** the user manual (a 20-page scanned PDF with no text layer), the VIA definition `nd104_via_v3_1.json` (VID `0x6D67`, PID `0x016C`, 8×16 matrix), and the purchase note. Download the manual and the VIA definition from the links in [`SOURCES.md`](SOURCES.md). A local `official/` folder is git-ignored for keeping copies.
- **Firmware binaries.** Chilkey's advice is not to flash a keyboard that already works. This keyboard was updated on 2026-11-23 anyway, because of a battery-drain problem; see [`docs/this-machine.md`](docs/this-machine.md) and the `dfu-util` notes in [`docs/community.md`](docs/community.md).

## Confidence notes

- Shortcuts come from the official manual PDF (read page by page) and Chilkey's support page. Where those conflict with reviews, the manual wins.
- The VIA keycode workaround (`0xc1`/`0xc2`) comes from one reviewer. It is not verified here.
- The effect-number table lists only what was seen on this keyboard. The claim that the numbers follow QMK's native list rests on the count (0–50) and on those observations; the QMK list was recalled from memory, not checked against the QMK source.
- The battery-drain fix (the V3.0.14 update turning on the sleep timers) appears to have worked, but no battery levels were recorded and a full weekend unplugged has not been retested.
- The keyboard's USB serial number is `vial:f64c2b3c`, which suggests the firmware may also speak the **Vial** protocol. No source confirming Vial support was found, and it has not been tested.
- No Reddit, Stack Exchange, or Kickstarter-comment threads about the ND104 turned up in search. Community knowledge lives mainly in two GitHub authors' repos/gists and in the Chilkey Discord (https://discord.gg/pXsxnerd7n), which isn't searchable.

## Credits

- [MrUrdam/chilkey_nd104_utilities](https://github.com/MrUrdam/chilkey_nd104_utilities) for the reverse-engineered HID protocol that `set_time.py` is built on.
- [borrougagnou/KB_CHILKEY_ND104_Multitool](https://github.com/borrougagnou/KB_CHILKEY_ND104_Multitool) and the same author's gists for the `dfu-util` flashing procedure.
- [Gadgetoid's review](https://gadgetoid.com/2025/11/07/chilkey-nd104-full-sized-mechanical-keyboard/) for the VIA workarounds and hardware notes.

This is an owner's notebook. It is not affiliated with or endorsed by Chilkey.
