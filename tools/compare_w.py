#!/usr/bin/env python3
import struct
from pathlib import Path
from tp_sha1 import expand_w

BLOCK = bytes.fromhex(
    "313233343536373839800000000000000000000000000000000000000000000000"
    "00000000000000000000000000000000000000000000000000000000000048000000"
)
block16 = [struct.unpack_from("<I", BLOCK, i)[0] for i in range(0, 64, 4)]
py_w = expand_w(block16)
print("py  W16-19", [f"{x:08X}" for x in py_w[16:20]])
# uni W16-19 from last unicorn run
print("uni W16-19", ["00000000", "00000048", "3433B208", "38373635"])
