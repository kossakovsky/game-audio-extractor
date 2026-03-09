#!/usr/bin/env python3
"""
Transcribe WAV files using OpenAI Whisper.

Processes files incrementally — already-transcribed files (tracked in the log)
are skipped on subsequent runs.
"""

import argparse
import os
import warnings

warnings.filterwarnings("ignore", message="FP16 is not supported on CPU")


def main():
    parser = argparse.ArgumentParser(
        description="Transcribe WAV audio files using OpenAI Whisper"
    )
    parser.add_argument(
        "-i", "--input-dir",
        default="data/converted",
        help="Directory containing WAV files (default: data/converted)",
    )
    parser.add_argument(
        "-l", "--log-file",
        default="data/logs/transcribe_log.txt",
        help="Transcription log file (default: data/logs/transcribe_log.txt)",
    )
    parser.add_argument(
        "-m", "--model",
        default="medium",
        help="Whisper model to use (default: medium)",
    )
    parser.add_argument(
        "--max-size",
        type=int,
        default=200,
        help="Max file size in KB to process (default: 200)",
    )
    parser.add_argument(
        "--language",
        default="ru",
        help="Audio language code (default: ru)",
    )
    args = parser.parse_args()

    max_size_bytes = args.max_size * 1024

    # Load already-processed files from log
    processed = set()
    if os.path.exists(args.log_file):
        with open(args.log_file, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split("\t")
                if len(parts) >= 2 and not line.startswith("No"):
                    processed.add(parts[1])
        print(f"Already processed in log: {len(processed)} files")

    import whisper
    print(f"Loading Whisper model ({args.model})...")
    model = whisper.load_model(args.model)
    print("Model loaded!\n")

    # Collect files under size limit, excluding already processed
    files = []
    for f in os.listdir(args.input_dir):
        if f.endswith(".wav") and f not in processed:
            path = os.path.join(args.input_dir, f)
            size = os.path.getsize(path)
            if size <= max_size_bytes:
                files.append((f, path, size))

    files.sort(key=lambda x: x[2])

    total = len(files)
    print(f"New files to process: {total}\n")

    if total == 0:
        print("Nothing to process!")
        return

    os.makedirs(os.path.dirname(args.log_file), exist_ok=True)
    log = open(args.log_file, "a", encoding="utf-8")

    for i, (name, path, size) in enumerate(files, 1):
        try:
            result = model.transcribe(path, language=args.language)
            text = result["text"].strip()
        except Exception as e:
            text = f"[ERROR: {e}]"

        size_kb = size / 1024
        line = f"{len(processed) + i}\t{name}\t{size_kb:.1f} KB\t{text}"

        print(f"[{i}/{total}] {name} ({size_kb:.1f} KB): {text}")

        log.write(line + "\n")
        log.flush()

    log.close()
    print(f"\nDone! Log: {args.log_file}")
    print(f"Search example: grep -i 'keyword' {args.log_file}")


if __name__ == "__main__":
    main()
