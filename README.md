# chilly104

Notes, official files, and community knowledge for the **Chilkey ND104**: a full-size (104-key) tri-mode mechanical keyboard with a knob and an LCD calculator/clock screen.

Product page: https://chilkey.com/products/nd104-keyboard

## Layout of this repo

| Path | What it is |
|---|---|
| `README.md` | This file: a quick setup path for macOS |
| `docs/manual-reference.md` | Every shortcut and procedure from the official user manual, transcribed (the PDF is image-only) |
| `docs/troubleshooting.md` | Official troubleshooting and FAQ, plus community fixes |
| `docs/community.md` | GitHub tools, reverse-engineered protocol, firmware flashing, reviews, known bugs |
| `docs/this-machine.md` | What this Mac reported about the keyboard (2026-11-02), plus the 2026-11-23 firmware update and sleep settings, and the 2026-11-24 lighting settings and effect numbers |
| `tools/set_time.py` | Sets the LCD clock from this Mac over USB (needs the `hidapi` pip package) |
| `tools/idle_breathe.py` | Background script: backlight breathes red when idle and is rainbow key-reactive while typing (macOS, needs `hidapi`). Tests in `tools/test_idle_breathe.py` |
| `SOURCES.md` | Every URL consulted, including which ones failed to load |

Chilkey's own files are **not** in this repo: the user manual (a 20-page scanned PDF with no text layer), the VIA definition `nd104_via_v3_1.json` (VID `0x6D67`, PID `0x016C`, 8×16 matrix), and the purchase note. Download the manual and the VIA definition from the links in `SOURCES.md`; a local `official/` folder is git-ignored for keeping copies.

Firmware binaries are **not** included on purpose. Chilkey's advice is not to flash a keyboard that already works. This keyboard was updated on 2026-11-23 anyway, because of a battery-drain problem; see `docs/this-machine.md` and the dfu-util notes in `docs/community.md`.

## Quick setup on macOS

1. **Use a wired connection for setup.** The web driver and all firmware work need USB. Plug the cable **directly into the Mac**, not through a hub or dock. Chilkey says this, and a reviewer reported hub/dock conflicts on a MacBook. Press `Fn + Space` to put the keyboard in USB mode; the cable must be connected.
2. **Switch to the Mac layout.** Hold `Fn + W` for 3 seconds. The default is Windows. The LCD shows the switch (observed on this keyboard on 2026-11-02; Gadgetoid's review said there was no confirmation, so newer firmware may have added it). To go back to Windows, hold `Fn + Q` for 3 seconds. This swaps the Win/Alt behavior but does not include Mac keycaps.
3. **Customize in the official web driver.** Open https://nd104.chilkey.com/ in **Chrome or Edge** (Firefox and Safari lack WebHID/WebUSB) and click Connect. It handles key remapping, RGB, macros, the screen image/GIF, and time/weather sync. Known bug: the driver refuses to work unless the LCD screen is connected, because the screen is a separate USB device.
4. **Or use VIA.** Go to https://usevia.app in Chrome, open Settings, turn on "Show Design tab", then load Chilkey's `nd104_via_v3_1.json` (link in `SOURCES.md`) on the Design tab. The board has 6 layers.
   - In VIA, Chilkey's `CUSTOM(0)` Mission Control and `CUSTOM(1)` Launchpad keys reportedly don't work (Gadgetoid, Nov 2025). The workaround is the **Any** key with `0xc1` for Mission Control and `0xc2` for Launchpad.
   - The default Fn layer is missing Mac media, brightness, and Mission Control on the F-row. Add them yourself.
5. **Set the clock.** Run `.conda/bin/python tools/set_time.py` with the keyboard on USB, or use web driver → Screen → "Update Time" / "Update Weather". The keyboard does not sync time on its own, and it loses the time when the battery runs flat.
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
| `Fn + N` | Toggle 6KRO / NKRO (default 6KRO) |
| `Fn + Win` | Lock/unlock the left Win (Cmd) key |
| `Fn + Shift + Delete` | Turn off the on-screen keypress display |
| `Fn + F13` (hold) | Screen DFU mode. **Don't do this by accident.** |

The full list is in `docs/manual-reference.md`.

## Confidence notes

- Shortcuts come from the official manual PDF (read page by page) and Chilkey's support page. Where those conflict with reviews, the manual wins.
- The VIA keycode workaround (`0xc1`/`0xc2`) comes from one reviewer. It is not verified here.
- The keyboard's USB serial number is `vial:f64c2b3c`, which suggests the firmware may also speak the **Vial** protocol. I found no source confirming Vial support and have not tested it.
- No Reddit, Stack Exchange, or Kickstarter-comment threads about the ND104 turned up in search. Community knowledge lives mainly in two GitHub authors' repos/gists and in the Chilkey Discord (https://discord.gg/pXsxnerd7n), which isn't searchable.
