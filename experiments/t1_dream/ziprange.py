"""Read single members (or the first bytes of a member) from a remote zip by HTTP range requests.

Stdlib only. Used for Chennu 2016 (Cambridge repository) and DREAM Figshare packages.
    from ziprange import RemoteZip
    z = RemoteZip(url); z.members  -> {name: (method, csize, usize, header_offset)}
    z.read(name, max_out=None)     -> bytes (decompressed; stops after max_out bytes if given)
"""
import struct
import time
import urllib.request
import zlib

UA = {"User-Agent": "open-data-client/1.0"}


def _get(url, a, b, tries=4):
    for k in range(tries):
        try:
            req = urllib.request.Request(url, headers={**UA, "Range": f"bytes={a}-{b}"})
            with urllib.request.urlopen(req, timeout=120) as r:
                data = r.read()
                if r.status != 206 and not (a == 0 and len(data) == b + 1):
                    raise IOError(f"no range support: status {r.status}")
                if len(data) != b - a + 1:
                    raise IOError(f"short read {len(data)} of {b - a + 1}")
                return data
        except Exception:
            if k == tries - 1:
                raise
            time.sleep(3 * (k + 1))


def _size(url):
    req = urllib.request.Request(url, headers={**UA, "Range": "bytes=0-0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        cr = r.headers.get("Content-Range")
        return int(cr.split("/")[-1])


class RemoteZip:
    def __init__(self, url, size=None):
        self.url = url
        self.size = size or _size(url)
        tail = _get(url, max(0, self.size - 70000), self.size - 1)
        z64 = tail.rfind(b"PK\x06\x06")
        if z64 >= 0:
            cd_size, cd_off = struct.unpack("<QQ", tail[z64 + 40:z64 + 56])
        else:
            i = tail.rfind(b"PK\x05\x06")
            cd_size, cd_off = struct.unpack("<II", tail[i + 12:i + 20])
        cd = _get(url, cd_off, cd_off + cd_size - 1)
        self.members = {}
        p = 0
        while cd[p:p + 4] == b"PK\x01\x02":
            meth, = struct.unpack("<H", cd[p + 10:p + 12])
            csz, usz = struct.unpack("<II", cd[p + 20:p + 28])
            nl, el, cl = struct.unpack("<HHH", cd[p + 28:p + 34])
            off, = struct.unpack("<I", cd[p + 42:p + 46])
            name = cd[p + 46:p + 46 + nl].decode("utf-8", "replace")
            extra = cd[p + 46 + nl:p + 46 + nl + el]
            q = 0
            while q + 4 <= len(extra):
                hid, hl = struct.unpack("<HH", extra[q:q + 4])
                body, k = extra[q + 4:q + 4 + hl], 0
                if hid == 1:
                    if usz == 0xFFFFFFFF:
                        usz, = struct.unpack("<Q", body[k:k + 8]); k += 8
                    if csz == 0xFFFFFFFF:
                        csz, = struct.unpack("<Q", body[k:k + 8]); k += 8
                    if off == 0xFFFFFFFF:
                        off, = struct.unpack("<Q", body[k:k + 8]); k += 8
                q += 4 + hl
            self.members[name] = (meth, csz, usz, off)
            p += 46 + nl + el + cl
        self.bytes_fetched = 0

    def read(self, name, max_out=None, chunk=4 << 20):
        meth, csz, usz, off = self.members[name]
        hdr = _get(self.url, off, off + 29)
        nl, el = struct.unpack("<HH", hdr[26:30])
        start = off + 30 + nl + el
        end = start + csz - 1
        if meth == 0:
            stop = end if max_out is None else min(end, start + max_out - 1)
            data = _get(self.url, start, stop)
            self.bytes_fetched += len(data)
            return data
        d = zlib.decompressobj(-15)
        out = bytearray()
        pos = start
        while pos <= end:
            b = _get(self.url, pos, min(end, pos + chunk - 1))
            self.bytes_fetched += len(b)
            pos += len(b)
            out += d.decompress(b)
            if max_out is not None and len(out) >= max_out:
                return bytes(out[:max_out])
        out += d.flush()
        return bytes(out)
