# Community knowledge

What I could find outside Chilkey. **No Reddit, Stack Exchange, or Kickstarter-comment threads turned up in search** (several queries, 2026-11-02). The real community work is on GitHub.

## Hardware IDs

| Component | Chip | USB VID:PID |
|---|---|---|
| Keyboard MCU | WCH CH585 (RISC-V, BLE) | `6d67:016c` ("UBEST ND104") |
| Display controller | U-BEST UB32F341S (ARM, RTX + LVGL), 320×172 | `5542:0001` |
| Display in DFU | | `5542:1000` |
| Keyboard in DFU | | `5542:0104` |

Source: MrUrdam README and borrougagnou gists. The non-DFU IDs match what this Mac reports; see `this-machine.md`.

## GitHub projects

### MrUrdam/chilkey_nd104_utilities (MIT)

https://github.com/MrUrdam/chilkey_nd104_utilities

- **ND104 Studio:** a Windows 10/11 tray app for time sync (NTP, time zones, DST), weather (5 providers), lighting, screen images/GIFs, keymap editing, a firmware safety lock, and update notifications.
- **nd104-probe:** a CLI that reads firmware versions and tests time/weather packets.
- **firmware/versions.json:** tracks the latest files on Chilkey's Drive.
  - Keyboard: `VN001_314A108_1V0_RGB_TYPE1_20260710.bin` (V3.0.14)
  - Screen 24 h/°C: `ND104_SCREEN_MCU_320_172_V1.0.0_20260317.bin` + `ND104_SCREEN_UI_320_172_V1.0.0_20251104.bin` (V1.2.4)
  - Screen 12 h/°F: `ND104_SCREEN_MCU_CF_320_172_V1.0.0_20260305.bin` + `ND104_SCREEN_UI_320_172_V1.0.0_20251230.bin`
- It only supports a USB connection. **There is no macOS app.**

### borrougagnou/KB_CHILKEY_ND104_Multitool (GPL-3.0)

https://github.com/borrougagnou/KB_CHILKEY_ND104_Multitool

- A C++/libusb tool with `clock_update` and `weather_update` binaries for Linux, Mac, and Windows. It is meant to run on a timer so the screen clock stays correct.
- **macOS is marked "not tested".** It installs to `~/Library/Application Support/Chilkey_ND104/` with LaunchAgents `com.chilkeynd104.chilkeynd104clock` (every 5 h) and `...weather` (every 30 min).
- There's a README bug: the macOS `launchctl bootstrap` lines use `$$HOME` (which expands to the PID). It should be `$HOME`.

### borrougagnou gists

- **Linux compatibility list:** https://gist.github.com/borrougagnou/93ebe6d08eac488e2e2a2b2d452e5bdb
  - Needs udev rules for `6d67:016c` and `5542:0001`; delete any old `99-ubest.rules`.
  - Chrome, Brave, Opera, and Chromium work for remapping, macros, RGB, uploads, and time. Firmware updates through the browser don't work on Linux. Firefox and Epiphany don't work at all (no WebUSB/WebHID). Snap browsers fail.
- **Firmware upgrade via dfu-util:** https://gist.github.com/borrougagnou/ab98c68cb6812d76fc0357e57f8541d9 (summary below)

## Firmware flashing with dfu-util (community procedure)

> Only do this if you have a reason to. Check SHA-256 sums first. Use wired USB, no hub.

- Keyboard DFU: hold **Left Shift + Right Shift**, then press **B**. Keys and RGB go dead.
- Screen DFU: long-press `Fn + F13`.
- DFU exits after 3 min idle.
- Run `dfu-util -l` first and confirm the device appears.

```sh
# keyboard (~11 s)
dfu-util -a 0 -d 5542:0104 -s 0x6000:leave -D keyboard.bin
# screen MCU (~6 s), then screen UI (~1 min)
dfu-util -a 0 -d 5542:1000 -s 0x8000 -D screen_mcu.bin
dfu-util -a 0 -d 5542:1000 -s 0x70080000:leave -D screen_ui.bin
```

- The gist says "Error during download get_status" after the screen-UI step is expected.
- On Windows, you need Zadig/WinUSB.
- The gist's `SHA256SUMS` file lists hashes for the Drive files.

### Tested on macOS, 2026-11-23

Done on this keyboard with `dfu-util` 0.11 from Homebrew, the keyboard plugged directly into the Mac. No `sudo` was needed.

- **Keyboard DFU:** after Left Shift + Right Shift + B the keys go dead but the **RGB stays on** (the gist says the RGB stops too; this was from firmware V3.0.2). The device re-enumerates as `5542:0104` "UBEST DFU Firmware Update".
- `dfu-util -l` matched the gist exactly: `name="@InternalFlash /0x6000/114*4Kg", serial="UB32"`.
- The keyboard flash ended with "Transitioning to dfuMANIFEST state" and the keyboard came back by itself as V3.0.14.
- **Screen DFU:** a long press of `Fn + F13` gives `5542:1000` "UBEST DFU Screen Firmware Update", with `name="@Internal Flash  /0x00000000/8*4Ka,120*4Kg,3583*512Ka,4096*4Kg"`.
- The screen-UI step did **not** show the `get_status` error here. It ended with "Transitioning to dfuMANIFEST state", and the screen rebooted as V1.2.4.
- **A backup read is not useful.** `dfu-util -a 0 -d 5542:0104 -s 0x6000:466944 -U backup.bin` completes, but only the header (which carries the model tag `VN001_314A108_1V0`, the same as in the vendor file) is readable; the rest comes back scrambled. There is no way back to the old version from such a file.
- `dfu-util` reports a download size 16 bytes smaller than each `.bin` file.
- The clock must be set again after the screen flash.
- Conda (conda-forge) has no macOS build of `dfu-util`. Homebrew does.
- **Don't run a Homebrew upgrade during a flash.** Here one was running in the background and removed libusb between the keyboard and screen steps, so `dfu-util` died with "Library not loaded: …/libusb-1.0.0.dylib" while the screen sat in DFU mode. Setting `DYLD_FALLBACK_LIBRARY_PATH` to another directory holding `libusb-1.0.0.dylib` (the project's `.conda/lib`) got it going again.

## HID protocol (from MrUrdam `docs/protocol.md`)

- Both devices: vendor usage page `0xFF60`, usage `0x61`, no report ID.
  - Keyboard: interface 1, 32-byte reports.
  - Screen: interface 0, 64-byte reports.
- Packet CRC is CRC-16/CCITT-FALSE (poly `0x1021`, init `0xFFFF`), computed with bytes 6–7 zeroed and stored little-endian in bytes 6–7.
- `1C` command frames: `A5` magic at byte 8, command at byte 9, length at byte 11, payload at byte 12+, then an 8-bit checksum = `(sum(bytes 9..) ^ 0xFF) & 0xFF`.
  - Time = `0x38`: year in big-endian, then month, day, hour, minute, second, weekday (0 = Sunday). Local time, with no time zone.
  - Weather = `0xFE`: icon index 0–9, plus current/max/min temperature in °C×10 as **sign-magnitude** (bit 15 = negative).
  - Acknowledgement: `A5 <cmd> 00 02 <status>`, where `FE` = OK and `FC` = rejected.
- The official web driver always sends icon `0x02`, so the weather icon never changes. That's a driver bug.
- Firmware version query: `11 02`, zero-padded to the report size, with the packet CRC. The answer has the text length at byte 5 and ASCII from byte 8. It works on both devices.
- Keyboard settings use plain VIA frames with no `1C` wrapper and no CRC. Read with `08 00 04 <id>`; the value comes back in byte 4. `0B` = sleep minutes, `07` = deep-sleep minutes, `00` = polling rate, `01`/`02` = debounce time/mode.
- **Checked on this keyboard, 2026-11-23:** the time packet over the keyboard route and both version queries work on V3.0.2/V1.2.0 and on V3.0.14/V1.2.4. The settings reads answer on both keyboard versions; values are in `this-machine.md`. Nothing else in this section has been tested here.
- On macOS the vendor interface (usage page `0xFF60`, usage `0x61`) opens with the `hidapi` Python package and needs no special permission. `tools/set_time.py` uses it.

## Reviews and their practical notes

- **Gadgetoid (Nov 2025)**, https://gadgetoid.com/2025/11/07/chilkey-nd104-full-sized-mechanical-keyboard/
  - VIA: Chilkey's Mission Control/Launchpad custom keycodes don't work. Use the Any key with `0xc1` and `0xc2` instead.
  - Encoder defaults are `CUSTOM(16)` for press, `CUSTOM(15)` for clockwise, and `CUSTOM(14)` for counterclockwise. `LCD_CALC` can be mapped to the button left of the LCD.
  - Dictation and Do Not Disturb keys can't be bound.
  - The web driver requires the LCD to be connected.
  - Hub/dock conflicts on a MacBook.
  - Backlight brightness is low, and the underglow also drives the nav-cluster light bar.
  - The knob has a grub screw (Allen key). The LCD/knob shroud uses Torx T6, which isn't included.
  - Battery: 2 × 4000 mAh LiPo, replaceable.
  - Calculator: long-press `(` / `)` for parentheses. There are no powers, roots, or trig functions.
- **AppleInsider review (Oct 2025)**, https://appleinsider.com/articles/25/10/31/chilkey-nd104-review-extremely-solid-construction-for-a-mechanical-keyboard. The page returned 403, so it wasn't read.
- **IgorsLab (ISO-DE)**, https://www.igorslab.de/en/chilkey-nd104-as-a-full-size-iso-aluminum-keyboard-in-pre-assembled-design-igors-new-keyboard-in-progress. Not read in detail.
- **LTT Labs**, https://www.lttlabs.com/products/keyboards/CHILKEYND104. The page returned 403. A search snippet says it lists the board as **not** QMK/VIA compatible, but that conflicts with Chilkey's VIA JSON, and the listing is older than the VIA file.

## QMK / Vial

- No QMK source or community QMK port exists. The firmware is Chilkey's own closed firmware on a WCH CH585.
- It speaks the VIA protocol, so the official JSON loads in usevia.app.
- The USB serial is `vial:f64c2b3c`, which hints at Vial protocol support. That is unconfirmed by any source and untested here.
