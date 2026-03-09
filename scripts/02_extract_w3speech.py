#!/usr/bin/env python3
"""
Extract audio from Witcher 3 .w3speech files.

Parses the CPSW container format, decodes Bit6-encoded entry counts,
and extracts individual Wwise audio files (.wav).
"""

import argparse
import glob
import os
import struct
import sys

LANG_KEY = 0x42386347  # Russian
MAX_REASONABLE_SIZE = 50 * 1024 * 1024  # 50 MB


def read_bit6(f, byte_count):
    """Read a Bit6-encoded variable-length integer."""
    result = 0
    shift = 0
    for i in range(byte_count):
        b = struct.unpack("B", f.read(1))[0]
        if b == 128:
            return 0
        s = 6
        mask = 255
        if b > 127:
            mask = 127
            s = 7
        elif b > 63:
            if i == 0:
                mask = 63
        result = result | ((b & mask) << shift)
        shift += s
    return result


def find_item_count(f, file_size):
    """Determine Bit6 encoding length and entry count."""
    for bit_len in range(1, 20):
        f.seek(10)
        count = read_bit6(f, bit_len)
        if count == 0 or count > 100000:
            continue
        entry_data = f.read(40)
        if len(entry_data) < 40:
            continue
        values = struct.unpack("<10I", entry_data)
        offset = values[2] + 4
        if offset >= file_size:
            continue
        f.seek(offset)
        riff = f.read(4)
        if riff == b'RIFF':
            print(f"  Bit6 length: {bit_len}, entries: {count}")
            f.seek(10 + bit_len)
            return count
    return 0


def process_file(input_file, output_dir):
    """Extract audio entries from a single .w3speech file."""
    print(f"\n=== {os.path.basename(input_file)} ===")
    file_size = os.path.getsize(input_file)
    print(f"  Size: {file_size / (1024 * 1024):.1f} MB")

    existing = set(os.listdir(output_dir))

    with open(input_file, "rb") as f:
        magic = f.read(4)
        if magic != b'CPSW':
            print(f"  SKIP: invalid format ({magic})")
            return

        version = struct.unpack("<I", f.read(4))[0]
        key1 = struct.unpack("<H", f.read(2))[0]

        item_count = find_item_count(f, file_size)
        if item_count == 0:
            print("  SKIP: could not determine entry count")
            return

        entries = []
        for i in range(item_count):
            data = f.read(40)
            if len(data) < 40:
                break
            values = struct.unpack("<10I", data)
            raw_id = values[0]
            offset = values[2] + 4
            size = values[4]
            # Guard against C++ size overflow bug: size -= 12
            if size >= 12:
                size -= 12
            else:
                size = 0
            xored_id = raw_id ^ LANG_KEY
            entries.append({"id": xored_id, "offset": offset, "size": size})

        extracted = 0
        skipped = 0
        errors = 0
        bad_size = 0

        for e in entries:
            name = f"0x{e['id']:08x}.wav"
            if name in existing:
                skipped += 1
                continue
            if e["size"] == 0 or e["size"] > MAX_REASONABLE_SIZE:
                bad_size += 1
                continue
            if e["offset"] + e["size"] > file_size:
                errors += 1
                continue
            try:
                f.seek(e["offset"])
                audio_data = f.read(e["size"])
                out_path = os.path.join(output_dir, name)
                with open(out_path, "wb") as out:
                    out.write(audio_data)
                existing.add(name)
                extracted += 1
            except Exception:
                errors += 1

        print(f"  Extracted: {extracted}, skipped: {skipped}, bad size: {bad_size}, errors: {errors}")


def main():
    parser = argparse.ArgumentParser(
        description="Extract audio from Witcher 3 .w3speech files"
    )
    parser.add_argument(
        "-i", "--input-dir",
        default="data/raw",
        help="Directory containing .w3speech files (default: data/raw)",
    )
    parser.add_argument(
        "-o", "--output-dir",
        default="data/extracted",
        help="Output directory for extracted audio (default: data/extracted)",
    )
    parser.add_argument(
        "--pattern",
        default="rupc*.w3speech",
        help="Glob pattern for input files (default: rupc*.w3speech)",
    )
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    files = sorted(glob.glob(os.path.join(args.input_dir, args.pattern)))
    print(f"Found {len(files)} file(s)")

    for f in files:
        process_file(f, args.output_dir)

    total = len(os.listdir(args.output_dir))
    print(f"\nTotal files in {args.output_dir}: {total}")


if __name__ == "__main__":
    main()
