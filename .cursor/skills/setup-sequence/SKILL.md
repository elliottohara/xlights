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

**Halloween override (October 18, 2026):** Halloween uses one show folder at
`/Users/elliott.ohara/xlights/Halloween`, governed by `show-folder-policy.json`.
Song folders contain `.xsq`, media, notes and tools; do not create layout/network
copies or launch xLights with a song folder. Song-specific groups, submodels and
face/state definitions live in the canonical Halloween layout with distinct
names where needed. The scaffold/helper recognizes this policy automatically.
The standalone-folder instructions below continue to apply to shows without
that policy, including Christmas.

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
  xlights_rgbeffects.xml   # per-sequence layout COPY (may diverge: groups/views)
  Faces@ DownloadedFaces@ ImportedMedia@ Images@ colorcurves@ palettes@
  valuecurves@ mhpresets@ xlights_networks.xml@ xlights_keybindings.xml@
  xlights_effectpresets.json@   # relative symlinks -> ../../ (show root)
```

**Each sequence folder is itself an xLights show folder** — launch xLights with `-s "<seq dir>"` and edit groups/views per song without touching the master layout. The scaffold script promotes it automatically (via `Tools/make_show_folder.sh`); run that script manually to promote a pre-existing sequence folder or `--refresh-layout` to re-copy the master layout.

Show root (`Christmas/`) keeps the master layout: `xlights_rgbeffects.xml`, networks, faces, shared `ImportedMedia/`.

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

## Display defaults for new sequences

The scaffold creates `Tools/sequence_defaults.json` and `Tools/finalize_sequence.py`.
After authoring/importing Projector effects and **before the final render**, apply
the defaults: Tune To mirrors the Projector's complete choreography and keeps
white `Tune to 87.9` visible on a black backing strip throughout the song.
The shared `xlights_api.render_all()` wrapper applies this automatically for
scaffolded songs. For direct `xl('renderAll')` calls, first run the generated
`Tools/finalize_sequence.py`, or call `Tools/apply_sequence_defaults.py <full xsq>`.
Reapply after changing Projector content; the helper replaces only Tune To and
is safe to repeat without accumulating cloned effects. Keep all other effects,
timings, controller assignments and the master layout intact.

The helper recognizes a direct Projector row or one imported group exclusively
targeting Projector. Multiple active Projector rows need an explicit source
selection. With no Projector choreography yet, the frequency remains visible;
reapply after adding that content. Missing Tune To hardware is a layout issue,
not permission to invent an output model. Verify both moving content and a
readable frequency in rendered sign pixels, including bright video frames.
Keep singers visible for the full song with resting mouths between lyrics.

## Do not

- Put new `.xsq` / song media / song scripts at the show root.
- Put song-specific timing templates in the root `Timing Templates/` folder.
- Create this skill scaffold under `~/.cursor/skills/` — it lives in this repo at `.cursor/skills/setup-sequence/`.
