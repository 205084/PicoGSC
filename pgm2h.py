#!/usr/bin/env python3
"""
pgm2h.py - convert a PicoGSC PGM capture into a C header for embedding.

Usage:  python3 pgm2h.py frame.pgm > frame_data.h

Produces a 128,000-byte array in the same 4bpp packed format the capture
buffer uses (high nibble = left pixel), so it can be blitted with the exact
same code path as a live frame. Useful for testing the output side without a
PowerBook attached.
"""
import sys, re

if len(sys.argv) < 2:
    sys.exit("usage: pgm2h.py <file.pgm>")

txt = open(sys.argv[1]).read()
body = re.sub(r'#.*', '', txt).split()

if body[0] != 'P2':
    sys.exit("not an ASCII PGM (P2) file")

w, h, maxv = int(body[1]), int(body[2]), int(body[3])
pix = [int(v) for v in body[4:]]

if (w, h) != (640, 400):
    sys.exit(f"expected 640x400, got {w}x{h}")
if len(pix) != w * h:
    sys.exit(f"expected {w*h} pixels, found {len(pix)}")
if maxv != 15:
    print(f"// warning: maxval is {maxv}, expected 15", file=sys.stderr)

packed = [(pix[i] << 4) | pix[i + 1] for i in range(0, len(pix), 2)]

print(f"// PicoGSC capture, {w}x{h}, 4bpp packed, high nibble first")
print("// raw bus values - QuickDraw polarity (high = dark)")
print(f"const unsigned char pb_frame[{len(packed)}] = {{")
for i in range(0, len(packed), 16):
    print("  " + ",".join(str(b) for b in packed[i:i+16]) + ",")
print("};")
