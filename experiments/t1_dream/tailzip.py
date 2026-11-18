"""Read only the LAST part of a deflated zip member by HTTP range requests.

Deflate cannot normally be entered mid-stream. Here we fetch the last C compressed
bytes of a member, search bit offsets for a valid deflate block start, and inflate
to the end of the member with a preset 32 KB dictionary. Back-references into the
unknown history give wrong bytes, so we inflate twice with two different
dictionaries: bytes that differ are "tainted" (depend on unknown history) and are
masked; bytes equal in both are exact. Because we inflate to the member's end, the
position of every output byte in the file is known exactly (usize - len(out)).

Stdlib + numpy only. Verified against a full download in method_check.py.
"""
import struct
import zlib

import numpy as np

from ziprange import _get

DICT_A = bytes(32768)
DICT_B = bytes([0xA5]) * 32768


def _shift(buf: bytes, bit: int) -> bytes:
    if bit == 0:
        return buf
    v = int.from_bytes(buf, "little") >> bit
    return v.to_bytes(len(buf), "little")


def _try(buf: bytes, k: int, bit: int, probe: int = 6000):
    """True if a deflate stream parses from bit offset 8k+bit for `probe` input bytes."""
    seg = _shift(buf[k:k + probe + 1], bit)[:probe]
    d = zlib.decompressobj(-15, zdict=DICT_A)
    try:
        out = d.decompress(seg)
    except zlib.error:
        return False
    if d.eof:
        return False
    return len(out) > probe * 0.8


def find_sync(buf: bytes, max_bytes: int = 200000):
    for k in range(min(max_bytes, len(buf) - 7000)):
        for bit in range(8):
            if _try(buf, k, bit, 600) and _try(buf, k, bit, 6000):
                return k, bit
    raise RuntimeError("no deflate block start found")


def _inflate(stream: bytes, zd: bytes) -> bytes:
    d = zlib.decompressobj(-15, zdict=zd)
    out = d.decompress(stream) + d.flush()
    if not d.eof:
        raise RuntimeError("stream did not reach end of member")
    return out


def member_data_range(url: str, offset: int, csize: int):
    """Absolute byte range [start, end] of the member's compressed data."""
    hdr = _get(url, offset, offset + 29)
    nl, el = struct.unpack("<HH", hdr[26:30])
    start = offset + 30 + nl + el
    return start, start + csize - 1


def read_tail(url: str, offset: int, csize: int, usize: int, need_bytes: int):
    """Return (pos0, data, tainted_mask, fetched) for the member's last bytes.

    data covers file bytes [pos0, usize). tainted_mask marks bytes that depend on
    unknown history. Fetches more if the clean part is shorter than need_bytes.
    """
    start, end = member_data_range(url, offset, csize)
    ratio = csize / usize
    c = int(need_bytes * ratio * 1.02) + 120_000
    fetched = 0
    while True:
        a = max(start, end - c + 1)
        buf = _get(url, a, end)
        fetched += len(buf)
        if a == start:  # whole member: plain inflate
            out = zlib.decompress(buf, -15)
            return 0, out, np.zeros(len(out), bool), fetched
        k, bit = find_sync(buf)
        stream = _shift(buf[k:], bit)
        oa, ob = _inflate(stream, DICT_A), _inflate(stream, DICT_B)
        assert len(oa) == len(ob)
        taint = np.frombuffer(oa, np.uint8) != np.frombuffer(ob, np.uint8)
        # first clean position after the last tainted byte is not required:
        # taint is per byte; callers mask tainted samples.
        last_taint = int(np.nonzero(taint)[0].max()) + 1 if taint.any() else 0
        if len(oa) - last_taint >= need_bytes or a == start:
            return usize - len(oa), oa, taint, fetched
        c = int(c * 1.5)


def parse_edf_header(h: bytes):
    ns = int(h[252:256])
    def field(off, width, n):
        return [h[off + i * width: off + (i + 1) * width].decode("ascii", "replace").strip() for i in range(n)]
    o = 256
    labels = field(o, 16, ns); o += 16 * ns
    o += 80 * ns  # transducer
    units = field(o, 8, ns); o += 8 * ns
    pmin = np.array(field(o, 8, ns), float); o += 8 * ns
    pmax = np.array(field(o, 8, ns), float); o += 8 * ns
    dmin = np.array(field(o, 8, ns), float); o += 8 * ns
    dmax = np.array(field(o, 8, ns), float); o += 8 * ns
    o += 80 * ns  # prefilter
    nsamp = np.array(field(o, 8, ns), int)
    return dict(ns=ns, nrec=int(h[236:244]), recdur=float(h[244:252]), hbytes=int(h[184:192]),
                labels=labels, units=units, nsamp=nsamp,
                gain=(pmax - pmin) / (dmax - dmin), offs=pmin - (pmax - pmin) / (dmax - dmin) * dmin)
