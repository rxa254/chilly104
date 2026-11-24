# ND104 user manual: transcribed reference

Source: Chilkey's ND104 user manual PDF (manual pages 18–34; link in `SOURCES.md`, not included in this repo). The PDF has no text layer, so this is a transcription of its pages.

## 1. Connection (pp. 18–21)

**Wired.** Use a USB Type-A → Type-C cable. "If you are using a macOS device, you may need a Type-C to Type-A adapter." `Fn + Space` = switch to USB mode (the cable must be connected).

**Bluetooth.** Device names are `ND104 BT1`, `ND104 BT2`, and `ND104 BT3`.
1. Long-press `Fn + Z / X / C` (BT1 / BT2 / BT3) to enter pairing mode.
2. While pairing, that key's LED flashes rapidly.
3. On the computer, enable Bluetooth and select "ND104 BT1".

Once channels are paired, short-press `Fn + Z/X/C` to switch between them.

**2.4 GHz.** The device name is `ND104 2.4G`.
1. Hold `Fn + V` until V flashes purple rapidly.
2. Insert the receiver into the computer.

Long-press `Fn + V` = receiver pairing mode; short-press = switch to 2.4 GHz. The receiver is stored in the compartment on the back of the keyboard ("press to open" round cover).

## 2. Layout (p. 22)

- The PCB supports full split layouts: stepped Caps Lock, split left/right Shift, split Spacebar, split Backspace, plus ISO and ANSI.
- The supplied plate does **not** support split configurations. Ask customer service for the plate design files. (ANSI and ISO `.dwg` plate files are linked on https://chilkey.com/pages/console.)
- The four keys at top right (knob, screen buttons) "can be customized as keyboard keys".
- The keyboard ships with a silicone storage case in the same color.

## 3. Lighting (p. 23)

Backlight, with `Fn +`:

| Key | ↑ | ↓ | ← | → | `\` | `]` | `P` | `;` | `[` | `'` |
|---|---|---|---|---|---|---|---|---|---|---|
| Action | brightness + | brightness − | speed − | speed + | on/off | effect switch | hue + | hue − | saturation + | saturation − |

Underglow, with `Fn + Shift +`:

| Key | ↑ | ↓ | `\` | `]` | `P` | `;` | `[` | `'` |
|---|---|---|---|---|---|---|---|---|
| Action | brightness + | brightness − | on/off | effect switch | hue + | hue − | saturation + | saturation − |

- `Fn + /` (hold 3 s) = Lighting Test Mode. Press any key except the arrows to exit.
- `Fn + N` = 6KRO/NKRO toggle. Default is 6KRO.

FAQ addition: `Fn + Right Shift + L` disables OS "dynamic lighting" control in wired mode (requires current firmware).

## 4. LCD screen (p. 24)

| `Fn +` | Action |
|---|---|
| Delete | LCD on/off |
| PageUp / PageDown | LCD page up / down |
| Rotate knob | LCD page up/down |
| Short-press knob | LCD on/off |
| Cal/Enter | Enter/exit calculator mode |
| Shift + Delete | Keypress character display on/off |
| F13 | Restart the LCD |
| Shift + PgUp / PgDn | Screen brightness |
| Shift + F13 | Restore LCD factory settings |
| F13 (long press) | **Screen DFU (firmware upgrade) mode.** Exits after 3 minutes idle. |

- In calculator mode, the Fn screen operations above are disabled.
- Num Lock toggles Num Lock. In calculator mode it acts as the calculator's Backspace (CE).

## 5. Win/Mac layout (p. 24)

- `Fn + Q` long-press 3 s = Windows layout.
- `Fn + W` long-press 3 s = Mac layout.
- The default is **Windows**.

## 6. Other functions (p. 25)

| Keys | Action |
|---|---|
| `Space + Backspace` hold >5 s | Factory reset. The Fn LED flashes purple on success. |
| `Fn + Win` | Lock/unlock left Win key. When locked, its backlight turns white. |
| `Fn + M` | Charging indicator on/off |
| `Fn + Shift + H` | Max backlight on battery: 50 % (default, power saving) ↔ 100 % |
| `Fn + Backspace` hold (on battery) | Keys 1–0 show charge in green (1 = 10 % … 0 = 100 %) |

Indicators:
- Low battery: the Fn LED flashes red.
- Charging: the Fn LED flashes green and turns off when charging is complete.
- Caps Lock: the indicator glows red.

## 7. Indicator lights (p. 26)

- Caps Lock indicator: Caps key
- Win Lock indicator: Win key
- BT1 / BT2 / BT3 indicators: Z / X / C
- 2.4G indicator: V
- Factory reset indicator: Fn
- Battery indicator: number row 1–0

## 8. Web driver (pp. 27–30)

Connect over USB, then open https://nd104.chilkey.com/ in Edge or Chrome.

- **Keyboard:** click a key in the top panel, then click its new function in the lower panel.
- **RGB Lighting:** choose Backlight or Underglow, mode dropdown, Brightness and Speed sliders.
- **Screen:** Choose File → Crop Image → Download Image. Recommended images are 320×172 px, PNG/JPG/GIF, GIF under 60 frames, file under 2 MB. The Functions panel has "Update Time" and "Update Weather".
- **Macros:** set the delay, click Record, type the keys, click Stop Recording, then save. Assign it under Keyboard → Macro: pick a key, then pick the macro.

## 9. Disassembly (pp. 31–33)

1. Loosen the knob's set screw with the included hex wrench and pull the knob off.
2. Put your fingers at the top/bottom case seam and your thumbs on keycaps (Caps Lock on the left, numpad `+` on the right). Press down with your thumbs and lift with your fingers. The case is held by quick-release ball catches.

## 10. Electrical (p. 34)

| Item | Value |
|---|---|
| Current, backlight on | ≤ 500 mA |
| LCD current | ≤ 200 mA |
| Current, backlight off | ≤ 100 mA |
| Sleep current | ≤ 2 mA |
| Wireless working current | ≤ 20 mA |
| USB voltage | 5 ± 0.5 V |
| Battery | Li-ion, 3.7 V typical, 4.2 V max (reviewers: 2 × 4000 mAh packs) |
| Charge current | ≤ 500 mA |
