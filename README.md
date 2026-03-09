# Game Audio Extractor

Extract and transcribe Russian voice lines from The Witcher 3 game files.

## Pipeline Overview

```
GOG installer (.exe)
  → 01_unpack_installer.sh    → .w3speech files
  → 02_extract_w3speech.py    → Wwise audio (.wav)
  → 03_convert_audio.sh       → Standard WAV files
  → 04_transcribe.py          → Text transcription log
  → 05_copy_files.sh          → Copy selected files
```

## Dependencies

| Tool | Install | Purpose |
|------|---------|---------|
| Python 3 | — | Run extraction and transcription scripts |
| [innoextract](https://constexpr.org/innoextract/) | `brew install innoextract` | Unpack GOG installer .exe files |
| [vgmstream-cli](https://vgmstream.org/) | `brew install vgmstream` | Convert Wwise audio to standard WAV |
| [openai-whisper](https://github.com/openai/whisper) | `pip install -r requirements.txt` | Speech-to-text transcription |

## Setup

```bash
python3 -m venv whisper_env
source whisper_env/bin/activate
pip install -r requirements.txt
```

## Usage

All scripts use relative paths by default and should be run from the project root.

### Step 1: Unpack GOG installer

```bash
./scripts/01_unpack_installer.sh /path/to/installer.exe
# Extracts .w3speech files to data/raw/
```

If you already have `.w3speech` files, place them in `data/raw/` and skip this step.

### Step 2: Extract audio from .w3speech

```bash
./scripts/02_extract_w3speech.py
# Reads data/raw/rupc*.w3speech → outputs to data/extracted/

# Custom paths:
./scripts/02_extract_w3speech.py -i /path/to/input -o /path/to/output
```

### Step 3: Convert Wwise audio to WAV

```bash
./scripts/03_convert_audio.sh
# Reads data/extracted/ → outputs to data/converted/

# Custom paths:
./scripts/03_convert_audio.sh /path/to/input /path/to/output
```

### Step 4: Transcribe audio

```bash
source whisper_env/bin/activate
./scripts/04_transcribe.py
# Reads data/converted/ → writes to data/logs/transcribe_log.txt

# Options:
./scripts/04_transcribe.py --model large      # Use a different Whisper model
./scripts/04_transcribe.py --max-size 500      # Process files up to 500 KB
./scripts/04_transcribe.py --language en       # Transcribe English audio
```

The script is incremental — it skips files already present in the log.

### Step 5: Search and copy results

Search the transcription log:

```bash
grep -i 'keyword' data/logs/transcribe_log.txt
```

Copy specific files by name:

```bash
# Create a text file with one filename per line
echo "0x000ff9e1.wav" > my_selection.txt
echo "0x0010388c.wav" >> my_selection.txt

./scripts/05_copy_files.sh my_selection.txt
# Copies from data/converted/ to data/selected/
```

## Directory Structure

```
├── scripts/
│   ├── 01_unpack_installer.sh
│   ├── 02_extract_w3speech.py
│   ├── 03_convert_audio.sh
│   ├── 04_transcribe.py
│   └── 05_copy_files.sh
├── data/                        # (gitignored)
│   ├── raw/                     # .w3speech source files
│   ├── extracted/               # Wwise audio (pre-conversion)
│   ├── converted/               # Standard WAV files
│   └── logs/                    # Transcription logs
├── requirements.txt
└── .gitignore
```

## Known Issues

- **C++ size overflow**: The original C++ extractor (`w3speech_extractor`) has a size calculation bug where `size -= 12` can underflow. The Python extractor guards against this.
- **Large files**: Whisper transcription filters files by size (default 200 KB) to skip music and ambient tracks. Increase with `--max-size`.
- **Mac compatibility**: All tools are tested on macOS. Linux users may need to install `vgmstream-cli` from source.
