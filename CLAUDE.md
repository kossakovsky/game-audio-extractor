# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Pipeline for extracting and transcribing Russian voice lines from The Witcher 3 `.w3speech` game files. Five sequential shell/Python scripts process GOG installer → extracted audio → standard WAV → text transcription.

## Running the Pipeline

All scripts use relative paths and must be run from the project root.

```bash
# Step 1: Unpack GOG installer (requires innoextract)
./scripts/01_unpack_installer.sh /path/to/installer.exe

# Step 2: Extract audio from .w3speech binary format
./scripts/02_extract_w3speech.py

# Step 3: Convert Wwise audio to standard WAV (requires vgmstream-cli)
./scripts/03_convert_audio.sh

# Step 4: Transcribe with Whisper (activate venv first)
source whisper_env/bin/activate
./scripts/04_transcribe.py

# Step 5: Copy selected files
./scripts/05_copy_files.sh selections.txt
```

## Architecture

- **No build system or tests** — this is a data-processing pipeline, not a library
- Scripts are numbered `01`–`05` and run sequentially; each reads from the previous step's output directory
- Data flows through: `data/raw/` → `data/extracted/` → `data/converted/` → `data/logs/`
- The `data/` directory is gitignored (contains large binary files)
- Python scripts use argparse with sensible defaults; shell scripts use positional args

## Key Technical Details

- **CPSW format**: `02_extract_w3speech.py` parses the Witcher 3 binary container format (magic bytes `CPSW`), using Bit6-encoded variable-length integers for entry counts
- **Language key**: `LANG_KEY = 0x42386347` (Russian); audio IDs are XOR'd with this key
- **Size guard**: The Python extractor guards against a C++ underflow bug where `size -= 12` can wrap unsigned integers
- **Incremental processing**: Both extraction (step 2) and transcription (step 4) skip already-processed files
- **Transcription log format**: TSV with columns `index`, `filename`, `size`, `text` — written to `data/logs/transcribe_log.txt`
- **File size filter**: Whisper transcription defaults to files ≤200 KB to skip music/ambient tracks

## Dependencies

- macOS-focused (Homebrew installs)
- `innoextract` — GOG .exe unpacking
- `vgmstream-cli` — Wwise audio conversion
- `openai-whisper==20240930` — speech-to-text (installed in `whisper_env` venv)

## Conventions

- Shell scripts use `set -euo pipefail`
- Python scripts have `#!/usr/bin/env python3` shebangs
- Output filenames are hex IDs: `0x{id:08x}.wav`
