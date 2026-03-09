#!/bin/bash
#
# Extract .w3speech files from a GOG installer executable using innoextract.
#

set -euo pipefail

usage() {
    echo "Usage: $(basename "$0") <installer.exe> [output_dir]"
    echo ""
    echo "Extract .w3speech files from a GOG Witcher 3 installer."
    echo ""
    echo "Arguments:"
    echo "  installer.exe   Path to GOG installer .exe file"
    echo "  output_dir      Output directory (default: data/raw)"
    echo ""
    echo "Requirements:"
    echo "  innoextract     Install via: brew install innoextract"
    exit "${1:-0}"
}

if [[ "${1:-}" == "--help" ]] || [[ "${1:-}" == "-h" ]]; then
    usage
fi

if [[ $# -lt 1 ]]; then
    usage 1
fi

INSTALLER="$1"
OUTPUT_DIR="${2:-data/raw}"

if ! command -v innoextract &>/dev/null; then
    echo "Error: innoextract not found. Install via: brew install innoextract"
    exit 1
fi

if [[ ! -f "$INSTALLER" ]]; then
    echo "Error: file not found: $INSTALLER"
    exit 1
fi

TEMP_DIR=$(mktemp -d)
trap 'rm -rf "$TEMP_DIR"' EXIT

echo "Extracting from: $INSTALLER"
innoextract -d "$TEMP_DIR" "$INSTALLER"

mkdir -p "$OUTPUT_DIR"

COUNT=0
while IFS= read -r -d '' f; do
    mv "$f" "$OUTPUT_DIR/"
    COUNT=$((COUNT + 1))
done < <(find "$TEMP_DIR" -name "*.w3speech" -print0)

if [[ $COUNT -eq 0 ]]; then
    echo "Warning: no .w3speech files found in installer"
else
    echo "Extracted $COUNT .w3speech file(s) to $OUTPUT_DIR"
fi
