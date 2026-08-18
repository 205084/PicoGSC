# The PowerBook 180 GSC panel bus

Everything here was **measured**, not taken from documentation — Apple never
published the electrical interface of this bus. Corrections and independent
confirmations are very welcome.

Equipment used: gusmanb RP2350-based logic analyser, Voltcraft DOV-1004
(rebadged Rigol DHO, 12-bit, 100 MHz, 4 ch), and finally the capture firmware
in this repository.

---

## 1. The chip

The **GSC (Gray Scale Controller)** is the display controller in the PowerBook
160/165/180. Apple names it in the 160/180 Developer Note but documents it only
at framebuffer level (128 KB VRAM, 16 bit wide, byte-addressable, 1/2/4 bit
modes, framebuffer base at `$6000 0000`). Reportedly it is a **Chips &
Technologies 65210** — worth chasing for a real datasheet.

The earlier PowerBooks (100, 14x, 170) use *Omaha2* instead, called the DDC
(Display Driver Chip) in the 140/170 Developer Note. Omaha2 is comparatively
well understood by the community because schematics with the interconnect
pinout exist. **No such schematics exist for the 16x/180.**

The Service Source confirms the parts are not interchangeable: the 180 uses
display 661-0748, cable 630-6273, inverter 922-0024 — all different from the
160/165 FSTN units.

---

## 2. Signals on the 26-pin interconnect

| Signal | Direction | Function |
|---|---|---|
| FPDATA[0..7] | GSC → panel | pixel data, 2 pixels per byte, 4 bpp |
| CL2 | GSC → panel | byte clock (often called the dot clock) |
| CL1 | GSC → panel | line clock |
| FLM | GSC → panel | first line marker, i.e. frame sync |
| M_F | GSC → panel | AC drive / frame polarity. Measured static high. |
| DISP_BLANK | GSC → panel | data valid |
| STN_MODE | → GSC | panel identification strap, **input to the GSC** |
| GND | — | several pins (1, 4, 7 among others) |

The names follow the conventions used in the 140/170 schematics and the general
Sharp/Hitachi flat-panel interface family.

**STN_MODE tied to GND** makes the machine initialise video with no panel
attached — extremely useful for bench work, and it keeps the fragile original
panel out of the test setup.

---

## 3. Timing

| Parameter | Value |
|---|---|
| Resolution | 640 × 400 |
| Colour depth | 4 bpp linear — **not** dual-scan |
| Bytes per line | 320 (exact) |
| Lines per frame | 400 (exact) |
| Vertical blanking | **none** |
| Framebuffer | 128,000 bytes |
| CL2 during burst | ~15.7 MHz |
| CL2 line average | 13.06 MHz |
| Burst length | ~20.4 µs |
| CL1 | ~40.8 kHz |
| Logic level | 5 V |

CL2 derives from a 31.3344 MHz GSC oscillator divided by two.

### FLM is mode-dependent

This tripped me up initially, so it is worth stating clearly:

| State | FLM |
|---|---|
| ROM boot screen (blinking floppy / checkerboard) | **exactly 102 Hz** |
| OS loaded, 16 grey levels selected | **69.9 Hz** |

The burst length stays constant at ~20.4 µs; what changes is the **pause
between bursts** (~4 µs at 102 Hz, ~15.4 µs at the slower mode). The transition
is visible live on a scope when the ROM hands over to the OS.

Note this does not fully agree with liamur's earlier reference table for the
Duo/160 (2-bit/4-bit → 87 Hz, 1-bit → 68 Hz). Measured here at 16 grey levels
is 69.9 Hz, i.e. his 1-bit figure. **Unresolved.**

Practical consequence: **do not hard-code a frame rate.** The capture logic
should wait on FLM and count bytes, which is mode-agnostic by construction.

---

## 4. Data format

- One byte carries **two pixels**, 4 bits each.
- Sampling on the **falling CL2 edge** (Sharp convention) is correct — verified
  on the first attempt.
- High nibble first — verified against the actual panel image, not assumed.

### Polarity

**A higher nibble value means darker.** This is the correct convention from
QuickDraw's perspective, and the panel implements it faithfully. Modern display
formats expect the opposite, so the inversion belongs on the output side, not
in the bus data. PicoGSC handles it in the display palette and keeps captured
data raw.

### The LSB finding — preliminary

Across entire frames, only the values **0, 4, 8 and 14** occur. Bit 0 of each
nibble is never set, i.e. FPDATA0 and FPDATA4 appear to stay low permanently.

If that holds, the 180's GSC drives effectively **8 grey levels** in this mode,
which would be consistent with liamur's earlier observation about D4.

⚠️ **Not yet verified.** A wiring fault on exactly those two lines has not been
ruled out. The check is straightforward: put the logic analyser on the **5 V
(A) side** of level shifter chip 1 and watch FPDATA0/FPDATA4 while the machine
runs. Toggling there but not on the B side means a wiring fault; not toggling
at all confirms the GSC.

---

## 5. Panel architecture (from component inspection)

Deduced by examining the panel PCB, not from documentation:

- **6× Toshiba T6A40** — row/gate drivers, 68 outputs each → 6 × 68 = 408 rows
- **6× TAB-bonded custom dies marked A37E7** — column/source drivers
- **4× µPC4064G** (NEC dual J-FET op-amps) = 8 amplifiers, paired with 16 small
  transistor buffer stages → generates **16 analogue grey reference levels**,
  matching the 180's 16-shade spec
- **74HC4050** buffers the incoming signals, **74HC174** latches pixel data —
  the presence of 74HC logic confirms the 26-pin bus is **digital**, not analogue
  video
- **LM358** and factory-sealed trimmers set the reference ladder

So: the flex carries digital data, the panel generates 16 reference voltages
locally, and the source drivers select among them per pixel.

---

## 6. Verification method

The capture chain was proven rather than assumed:

1. Passive continuity mapping to identify ground and power pins
2. DC level measurement at idle
3. Dynamic classification via clock-ratio analysis — dot : line : frame ratios
   are far more reliable than absolute frequency estimates
4. Data-line identification through known test patterns
5. **Byte-exact verification:** two independent full-frame captures of a static
   screen, compared byte by byte → **zero differing bytes** across 128,000 bytes.
   With a quarter of a million bytes compared, any bit slip, sampling jitter,
   ground bounce or DMA overrun would have shown up.
6. Export as PGM and visual comparison against the internal panel — the 1-pixel
   checkerboard dithering of the System 7 desktop survives intact, which only
   happens if byte clock, sampling edge and nibble packing are all correct.
