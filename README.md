# PicoGSC

**Live video bridge from the Apple PowerBook 180's internal LCD bus to HDMI/DVI.**

PicoGSC taps the 26-pin panel interconnect of a PowerBook 180, captures the raw
GSC video bus with an RP2350, and outputs it as a standard DVI signal so a
1992 active-matrix PowerBook can drive a modern monitor, or eventually a modern
panel fitted into its own lid.

**Status: working prototype.** Capture is verified byte-exact. Live output runs
at ~22 fps and is being reworked for full frame rate.

<img width="1152" height="2048" alt="image" src="https://github.com/user-attachments/assets/2b9951cd-5671-4fa5-80e9-557577b88a03" />


---

## What's a GSC?

The **GSC (Gray Scale Controller)** is the display controller in the PowerBook
160/165/180 reportedly a **Chips & Technologies 65210**. It drives the panel
over a 26-pin flex cable with a parallel TTL interface (FPDATA[0..7], CL1, CL2,
FLM, M, DISP_BLANK).

Apple never published the electrical pinout or timing of that interface. The
Developer Note documents the GSC only at framebuffer level; the Service Source
covers part numbers. **Everything in this repository was measured**, not
transcribed see [`docs/gsc-bus.md`](docs/gsc-bus.md).

The earlier PowerBooks (100, 14x, 170) use a different chip, *Omaha2*, which is
already reasonably well understood by the community. The 16x/180 GSC was not.

---

## Measured bus specification

| Parameter | Value |
|---|---|
| Resolution | 640 × 400 |
| Colour depth | 4 bpp linear (not dual-scan) |
| Bytes per line | 320 (exact) |
| Lines per frame | 400 (exact), **no vertical blanking** |
| Framebuffer | 128,000 bytes |
| CL2 during burst | ~15.7 MHz (31.3344 MHz GSC oscillator ÷ 2) |
| CL2 line average | 13.06 MHz, burst ~20.4 µs |
| CL1 | ~40.8 kHz |
| FLM | **mode-dependent**: exactly 102 Hz on the ROM boot screen, 69.9 Hz with the OS loaded |
| Logic level | 5 V |
| M_F | static high (as measured) |
| Sampling edge | data valid on the **falling** CL2 edge (Sharp convention) |

### Findings

1. **Frame geometry confirmed end-to-end.** Two independent full-frame captures
   of a static screen compared byte-by-byte: **zero differing bytes**. The
   exported image is pixel-identical to the internal panel.

2. **Polarity follows QuickDraw.** A *higher* nibble value means *darker*. That
   is the correct convention from QuickDraw's perspective and the panel
   implements it faithfully — the inversion happens on the output side, not in
   the bus. PicoGSC handles this in the palette, so captured data stays raw.

3. **The nibble LSB never appears set** — across entire frames only the values
   0/4/8/14 occur, i.e. bit 0 of each nibble stays low.
   ⚠️ **Preliminary.** A 5 V-side check on FPDATA0/FPDATA4 to rule out a wiring
   fault on my end is still outstanding. If it holds, the 180's GSC drives
   effectively 8 grey levels in this mode.

---

## Hardware

| Qty | Part | Note |
|---|---|---|
| 1 | Adafruit Feather RP2350 (HSTX) | 8 MB PSRAM present but **unused** in v0.2 |
| 1 | Adafruit RP2350 22-pin FPC HSTX to DVI adapter | + 22-pin FPC cable |
| 2 | 74LVC245A | level shifter, **VCC = 3.3 V**, DIR high, /OE low |
| 2 | 100 nF X7R | decoupling, mandatory |
| — | wire, ≥4 ground returns | see wiring doc |

Full pin-by-pin build instructions: [`docs/wiring.md`](docs/wiring.md)

**A note on grounding:** at 15.7 MHz on flying leads, a single ground wire for
13 signals is the most common failure mode. Distribute several returns through
the bundle.

---

## Quick start

1. Arduino IDE with the [earlephilhower arduino-pico](https://github.com/earlephilhower/arduino-pico) core
   Board: *Adafruit Feather RP2350 HSTX* — **Upload Method: Picotool**
2. Library Manager → install **Adafruit DVI HSTX** (pulls in Adafruit GFX)
3. Open `firmware/picogsc/picogsc.ino`, flash it
4. Connect the DVI adapter, then a monitor. You should see the *no signal* screen.
5. Type `t` on the serial console → test pattern (grey wedge + 1 px checkerboard).
   This verifies palette and sharpness **without a PowerBook attached**.
6. Wire up the PowerBook per the wiring doc, power it on. The bridge switches to
   live automatically once FLM starts.

⚠️ The DVI library overclocks the RP2350 to 264 MHz simply by being included.
Do **not** enable PSRAM in this configuration — the resulting QMI clock exceeds
the APS6404 specification.

### Serial commands

| Key | Action |
|---|---|
| `c` | capture a single frame |
| `v` | verify: capture twice, compare CRCs (requires a static screen) |
| `s` | statistics + nibble histogram |
| `d` / `D` | hex dump, short / full |
| `l <n>` | dump line n as hex |
| `p` | export frame as ASCII PGM (raw bus values) |
| `n` | toggle nibble order |
| `e` | toggle sampling edge FALL/RISE |
| `i` | M_F / DISP_BLANK levels + rough FLM frequency |
| `t` | test pattern |
| `g` | bridge on/off |

The bridge runs standalone no PC required once flashed.

---

## Roadmap

- [x] Bus characterisation (logic analyser + scope)
- [x] Verified byte-exact frame capture
- [x] Live DVI output
- [ ] 5 V-side verification of the FPDATA0/FPDATA4 finding
- [ ] Dual-core rework — capture and blit currently run sequentially, which is
      what costs the frame rate, not bandwidth
- [ ] Triple buffering for the ~70 Hz → 60 Hz mismatch
- [ ] Custom PCB
- [ ] Passive/STN LCD Reverse Engineering & Support
- [ ] Optional kit with a modern panel for the original lid

---

## Related work

This project builds on the PowerBook reverse-engineering thread at
[68kMLA](https://68kmla.org/bb/threads/powerbook-reverse-engineering-for-fun-and-no-profit.52504/),
where much of the groundwork on the Omaha2-based machines was done by others.

---

## Licence

Code: MIT — see [LICENSE](LICENSE).
Documentation and measurements: free to use, attribution appreciated.

Hardware designs, once they exist, will be released under CERN-OHL.

---

*Note: comments inside the firmware are currently in German. Translation is on
the list — the documentation here is the authoritative reference.*
