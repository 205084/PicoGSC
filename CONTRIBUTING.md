# Contributing

The most valuable contribution right now is **independent verification**.

If you have a PowerBook 160/165/180 and want to replicate this:

1. Follow [`docs/wiring.md`](docs/wiring.md) — the pinout there is from my own
   harness, so double-check against yours before soldering.
2. Flash the firmware, run `v` on a static screen. Zero CRC differences means
   your chain is good.
3. Run `s` and report the nibble histogram. **Especially interesting:** do you
   also see only 0/4/8/14, or do odd values appear? That would settle the open
   LSB question.

If you have a **160 or 165** (passive matrix FSTN rather than active matrix),
your numbers will likely differ — please report them anyway. The mode-dependent
FLM behaviour in particular deserves more data points.

## What would help most

- 5 V-side confirmation of the FPDATA0/FPDATA4 finding
- A real datasheet for the Chips & Technologies 65210
- FLM measurements in other colour-depth settings (1-bit, 2-bit)
- Confirmation of the frame geometry with the OS loaded (it was verified on the
  ROM boot screen; the OS mode is assumed identical but unverified)

## Reporting

Open an issue, or post in the
[68kMLA thread](https://68kmla.org/bb/threads/powerbook-reverse-engineering-for-fun-and-no-profit.52504/).
Please include which machine, which mode, and how you measured.

## Code

Firmware comments are currently in German; translation is welcome. Keep the
measured specification in `docs/gsc-bus.md` as the single source of truth —
if a number changes there, change it in the sketch header too.
