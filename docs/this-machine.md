# This Mac: observed 2026-11-02

From `system_profiler SPUSBHostDataType` with the keyboard on USB-C:

```
VIA Labs hub (2109:2813, 480 Mb/s)        <- external hub (also: C920 webcam, SINOWEALTH mouse)
└── USB HUB (1a86:8091, QinHeng, 480 Mb/s) <- inside the keyboard (only ND104 devices behind it)
    ├── ND104 screen  UBEST  5542:0001  12 Mb/s  serial <redacted>
    └── ND104         UBEST  6d67:016c  12 Mb/s  serial vial:f64c2b3c  500 mA
```

The `1a86:8091` hub has nothing behind it except the keyboard and its screen, so it is almost certainly the ND104's own internal hub. That's how one USB-C cable carries two USB devices. This is inferred from the topology; no source confirms it.

## What this means

- Both the keyboard and its screen enumerate correctly, so the cable and USB mode are fine.
- The keyboard IDs match the official VIA JSON (`0x6D67` / `0x016C`).
- **It's connected through one external hub** (VIA Labs `2109:2813`). Chilkey says to avoid hubs, and a reviewer saw hub/dock conflicts on a MacBook. If anything flaky happens, especially with the web driver or a firmware update, plug it directly into the Mac first.
- `system_profiler SPBluetoothDataType` showed no ND104 entry, so it has never been paired over Bluetooth on this Mac.

# Firmware update and sleep settings: 2026-11-23

## Why

After a weekend unplugged, the battery showed 1 % and the LCD clock was wrong. The clock is a consequence of the battery: the screen only gets the time when a host pushes it, and loses it when power drops out.

## Versions (read from the devices over USB)

| Part | Before | After |
|---|---|---|
| Keyboard | `V3.0.2 Nov  4 2025 17:17` | `V3.0.14 20260710_123331` |
| Screen (24 h/°C) | `V1.2.0 Nov  4 2025 16:27:41` | `V1.2.4 Mar 17 2026 21:37:00` |

Files flashed, all from Chilkey's Drive folders, SHA-256 matched against the borrougagnou gist's `SHA256SUMS`:

- `VN001_314A108_1V0_RGB_TYPE1_20260710.bin`
- `ND104_SCREEN_MCU_320_172_V1.0.0_20260317.bin`
- `ND104_SCREEN_UI_320_172_V1.0.0_20251104.bin`

The procedure and what was observed on macOS are in `community.md`.

## Keyboard settings (VIA read `08 00 04 <id>`, value in byte 4)

| id | Setting | V3.0.2 | V3.0.14 |
|---|---|---|---|
| `0B` | Sleep time (min) | 0 | 10 |
| `07` | Deep-sleep time (min) | 0 | 20 |
| `00` | USB polling rate | 8 | 1 |
| `01` | Debounce time (ms) | 5 | 5 |
| `02` | Debounce mode | 2 | 2 |
| `05` | Online RGB | 0 | 0 |

- Nothing was written to these settings; the changes came with the flash.
- The 0s on V3.0.2 mean either that sleep was disabled or that V3.0.2 does not implement those ids. Not determined.
- The polling-rate value changed from 8 to 1 on its own. Left as is.

## Still open

- **2026-11-24: the sleep fix appears to have worked.** The day after the update the LCD clock was still correct, so the keyboard had not lost power. No `Fn + Backspace` levels were recorded, so the drain rate is not quantified, and a full weekend unplugged (the original failure) has not been repeated. To quantify: charge to full (Fn LED stops flashing green), unplug, note the `Fn + Backspace` level, and compare the next morning.
- A weekend is about 60 h. Chilkey's figures are 28 h wireless with lighting and screen on, 118 h with them off, and ≤ 2 mA asleep, so a full battery going flat over a weekend means it did not sleep, was not full, or the gauge is wrong.
- Charging is capped at 500 mA, and backlight plus LCD can draw about that much. On a 500 mA hub port it may barely charge while in use. Not measured.

## Connection

- For the flash, the keyboard was moved off the VIA Labs hub and plugged directly into the Mac. In that arrangement the only hub in the path is the keyboard's own `1a86:8091`.

# Lighting: 2026-11-24

Read and set over USB with plain VIA frames on the keyboard's vendor interface: `08 <channel> <id>` reads, `07 <channel> <id> <value…>` sets. Channel `02` is the underglow (rgblight) and `03` is the per-key backlight (rgb_matrix). Ids: `01` brightness, `02` effect, `03` speed, `04` color (hue, saturation, each 0–255).

## As found (after the V3.0.14 flash)

| | Brightness | Effect | Speed | Hue, saturation |
|---|---|---|---|---|
| Underglow | 255 | 6 | 0 | 0, 255 |
| Backlight | 255 | 13 | 127 | 0, 255 |

- The underglow was "almost invisible" even though it was already at full brightness, so the dimness is hardware, not a setting.
- The backlight reads back 254 when 255 is sent.

## Backlight effect numbers

- The firmware accepts effects 0–50; anything higher reads back as 50.
- The numbers follow QMK's full native rgb_matrix effect list, **not** the shorter list in VIA's `qmk_rgb_matrix` menu. The QMK list was recalled from memory, not checked against the QMK source.
- Observed on this keyboard:

| Effect | What it did |
|---|---|
| 1 | Solid color |
| 5 | Breathing (used for the idle state; "looks good") |
| 32 | Typing heatmap; barely changes with normal typing |
| 34 | Dark board; the pressed key lights in the base color and fades |
| 35 | Whole board in the base color; pressed keys shift hue |
| 37 | Faint, one color |
| 39 | One-color ripples from each key |
| 42 | Not described by the user after it was set |
| 43 | Rainbow ripples from each key ("too exciting") |

- Underglow effect 1 is a solid color. Other underglow effect numbers were not explored.

## Setup on 2026-11-24 (not saved, later lost)

- Underglow: solid blue (effect 1, hue 170, saturation 255, brightness 255).
- Backlight: driven by `tools/idle_breathe.py` while that script runs. Red breathing (effect 5, speed 88, for a period of about 3 s by QMK's formula; the period was not timed) after 5 s without a keypress, and effect 34 with the base hue swept around the color wheel every 4 s while typing.
- None of this was saved with the VIA save command (`09`).
- hidapi opens the vendor interface exclusively on macOS: a second open fails while another process holds it. The script therefore holds the device only while it is sending.

## Saved configuration: 2026-11-25

- On 2026-11-25 the keyboard was paired over Bluetooth, moved to a wall charger, and later returned to USB. Afterwards the unsaved colors were gone: the underglow read back exactly as found on 2026-11-24 (effect 6, speed 0, hue 0, saturation 255), not blue. So values set with `07` and not saved do not survive; which step (mode switch or loss of USB power) reset them was not isolated.
- The backlight was then chosen by hand with `Fn + ]` and stored with `09 02` and `09 03` (the keyboard echoed both). Stored values:

| | Brightness | Effect | Speed | Hue, saturation |
|---|---|---|---|---|
| Underglow | 255 | 6 | 0 | 0, 255 |
| Backlight | 255 | 20 | 0 | 56, 255 |

- Whether the stored values survive a power cycle has not been tested.
- Over Bluetooth, macOS lists the vendor interface but refuses to open it ("open failed"), so lighting can be read and set only over USB.
- No battery or charging readout exists over USB (settings ids `00`–`2F` and the other VIA channels were read; nothing battery-like). Over Bluetooth, macOS shows the level in `pmset -g accps`; it read 65 % from 13:52 to 13:57, too short a span to show charging.
