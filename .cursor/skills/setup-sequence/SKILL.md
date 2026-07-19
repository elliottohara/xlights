---
name: setup-sequence
description: >-
  Scaffolds a per-song folder under Christmas/Sequences/<Song Name>/ (or another
  show directory) with .xsq placeholder path, AGENT NOTES.md, Media/, Timing
  Templates/, Tools/, and Backups/. Use when starting a new xLights sequence,
  setting up folders for a new song, or when the user asks to scaffold a sequence.
---

# Setup sequence folders

## Layout (required)

Every song gets its own folder under the show directory:

```
<Show>/Sequences/<Song Name>/
  <Song Name>.xsq          # created later via xLights API (optional placeholder note)
  AGENT NOTES.md
  Media/                   # lyric video, song images
  Media/Images/
  Timing Templates/        # song-specific timing .xsq templates
  Tools/                   # song scripts (import shared Tools/xlights_api.py)
  Backups/                 # local .xsq.bak-* copies
```

Show root (`Christmas/`) keeps layout only: `xlights_rgbeffects.xml`, networks, faces, shared `ImportedMedia/`.

Shared across songs:
- `/Users/elliott.ohara/xlights/Tools/xlights_api.py`
- `/Users/elliott.ohara/xlights/Timing Templates/` (reusable templates only)

## Workflow

1. Confirm **show** (default `Christmas`) and **exact song name** (matches the `.xsq` basename, e.g. `Holy Forever 2026`).
2. Run the scaffold script (do not invent a one-off mkdir tree):

```bash
"/Users/elliott.ohara/xlights/.cursor/skills/setup-sequence/scripts/setup_sequence.sh" \
  "Song Name 2026" \
  [Christmas|Halloween]
```

3. Tell the user the created path. Next steps (only if they ask / are starting the sequence now):
   - Download media into `Media/` via `./yt2mp4.sh "<url>" "<seq>/Media"` (see root `AGENTS.md`).
   - Create the `.xsq` through the xLights API (`newSequence` with `mediaFile` pointing at `Media/...`), saving to the full sequence path.
   - Put timing templates under `Timing Templates/`; song scripts under `Tools/` with:

```python
sys.path.insert(0, '/Users/elliott.ohara/xlights/Tools')
import xlights_api as x
```

4. Update root `AGENTS.md` only if the convention itself changes — not for every new song.
5. Read `AGENT NOTES.md` before editing an existing sequence; keep it updated after significant work.

## Do not

- Put new `.xsq` / song media / song scripts at the show root.
- Put song-specific timing templates in the root `Timing Templates/` folder.
- Create this skill scaffold under `~/.cursor/skills/` — it lives in this repo at `.cursor/skills/setup-sequence/`.
