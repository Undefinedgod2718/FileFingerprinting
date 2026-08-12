#!/usr/bin/env python3
import struct
from pathlib import Path

MASK = 0xFFFFFFFF
BLOCK = bytes.fromhex(
    "313233343536373839800000000000000000000000000000000000000000000000"
    "00000000000000000000000000000000000000000000000000000000000048000000"
)
block16 = [struct.unpack_from("<I", BLOCK, i)[0] for i in range(0, 64, 4)]
bitlen = 72


def get_w(w, i):
    if i == -2:
        return bitlen
    if i == -1:
        return 0
    return w[i] & MASK


w = [0, 0] + block16
for k in range(64):
    t = k + 14
    if t >= len(w):
        w.extend([0] * (t - len(w) + 1))
    w[t] = (get_w(w, k + 11) ^ get_w(w, k + 6) ^ get_w(w, k - 2) ^ get_w(w, k)) & MASK

for i in range(14, 26):
    print(i, f"{w[i]:08X}")
