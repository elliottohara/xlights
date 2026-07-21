#!/usr/bin/env bash
# Scaffold a per-song folder under <Show>/Sequences/<Song Name>/.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../../../.." && pwd)"
SONG="${1:-}"
SHOW="${2:-Christmas}"

if [[ -z "$SONG" ]]; then
  echo "Usage: $0 \"Song Name 2026\" [Christmas|Halloween]" >&2
  exit 1
fi

SHOW_DIR="$ROOT/$SHOW"
SEQ_DIR="$SHOW_DIR/Sequences/$SONG"

if [[ ! -d "$SHOW_DIR" ]]; then
  echo "Error: show directory not found: $SHOW_DIR" >&2
  exit 1
fi

if [[ -e "$SEQ_DIR" ]]; then
  echo "Error: already exists: $SEQ_DIR" >&2
  exit 1
fi

mkdir -p \
  "$SEQ_DIR/Media/Images" \
  "$SEQ_DIR/Timing Templates" \
  "$SEQ_DIR/Tools" \
  "$SEQ_DIR/Backups"

cat > "$SEQ_DIR/AGENT NOTES.md" <<EOF
# ${SONG} — Sequence Agent Notes

Working notes for \`${SHOW}/Sequences/${SONG}/${SONG}.xsq\`. Read alongside the root \`AGENTS.md\`.

## Media

- Sequence media: \`${SHOW}/Sequences/${SONG}/Media/\` (lyric video / audio)
- Song images: \`${SHOW}/Sequences/${SONG}/Media/Images/\`

## Timing

- Song timing templates: \`${SHOW}/Sequences/${SONG}/Timing Templates/\`

## Tools

- Song scripts: \`${SHOW}/Sequences/${SONG}/Tools/\`
- Shared API client: \`Tools/xlights_api.py\` (import via \`sys.path\` to the repo \`Tools/\` folder)

## Session / status

- Scaffolded; sequence file not created yet.
EOF

# Keep empty dirs visible to git
touch \
  "$SEQ_DIR/Media/.gitkeep" \
  "$SEQ_DIR/Media/Images/.gitkeep" \
  "$SEQ_DIR/Timing Templates/.gitkeep" \
  "$SEQ_DIR/Tools/.gitkeep" \
  "$SEQ_DIR/Backups/.gitkeep"

# Make the sequence folder a standalone xLights show folder (per-sequence
# layout copy + symlinks to shared show-root assets).
"$ROOT/Tools/make_show_folder.sh" "$SEQ_DIR"

echo "Created: $SEQ_DIR"
echo "Next:"
echo "  1. Put media in: $SEQ_DIR/Media/"
echo "  2. Create ${SONG}.xsq via xLights API (save to that path)"
echo "  3. Keep notes in: $SEQ_DIR/AGENT NOTES.md"
