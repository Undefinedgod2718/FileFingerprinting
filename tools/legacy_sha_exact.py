#!/usr/bin/env python3
"""Exact port of FUN_00401ef0 / 00401f30 / 00401fd0 / 00401ce0 (LE block words)."""
from __future__ import annotations

import struct
from pathlib import Path

MASK = 0xFFFFFFFF
GUI = "67972355 BD7D1290 86D9DB6B FB4F59C8 C3CEDDAD"


def rol(x: int, n: int) -> int:
    x &= MASK
    return ((x << n) | (x >> (32 - n))) & MASK


def sha1_compress(state: list[int]) -> None:
    w = list(state[7:23])
    for i in range(16, 80):
        w.append((w[i - 3] ^ w[i - 8] ^ w[i - 14] ^ w[i - 16]) & MASK)
        w[i] = rol(w[i], 1)

    a, b, c, d, e = state[0], state[1], state[2], state[3], state[4]
    for i in range(80):
        if i < 20:
            f = (b & c) | ((~b) & d)
            k = 0x5A827999
        elif i < 40:
            f = b ^ c ^ d
            k = 0x6ED9EBA1
        elif i < 60:
            f = (b & c) | (b & d) | (c & d)
            k = 0x8F1BBCDC
        else:
            f = b ^ c ^ d
            k = 0xCA62C1D6
        temp = (rol(a, 5) + f + e + k + w[i]) & MASK
        e, d, c, b, a = d, c, rol(b, 30), a, temp
    state[0] = (state[0] + a) & MASK
    state[1] = (state[1] + b) & MASK
    state[2] = (state[2] + c) & MASK
    state[3] = (state[3] + d) & MASK
    state[4] = (state[4] + e) & MASK


class TpSha1Context:
  """Layout: state[0..4], bitlen_lo[5], bitlen_hi[6], block_words[7..22] (64 bytes)."""

  def __init__(self) -> None:
      self.words = [0] * 23
      self.init()

  def init(self) -> None:
      self.words[0] = 0x67452301
      self.words[1] = 0xEFCDAB89
      self.words[2] = 0x98BADCFE
      self.words[3] = 0x10325476
      self.words[4] = 0xC3D2E1F0
      self.words[5] = 0
      self.words[6] = 0

  def _block_bytes(self) -> bytearray:
      b = bytearray(64)
      for i in range(16):
          struct.pack_into("<I", b, i * 4, self.words[7 + i] & MASK)
      return b

  def _set_block_from_bytes(self, data: bytes) -> None:
      for i in range(16):
          chunk = data[i * 4 : i * 4 + 4]
          if len(chunk) < 4:
              chunk = chunk + b"\x00" * (4 - len(chunk))
          self.words[7 + i] = struct.unpack("<I", chunk)[0]

  def update(self, data: bytes) -> None:
      offset = 0
      n = len(data)
      while offset < n:
          take = min(0x2000, n - offset)
          self._update_chunk(data[offset : offset + take])
          offset += take

  def _update_chunk(self, data: bytes) -> None:
      # FUN_00401f30 — tail always MOVSD from [EBX+0x1c], no append
      bit_add = len(data) * 8
      lo = self.words[5]
      hi = self.words[6]
      new_lo = (lo + bit_add) & MASK
      if new_lo < lo:
          hi = (hi + 1) & MASK
      self.words[5] = new_lo
      self.words[6] = (hi + (len(data) >> 29)) & MASK

      idx = 0
      n = len(data)
      if n > 0x3F:
          blocks = n >> 6
          rem = n - (blocks << 6)
          for _ in range(blocks):
              for i in range(16):
                  self.words[7 + i] = struct.unpack_from("<I", data, idx + i * 4)[0]
              sha1_compress(self.words)
              idx += 64
          data = data[idx:]
          n = rem

      if n > 0:
          buf = bytearray(64)
          buf[:n] = data
          for i in range(16):
              chunk = buf[i * 4 : i * 4 + 4]
              if len(chunk) < 4:
                  chunk = chunk + b"\x00" * (4 - len(chunk))
              self.words[7 + i] = struct.unpack("<I", chunk)[0]

  def finalize(self) -> list[int]:
      # FUN_00401fd0
      lo = self.words[5]
      hi = self.words[6]
      used = (lo >> 3) & 0x3F

      buf = bytearray(64)
      for i in range(16):
          struct.pack_into("<I", buf, i * 4, self.words[7 + i] & MASK)
      buf[used] = 0x80
      if used < 0x38:
          buf[used + 1 : 56] = b"\x00" * (55 - used)
      else:
          buf[used + 1 : 64] = b"\x00" * (63 - used)
          for i in range(16):
              self.words[7 + i] = struct.unpack_from("<I", buf, i * 4)[0]
          sha1_compress(self.words)
          for i in range(14):
              self.words[7 + i] = 0
          buf = bytearray(64)

      # length as native LE uint32 pair (not BE)
      struct.pack_into("<I", buf, 56, hi & MASK)
      struct.pack_into("<I", buf, 60, lo & MASK)
      for i in range(16):
          self.words[7 + i] = struct.unpack_from("<I", buf, i * 4)[0]
      sha1_compress(self.words)
      return self.words[0:5]

  def format_gui(self) -> str:
      return " ".join(f"{w:08X}" for w in self.finalize())


def main() -> None:
    raw = (Path(__file__).resolve().parent / "fixtures" / "digits.bin").read_bytes()
    ctx = TpSha1Context()
    ctx.update(raw)
    got = ctx.format_gui()
    print("tp exact port", got)
    print("gui golden   ", GUI)
    print("match", got == GUI)


if __name__ == "__main__":
    main()
