#!/bin/bash
#
# Copy Roach (Плотва) audio files to the repository root.
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SRC_DIR="$REPO_ROOT/data/converted"
DEST_DIR="$REPO_ROOT"

FILES=(
    0x000ff9e1.wav  # Давай плотва!
    0x0010388c.wav  # Быстрее плотва!
    0x000ffa9d.wav  # Погоди, плотва!
    0x000ff8b6.wav  # Спокойной плотва!
    0x000ff8c4.wav  # Вперед, Платва!
    0x000ff9e9.wav  # Шевелись, Платва!
    0x00105044.wav  # Давай, Платва!
    0x000ffaa9.wav  # Платване так быстро!
    0x000fd754.wav  # Платва тебя догонит.
)

COPIED=0
MISSING=0

for f in "${FILES[@]}"; do
    if cp "$SRC_DIR/$f" "$DEST_DIR/$f" 2>/dev/null; then
        echo "OK: $f"
        COPIED=$((COPIED + 1))
    else
        echo "NOT FOUND: $f"
        MISSING=$((MISSING + 1))
    fi
done

echo ""
echo "Done. Copied: $COPIED, missing: $MISSING"
echo "Output: $DEST_DIR"
