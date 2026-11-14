#!/usr/bin/env python3
"""news-image-01 entry: "Five Pins on a Map".

An illustrated world map sums up Friday 13 November 2026 with one
glowing pin per story:

  * a microchip over North America - Nvidia chief executive
    Jensen Huang resigns and a Microsoft 365 outage follows the
    same technology world around the globe;
  * a dove over Europe - Europe wins a seat at the Ukraine
    peace talks;
  * a tanker over the Middle East - Iran says it hit a US radar
    in Bahrain as tankers are struck in the Strait of Hormuz;
  * a fleet over the western Pacific - Taiwan details China's
    large, unannounced naval drills;
  * a crowd over South America - Pope Leo greets record crowds
    in Peru.

The map ships in this repository as ``image.png``.  Running this
program validates the picture against the competition rules -
format, a 1 MiB byte ceiling and a 1024x1024 pixel ceiling - and
delivers it, untouched, as ``entry.png`` inside
``$MAKEFUN_OUTPUT_DIR``.  Nothing but the standard library.
"""

import hashlib
import os
import struct
import sys
import zlib
from pathlib import Path

LIMIT_BYTES = 1_048_576
LIMIT_SIDE = 1024

SIGNATURES = (
    (b"\x89PNG\r\n\x1a\n", "PNG"),
    (b"\xff\xd8\xff", "JPEG"),
)


def png_size(data):
    """Width and height from IHDR, with the chunk CRC verified."""
    if len(data) < 33:
        raise ValueError("truncated PNG")
    length, ctype = struct.unpack(">I", data[8:12])[0], data[12:16]
    if ctype != b"IHDR" or length != 13:
        raise ValueError("first chunk is not IHDR")
    body = data[16:29]
    (crc,) = struct.unpack(">I", data[29:33])
    if zlib.crc32(b"IHDR" + body) & 0xFFFFFFFF != crc:
        raise ValueError("IHDR CRC does not match")
    return struct.unpack(">II", body[0:8])


def jpeg_size(data):
    """Width and height from the first SOF marker segment."""
    pos = 2
    while pos + 4 <= len(data):
        if data[pos] != 0xFF:
            raise ValueError("bad JPEG marker")
        marker = data[pos + 1]
        if marker in (0xD8, 0xD9) or 0xD0 <= marker <= 0xD7:
            pos += 2
            continue
        (seg_len,) = struct.unpack(">H", data[pos + 2:pos + 4])
        if seg_len < 2 or pos + 2 + seg_len > len(data):
            raise ValueError("JPEG segment out of range")
        if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
            if seg_len < 7:
                raise ValueError("truncated frame header")
            height, width = struct.unpack(">HH", data[pos + 5:pos + 9])
            return width, height
        pos += 2 + seg_len
    raise ValueError("no SOF marker in JPEG")


READERS = {"PNG": png_size, "JPEG": jpeg_size}


def validate(data):
    """Return (format, width, height); raise ValueError if invalid."""
    if not data:
        raise ValueError("empty image")
    if len(data) > LIMIT_BYTES:
        raise ValueError("image is over the 1 MiB limit")
    for magic, name in SIGNATURES:
        if data.startswith(magic):
            width, height = READERS[name](data)
            break
    else:
        raise ValueError("unknown image format")
    if not (1 <= width <= LIMIT_SIDE and 1 <= height <= LIMIT_SIDE):
        raise ValueError("image is over the 1024x1024 limit")
    return name, width, height


def main():
    source = Path(__file__).resolve().parent / "image.png"
    if not source.is_file():
        print("error: image.png missing from the entry repo", file=sys.stderr)
        return 1

    data = source.read_bytes()
    try:
        kind, width, height = validate(data)
    except ValueError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 1

    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "entry.png"
    target.write_bytes(data)

    same = hashlib.sha256(target.read_bytes()).digest() == \
        hashlib.sha256(data).digest()
    if not same:
        print("error: output copy differs from the bundled image",
              file=sys.stderr)
        return 1

    print("wrote %s (%s, %dx%d, %d bytes)"
          % (target, kind, width, height, len(data)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
