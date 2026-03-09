#!/bin/bash
#
# Copy specific audio files from the converted directory to a destination.
# Reads file names from a list file (one filename per line).
#

set -euo pipefail

usage() {
    echo "Usage: $(basename "$0") <file_list> [source_dir] [dest_dir]"
    echo ""
    echo "Copy specific WAV files listed in a text file."
    echo ""
    echo "Arguments:"
    echo "  file_list    Text file with one filename per line"
    echo "  source_dir   Source directory (default: data/converted)"
    echo "  dest_dir     Destination directory (default: data/selected)"
    echo ""
    echo "Example:"
    echo "  $(basename "$0") my_files.txt"
    echo "  $(basename "$0") my_files.txt data/converted ~/output"
    exit "${1:-0}"
}

if [[ "${1:-}" == "--help" ]] || [[ "${1:-}" == "-h" ]]; then
    usage
fi

if [[ $# -lt 1 ]]; then
    usage 1
fi

FILE_LIST="$1"
SRC_DIR="${2:-data/converted}"
DEST_DIR="${3:-data/selected}"

if [[ ! -f "$FILE_LIST" ]]; then
    echo "Error: file list not found: $FILE_LIST"
    exit 1
fi

mkdir -p "$DEST_DIR"

COPIED=0
MISSING=0

while IFS= read -r f; do
    # Skip empty lines and comments
    [[ -z "$f" || "$f" == \#* ]] && continue

    if cp "$SRC_DIR/$f" "$DEST_DIR/$f" 2>/dev/null; then
        echo "OK: $f"
        COPIED=$((COPIED + 1))
    else
        echo "NOT FOUND: $f"
        MISSING=$((MISSING + 1))
    fi
done < "$FILE_LIST"

echo ""
echo "Done. Copied: $COPIED, missing: $MISSING"
echo "Output: $DEST_DIR"
