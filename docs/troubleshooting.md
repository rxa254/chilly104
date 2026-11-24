# Troubleshooting

Sources: Chilkey support page (https://chilkey.com/pages/nd104-keyboard_support_c), the FAQ (https://chilkey.com/blogs/updates/nd104-faq-resources), and community reports, which are labeled where they appear.

## Keyboard not detected or disconnects (wired)

Try these one at a time, in order:
1. Plug it **directly into the computer**. The FAQ says "avoid hubs or switchers". Gadgetoid saw conflicts with a USB-C hub/dock on a MacBook.
2. Use a different, properly shielded USB cable.
3. Try a different port.
4. Try another computer.
5. Check that the internal connector is seated. This requires opening the case; see `manual-reference.md` §9.

Also make sure the keyboard is in USB mode (`Fn + Space`).

## Bluetooth won't pair

- Try all three channels: hold `Fn + Z`, `Fn + X`, and `Fn + C` for 3–5 s each, until the key flashes fast.
- On the Mac, remove any old "ND104 BT*" entry first, then pair again.
- Check that the keyboard shows up on a phone's Bluetooth list. If it does, the keyboard is fine and the problem is on the computer side.
- Charge the battery before pairing.

## 2.4 GHz won't connect

- Order matters: hold `Fn + V` until V flashes fast, **then** insert the receiver.
- Keep it away from other USB receivers, keep the keyboard close, and keep the path clear.

## Wrong modifier keys on Mac (Cmd/Option swapped)

- Hold `Fn + W` for 3 s to switch to the Mac layout. The LCD shows the switch (observed 2026-11-02).
- If the left Cmd key does nothing, the Win key may be locked. Its backlight is white when locked; press `Fn + Win` to unlock.

## Web driver (nd104.chilkey.com) won't connect

- **Page spins and never loads (seen 2026-11-02, Chrome on macOS).** The site itself answered normally (HTTP 200 in under 0.3 s from the same Mac), and the page later loaded and connected on its own. One possible cause, untested: `index.html` loads `cropper.min.js` from `cdn.bootcdn.net`, a CDN in China, which can be slow. If it happens again, reload.
- **Setting the clock:** connect, then Screen → Update Time. It uses the Mac's local time and syncs only when you click, so do it again after the battery dies or the keyboard is fully powered off. Confirmed working 2026-11-02.
- **Setting the clock without the web driver:** `.conda/bin/python tools/set_time.py` with the keyboard on USB. It prints the keyboard firmware version and the screen's acknowledgement. Confirmed working 2026-11-23 on firmware V3.0.2 and V3.0.14.
- Use Chrome or Edge. Firefox fails; see webcompat issue https://github.com/webcompat/web-bugs/issues/233268. Safari doesn't support WebHID.
- Use a wired connection only.
- The **LCD screen must be connected**. The driver refuses to work otherwise (Gadgetoid).
- The driver's reported **screen** firmware version is often wrong (MrUrdam). Don't flash just because the number looks old.
- Linux: you need udev rules for `6d67:016c` and `5542:0001`, and Snap-packaged browsers don't work (borrougagnou gist).

## Screen problems

- Blank or odd screen: open the case, reseat the screen's flat-flex connector, make sure the battery is installed, then restart with the battery in. The flex cable to the daughterboard is easy to knock loose during reassembly (Gadgetoid).
- After a full power-off without a battery, the screen may start on a different page.
- `Fn + F13` restarts the LCD. `Fn + Shift + F13` restores the LCD's factory settings. A **long** press of `Fn + F13` enters DFU mode, which times out after 3 minutes idle.

## Knob doesn't respond

- Pull the knob, check that the pins on both sides aren't bent or pushed in, then reseat it firmly.
- If it responds slowly, reconnect the keyboard and check the firmware version.

## Battery percentage seems off

- A firmware update may help. That is the only case where Chilkey suggests updating.

## Battery flat and clock wrong after sitting unplugged

Seen on this keyboard on 2026-11-23, after a weekend unplugged, on keyboard firmware V3.0.2.

- The wrong clock follows from the flat battery. Fix the drain, then set the time again.
- Chilkey's support page says the keyboard sleeps after 10 minutes idle on battery and never sleeps on USB power. `Fn + Caps Lock` held 5–8 s forces deep sleep.
- On V3.0.2 the sleep and deep-sleep timers both read 0. After updating to V3.0.14 they read 10 and 20 minutes. See `this-machine.md`.
- The update appears to have fixed the drain: on 2026-11-24, the day after, the clock was still correct. No battery levels were recorded, and a full weekend unplugged has not been retested. To quantify: charge to full, unplug, note the `Fn + Backspace` level, and look again the next morning.
- Charge directly from the computer or a wall charger. Charging is capped at 500 mA, about what the backlight and LCD can draw.

## Reset everything

- Keys: hold `Space + Backspace` for more than 5 s. The Fn LED flashes purple.
- LCD: `Fn + Shift + F13`.

## Firmware

- **Chilkey's advice is not to flash a keyboard that works.** Flashing can brick it.
- Flash only over a stable direct USB connection, with other USB devices unplugged, and don't touch the keyboard during the update.
- Versions: the support page lists keyboard V3.0.4 and screen V1.2.1. Chilkey's Drive actually holds keyboard **V3.0.14** (2026-07-10) and screen **V1.2.4** (2026-03-17), according to MrUrdam's `versions.json`, updated 2026-10-31.
- See `community.md` for the dfu-util procedure. It was used on this keyboard on 2026-11-23 from macOS, V3.0.2 → V3.0.14 and screen V1.2.0 → V1.2.4, without problems.

## Contact

Email service@chilkey.com with a short video, your firmware version, and your OS. There's also a Discord: https://discord.gg/pXsxnerd7n.
