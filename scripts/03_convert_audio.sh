#!/bin/bash
#
# Convert extracted Wwise audio files to standard WAV using vgmstream-cli.
#

set -euo pipefail

usage() {
    echo "Usage: $(basename "$0") [input_dir] [output_dir]"
    echo ""
    echo "Convert Wwise .wav files to standard WAV format."
    echo ""
    echo "Arguments:"
    echo "  input_dir    Directory with extracted audio (default: data/extracted)"
    echo "  output_dir   Output directory for WAV files (default: data/converted)"
    echo ""
    echo "Requirements:"
    echo "  vgmstream-cli   Install via: brew install vgmstream"
    exit 0
}

if [[ "${1:-}" == "--help" ]] || [[ "${1:-}" == "-h" ]]; then
    usage
fi

INPUT_DIR="${1:-data/extracted}"
OUTPUT_DIR="${2:-data/converted}"

if ! command -v vgmstream-cli &>/dev/null; then
    echo "Error: vgmstream-cli not found. Install via: brew install vgmstream"
    exit 1
fi

mkdir -p "$OUTPUT_DIR"

TOTAL=$(ls "$INPUT_DIR"/*.wav 2>/dev/null | wc -l | tr -d ' ')
COUNT=0
ERRORS=0

echo "Converting $TOTAL files..."
echo ""

for f in "$INPUT_DIR"/*.wav; do
    COUNT=$((COUNT + 1))
    FILENAME=$(basename "$f")

    if vgmstream-cli -o "$OUTPUT_DIR/$FILENAME" "$f" > /dev/null 2>&1; then
        printf "\r[%d/%d] OK: %s" "$COUNT" "$TOTAL" "$FILENAME"
    else
        ERRORS=$((ERRORS + 1))
        printf "\r[%d/%d] ERROR: %s\n" "$COUNT" "$TOTAL" "$FILENAME"
    fi
done

echo ""
echo ""
echo "Done! Converted: $((COUNT - ERRORS)) of $TOTAL"
echo "Errors: $ERRORS"
echo "Output: $OUTPUT_DIR"
