# PicoGSC — wiring protocol (rev 2)

Build instructions for the capture front-end: PowerBook 180 GSC bus →
2× 74LVC245A → Adafruit Feather RP2350.

> **Warning:** the PowerBook side is 5 V. Never connect it to the RP2350
> directly. The 245s are not optional.
>
> The inverter board carries **~400 V** on its output side and holds charge
> after power-off. Do not probe it. What you want is its *low-voltage supply
> input*, not its output.

---

## 0. Scope

| | |
|---|---|
| Signals | **13** — FPDATA[0..7] + CL2 + CL1 + FLM + M_F + DISP_BLANK |
| Level shifters | **2 × 74LVC245A** (16 channels, 3 spare) |
| Direction | **5 V → 3.3 V only**, A→B |
| Target | Adafruit Feather RP2350 HSTX |

Two chips are enough. You do not need a third.

---

## 1. Bill of materials

| Qty | Part | Note |
|---|---|---|
| 2 | 74LVC245A (DIP-20 for breadboard, TSSOP for PCB) | VCC = **3.3 V**, not 5 V |
| 2 | 100 nF X7R ceramic | **mandatory**, directly at pin 20/10 |
| 13 | 33 Ω resistor | optional, series on the B outputs |
| 1 | breadboard / perfboard | place it at the PowerBook connector |
| ≥4 | ground return wires | see section 6 |

---

## 2. 74LVC245A base wiring (both chips identical)

```
        ┌───────∪───────┐
  DIR ──┤ 1          20 ├── VCC   → 3.3 V
   A1 ──┤ 2          19 ├── /OE   → GND
   A2 ──┤ 3          18 ├── B1
   A3 ──┤ 4          17 ├── B2
   A4 ──┤ 5          16 ├── B3
   A5 ──┤ 6          15 ├── B4
   A6 ──┤ 7          14 ├── B5
   A7 ──┤ 8          13 ├── B6
   A8 ──┤ 9          12 ├── B7
  GND ──┤10          11 ├── B8
        └───────────────┘
```

| Pin | Signal | Connection |
|---|---|---|
| 1 | DIR | **3.3 V** → direction A→B |
| 19 | /OE | **GND** → permanently enabled |
| 20 | VCC | **3.3 V** from the Feather's 3V3 pin |
| 10 | GND | common ground |

**Note the B side runs backwards** — B1 is pin 18, B8 is pin 11.

**Unused pins:** unused **inputs (A)** → tie to **GND** (floating CMOS inputs
oscillate and draw current). Unused **outputs (B)** → leave **open**.

---

## 3. Chip 1 — data bus FPDATA[0..7]

| PB pin | Signal | → 245 A pin | 245 B pin → | Feather GPIO | Silkscreen |
|---|---|---|---|---|---|
| 12 | FPDATA0 | 2 (A1) | 18 (B1) | GP22 | **SCK** |
| 11 | FPDATA1 | 3 (A2) | 17 (B2) | GP23 | **MO** |
| 9 | FPDATA2 | 4 (A3) | 16 (B3) | GP24 | **D24** |
| 8 | FPDATA3 | 5 (A4) | 15 (B4) | GP25 | **D25** |
| 6 | FPDATA4 | 6 (A5) | 14 (B5) | GP26 | **A0** |
| 5 | FPDATA5 | 7 (A6) | 13 (B6) | GP27 | **A1** |
| 3 | FPDATA6 | 8 (A7) | 12 (B7) | GP28 | **A2** |
| 2 | FPDATA7 | 9 (A8) | 11 (B8) | GP29 | **A3** |

GP22–GP29 is the only contiguous 8-bit block fully broken out on the header
that avoids the HSTX peripheral. `in pins, 8` requires them to be consecutive.

> GP20–GP27 does *not* work: **GP21 drives the on-board NeoPixel** and is not
> available on the header.
>
> A0–A3 (GP26–29) are the ADC pins; as plain digital inputs they are fine.

---

## 4. Chip 2 — clock, sync and status

| PB pin | Signal | → 245 A pin | 245 B pin → | Feather GPIO | Silkscreen |
|---|---|---|---|---|---|
| 14 | CL2 (byte clock) | 2 (A1) | 18 (B1) | GP4 | **D4** |
| 16 | CL1 (line) | 3 (A2) | 17 (B2) | GP5 | **D5** |
| 18 | FLM (frame) | 4 (A3) | 16 (B3) | GP6 | **D6** |
| ___ | DISP_BLANK | 5 (A4) | 15 (B4) | GP9 | **D9** |
| ___ | M_F | 6 (A5) | 14 (B5) | GP0 | **TX** |
| — | — | 7–9 (A6–A8) → GND | 11–13 (B6–B8) open | — | — |

*PB pin numbers for DISP_BLANK and M_F: fill in from your own harness.*

**DISP_BLANK and M_F are deliberately not part of the PIO program.** They are
diagnostic only, polled by the CPU. DISP_BLANK is the data-valid line — it is
redundant on the boot screen (CL2 only clocks during the valid burst, and
320 × 400 comes out exact), but it is the one line that would tell you if that
assumption ever stops holding in another mode. M_F measured static high.

---

## 5. Blocked pins on the Feather

| GPIO | Why |
|---|---|
| **GP8** | PSRAM chip select. Never use as GPIO. |
| **GP12–GP19** | HSTX peripheral → TMDS lanes to the DVI adapter |
| **GP2 / GP3** | **DDC I²C** on the adapter board (monitor EDID). **No jumper** — permanently tied to the HDMI connector. |
| **GP11** | Hot Plug Detect on the adapter (jumper can be cut) |
| **GP10** | CEC on the adapter (jumper can be cut) |
| **GP21** | NeoPixel, not on the header |

Not everything goes through HSTX: GP12–19 carry the TMDS pairs, but the HDMI
side channels hang on GP2/GP3/GP10/GP11. Driving 15.7 MHz data into a connected
monitor's DDC lines is a bad idea electrically and for EMI — which is why the
data bus was moved to GP22–29 rather than cutting jumpers.

Free after this assignment: GP1 (RX), GP7 (D13, has the red #7 LED), GP20 (MI),
plus GP10/GP11 if you cut the jumpers.

---

## 6. Power and ground

**3.3 V** from the Feather's **3V3** pin to both 245s (pin 20 and pin 1/DIR).
The regulator supplies 500 mA peak; the two chips draw a few milliamps.

**Decoupling:** 100 nF **directly** between pin 20 and pin 10 of each chip,
short leads, not routed across the breadboard. With 8 lines switching
simultaneously at 15.7 MHz this is the difference between clean edges and mush.

**Ground — the single most important point:**

- PowerBook, both 245s, the Feather and the logic analyser need **one common
  ground**.
- **Not** a single ground wire for 13 signals. Use at least 4 returns,
  distributed *between* the signals in the harness.
- PowerBook ground sits on several pins (1, 4, 7 among others — verify with a
  continuity check).

**Geometry:** put the 245s **directly at the PowerBook connector**. The 5 V run
is the sensitive one; the 3.3 V side to the Feather may be longer.

**Optional:** 33 Ω in series on each B output (at the 245, not at the Feather)
damps reflections on flying leads.

---

## 7. Cable routing

At 15.7 MHz on flying leads, routing is not cosmetics — it is the most common
source of failure.

- Bundle the 8 data lines together, clock/sync as a **separate** bundle. CL2 has
  the fastest edges and couples the most — do not run it parallel to the data
  lines over the full length.
- Interleave grounds: at least every fourth conductor in the data bundle.
- **No long stubs.** Every branch to the logic analyser is a stub. Keep them
  short, tap at the 245's B pin rather than at the Feather end.
- Label while you plug, not afterwards.

---

## 8. PowerBook-side preparation

- **Strap STN_MODE (PB pin 23) to GND** → the machine initialises video even
  with **no panel connected**. This keeps the fragile original panel out of the
  test setup.
  STN_MODE does **not** go through a level shifter — it is an *input to* the
  GSC, i.e. the wrong direction for a unidirectional 245. It's just a wire to
  ground.

---

## 9. Pre-power checklist

- [ ] VCC of both 245s measures **3.3 V** — not 5 V
- [ ] Pin 1 (DIR) at 3.3 V, both chips
- [ ] Pin 19 (/OE) at GND, both chips
- [ ] 100 nF fitted on both chips, short leads
- [ ] Chip 2: A6–A8 (pins 7–9) to GND
- [ ] Chip 2: B6–B8 (pins 11–13) open
- [ ] B side verified **reversed** (B1 = pin 18!)
- [ ] Nothing wired to GP2, GP3, GP8, GP10, GP11
- [ ] GP12–19 unoccupied
- [ ] STN_MODE (PB 23) to GND
- [ ] Common ground: PB ↔ 245 ↔ Feather ↔ LA
- [ ] Continuity check on all 13 runs, PB pin → Feather pin (unpowered!)
- [ ] Short check, 3.3 V against GND

**First test:** power the Feather, PowerBook **off**. Then switch the PowerBook
on and check with the logic analyser that CL2 arrives on the B side at
~15.7 MHz with clean 3.3 V levels and no wild overshoot. Only then flash the
firmware.

Put the logic analyser on the **B side**, in 3.3 V mode — the 5 V side is
already characterised; what matters now is what the RP2350 actually sees, which
verifies the level shifter at the same time.

---

## 10. PIO note

The IN base is **GP22**. In PIO, the pin index of `WAIT ... PIN` is relative to
the IN base and wraps **modulo 32**. With base 22 that gives:

| Signal | GPIO | Arithmetic | PIO index |
|---|---|---|---|
| CL2 | GP4 | (22 + 14) mod 32 = 4 | **14** |
| CL1 | GP5 | (22 + 15) mod 32 = 5 | **15** |
| FLM | GP6 | (22 + 16) mod 32 = 6 | **16** |

GP4–GP6 sit outside the IN base block and must still be assigned to the PIO and
enabled as inputs. If capture never triggers, the sync index is the first thing
to check.
