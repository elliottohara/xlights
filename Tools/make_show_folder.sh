#!/usr/bin/env bash
# Promote a sequence folder (<Show>/Sequences/<Song>/) into a standalone
# xLights show folder, so groups/views can be edited per sequence without
# touching the master layout.
#
#   Tools/make_show_folder.sh "Christmas/Sequences/Holy Forever 2026"
#   Tools/make_show_folder.sh "<seq dir>" --refresh-layout   # re-copy master rgbeffects
#
# What it does:
#   - Copies the show root's xlights_rgbeffects.xml into the sequence folder
#     (the per-sequence layout; never overwritten unless --refresh-layout).
#   - Relative-symlinks shared support files/folders back to the show root
#     (Faces, DownloadedFaces, ImportedMedia, Images, colorcurves, palettes,
#     valuecurves, mhpresets, networks, keybindings, effect presets) so they
#     stay in sync with the master and resolve in any git worktree.
#
# Idempotent: safe to re-run; existing files/links are left alone.
set -euo pipefail

SEQ_DIR="${1:-}"
REFRESH="${2:-}"

if [[ -z "$SEQ_DIR" ]]; then
  echo "Usage: $0 <sequence folder> [--refresh-layout]" >&2
  exit 1
fi

SEQ_DIR="$(cd "$SEQ_DIR" && pwd)"
SHOW_DIR="$(cd "$SEQ_DIR/../.." && pwd)"

if [[ "$(basename "$(dirname "$SEQ_DIR")")" != "Sequences" ]]; then
  echo "Error: expected <Show>/Sequences/<Song>, got: $SEQ_DIR" >&2
  exit 1
fi
if [[ ! -f "$SHOW_DIR/xlights_rgbeffects.xml" ]]; then
  echo "Error: no xlights_rgbeffects.xml in show root: $SHOW_DIR" >&2
  exit 1
fi

# Per-sequence layout copy (the one file that is allowed to diverge).
if [[ -f "$SEQ_DIR/xlights_rgbeffects.xml" && "$REFRESH" != "--refresh-layout" ]]; then
  echo "kept existing per-sequence layout (use --refresh-layout to re-copy master)"
else
  cp "$SHOW_DIR/xlights_rgbeffects.xml" "$SEQ_DIR/xlights_rgbeffects.xml"
  echo "copied master layout -> $SEQ_DIR/xlights_rgbeffects.xml"
fi

# Shared support assets: relative symlinks to the show root (../../ from the
# sequence folder). Relative so they resolve in every worktree slot.
SHARED=(
  Faces
  DownloadedFaces
  ImportedMedia
  Images
  colorcurves
  palettes
  valuecurves
  mhpresets
  xlights_networks.xml
  xlights_keybindings.xml
  xlights_effectpresets.json
)
for item in "${SHARED[@]}"; do
  src="$SHOW_DIR/$item"
  dst="$SEQ_DIR/$item"
  if [[ ! -e "$src" ]]; then
    continue
  fi
  if [[ -L "$dst" || -e "$dst" ]]; then
    echo "kept existing: $item"
  else
    ln -s "../../$item" "$dst"
    echo "linked: $item -> ../../$item"
  fi
done

echo
echo "Show folder ready: $SEQ_DIR"
echo "Launch (slot B example):"
echo "  open -n -a xLights --args -b -s \"$SEQ_DIR\""
