# xLights Show Directory — Agent Notes

Knowledge gathered while building "Feliz Navidad 2026" and "Holy Forever 2026" (July 2026). Verified against the live layout; re-verify names with `Christmas/xlights_rgbeffects.xml` if the layout has changed since.

**Per-sequence notes:** each song lives under `Christmas/Sequences/<Song Name>/` with `AGENT NOTES.md` next to the `.xsq` (e.g. `Christmas/Sequences/Holy Forever 2026/AGENT NOTES.md`). Read it before editing that sequence; keep it updated after significant work. To scaffold a new song folder, use the project skill `.cursor/skills/setup-sequence/`.

## Parallel agent work — use git worktrees

**Do not pile concurrent agent work onto `main` in the primary checkout.** Multiple agents (or agent + human) editing the same working tree collide on branches, dirty files, and saves. For any non-trivial or parallel task, work in a **dedicated git worktree** so `main` stays free.

### Convention

- **Worktree root (sibling of this repo):** `/Users/elliott.ohara/xlights-worktrees/<branch-name>/`
- **Branch name:** short kebab-case task slug (e.g. `remove-marquees-holy-forever`, `holy-forever-intro-rebuild`).
- **Primary checkout** (`/Users/elliott.ohara/xlights`) stays on `main` for review, merges, and one-off reads — not for long-running agent edits.

### Create / switch / clean up

```bash
# From the primary repo
mkdir -p /Users/elliott.ohara/xlights-worktrees
git fetch origin   # if tracking remotes
git worktree add -b <branch-name> /Users/elliott.ohara/xlights-worktrees/<branch-name> main

# List / remove when the branch is merged or abandoned
git worktree list
git worktree remove /Users/elliott.ohara/xlights-worktrees/<branch-name>
# optional: git branch -d <branch-name>
```

Open the **worktree path** as the Cursor workspace for that agent (not the primary checkout). Record the branch + worktree path in the song's `AGENT NOTES.md` when the work is non-trivial.

### xLights / path caveats in a worktree

- Absolute paths in this file that point at `/Users/elliott.ohara/xlights/...` mean the **primary** tree. In a worktree, prefer paths under that worktree root (or resolve relative to the repo root) for sequence files, scripts, and `saveSequence` targets.
- Shared on-disk media outside git (e.g. large `ImportedMedia/`, `Audio/`, `Videos/`) may still live under the primary tree — symlink or pass the primary path when the worktree checkout does not contain the file.
- Only one xLights GUI/API session should own a given show directory at a time. Point `-s` at the worktree's `Christmas/` (or Halloween/) when sequencing from that worktree; do not have two agents drive the same open show folder.
- When the task finishes: merge/PR into `main`, update `AGENT NOTES.md` if needed, then remove the worktree.

## Directory layout

- **Show directory (Christmas):** `/Users/elliott.ohara/xlights/Christmas/` — layout only: `xlights_rgbeffects.xml`, `xlights_networks.xml`, faces, shared `ImportedMedia/`. **Do not** dump song files at this root.
- **Per-sequence folders:** `Christmas/Sequences/<Song Name>/` — `<Song Name>.xsq`, `AGENT NOTES.md`, `Media/` (lyric video + song images), `Timing Templates/`, `Tools/` (song scripts), optional `Backups/`.
- **Shared timing templates:** `/Users/elliott.ohara/xlights/Timing Templates/` — cross-show / reusable templates only. Song-specific templates live under that song's `Timing Templates/`.
- **Shared API tooling:** `/Users/elliott.ohara/xlights/Tools/xlights_api.py` (and other show-agnostic helpers). Song scripts import it via `sys.path` to this folder.
- **Audio:** `/Users/elliott.ohara/xlights/Audio/` (e.g. `01 Feliz Navidad.mp3`) when audio is shared; otherwise prefer `Sequences/<Song>/Media/`.
- **Canonical local root:** `/Users/elliott.ohara/xlights`. Older sequences may still reference `/Users/elliott.ohara/Documents/xlights/...`; that symlink currently points to `/Volumes/Personal-Drive/xlights`. Prefer the local repo path in new scripts, and check the share/symlink if legacy media fails to load (`fixallpaths.sh` documents the path conventions).
- **Halloween:** separate show directory at `/Users/elliott.ohara/xlights/Halloween/` (same `Sequences/<Song>/` convention when used).
- **Videos (legacy/shared):** `/Users/elliott.ohara/xlights/Videos/` — optional shared downloads; prefer song `Media/` for sequence media.

## YouTube downloads

If a user wants a YouTube video for the show, **do not invent a one-off download workflow**. Use the existing helper at the show root:

```bash
./yt2mp4.sh "https://www.youtube.com/watch?v=VIDEO_ID"
```

- Default output: `/Users/elliott.ohara/xlights/Videos/<video title>.mp4`
- For a sequence, pass that song's Media folder as the second arg:
  `./yt2mp4.sh "<url>" "/Users/elliott.ohara/xlights/Christmas/Sequences/<Song Name>/Media"`
- Optional other folders (e.g. `./Audio`):
  `./yt2mp4.sh "<url>" "/Users/elliott.ohara/xlights/Audio"`
- Requires `yt-dlp` and `ffmpeg` (`brew install yt-dlp ffmpeg`). Ask before installing if they are missing.
- Prefer song `Media/` for sequence media; use `Audio/` only when the user wants audio-only / audio-folder placement.

## xLights automation API — build sequences through it, don't write .xsq by hand

**Sequences are authored via the API** (survives xLights file-format changes). Full command reference: `documentation/xlDo Commands.txt` in the xLights repo. Use `Tools/xlights_api.py` (thin Python client).

- Launch attached to the GUI session (a headless shell launch will hang):
  `open -a xLights --args -a -s "/Users/elliott.ohara/xlights/Christmas"`
- The API is **HTTP POST** to `http://127.0.0.1:49913/xlDoAutomation` with a JSON body — not raw TCP.
  Example: `curl -s -X POST -d '{"cmd":"getVersion"}' http://127.0.0.1:49913/xlDoAutomation`
- On startup xLights runs a **blocking show-directory backup**. Poll `getVersion` until it responds.

### Sequence-authoring workflow (proven, see `Tools/feliz_navidad_2026.py`)

1. `newSequence` (`mediaFile`, `frameMS:25`, `force:"true"`) — response includes exact duration (`len` ms).
2. `importXLightsSequence` (`mapmethod:"auto"`, `importmedia:"false"`) with a timing-only template to bring in timing tracks — song templates live in `Christmas/Sequences/<Song>/Timing Templates/`; shared/reusable ones in root `Timing Templates/` (each template is an old sequence with all model effects stripped).
3. `addEffect` per effect: `{"cmd":"addEffect","target":"<element>","effect":"On","settings":"T_TEXTCTRL_Fadeout=.25","palette":"C_BUTTON_Palette1=#FF0000,C_CHECKBOX_Palette1=1","layer":0,"startTime":1000,"endTime":2000}`. Settings/palette use the same key=value strings as the .xsq EffectDB. Layers auto-create. ~1 ms per call.
4. `saveSequence` (`seq` = **full path**, else it saves relative to cwd), `renderAll`, `exportVideoPreview`.

### API quirks (learned the hard way)

- **Transient 503s** under rapid-fire addEffect — retry with backoff (client handles it).
- **Element names are trimmed** by the API: layout name `Arches - Top ` (trailing space) must be sent as `Arches - Top`.
- **addEffect fails (503) for elements not in the sequence's master view**, and there is no API to add display elements. The default master view here excludes some groups (notably `EFL Wings`, `Large Spiral Trees`, `Spinners`, individual `Rose Bush N`). Workaround: sequence their member models instead (see `EXPAND` in `Tools/feliz_navidad_2026.py`).
- **Submodels ARE addressable** as `Model/Submodel` (e.g. `Singing Bulb - Center/Base`) for `addEffect`/`getEffectIDs` — no wrapper group needed.
- **ALWAYS check a model's submodels FIRST** (in `xlights_rgbeffects.xml`) before resorting to per-pixel/custom-grid analysis to light part of a prop. If no submodel matches exactly, combine the nearest submodel with `B_CUSTOM_SubBuffer` (works because ranges-submodel node order is usually geographic — verify x-monotonicity). `GE Merry Christmas` now has a dedicated `Christ` ranges submodel (241 nodes through custom-grid x=262; `mas` starts at x=264), so use element `GE Merry Christmas/Christ` directly with no buffer.
- **NEVER edit effects with `setEffectSettings` — it corrupts them.** Verified in source (`SettingsMap::ParseJson`): it parses the settings param as `key:value` with values **whitespace-trimmed** (destroys the `Teddy ` face def → silently falls back to another def), and JSON-object params are **silently dropped** (dict settings/palette = no-op that still reports `worked:true`). Round-tripping `getEffectSettings` output back in re-defaults the effect. The only safe effect edit: **wipe the element** with `cloneModelEffects` (`source` = any effect-free element like `House`, `eraseModel:"true"`) **and re-add** via `addEffect`, whose `key=value` parser preserves values verbatim.
- **No API command deletes individual effects or timing tracks.** Timing tracks: GUI only (plan track names before importing). Effects, two workarounds:
  - Layer is entirely yours: `cloneModelEffects` wipe (true deletion). Note it only touches target layers up to the SOURCE's layer count — a 1-layer empty source (e.g. `House`) wipes layer 0 only, leaving deeper layers untouched.
  - Effect sits on a layer shared with originals (or on a deep layer): **"Off-park" it** — `setEffectSettings` with `name:"Off"` + shrink to a 25 ms slot inside a known-dark window (t<180 ms on Holy Forever). Off ignores settings, so the value-mangling doesn't matter; result is inert and invisible, and the stub row can be hand-deleted in the GUI later.
- **`importXLightsSequence` adds timing tracks by name; import each track ONCE.** Re-importing a template containing a track that already exists in the sequence risks duplicated marks — rebuild the template, but don't re-import existing tracks; add-only.
- `getEffectSettings` also reads **timing tracks** (marks come back as effects; `name` = the mark label) — useful for verifying imported timing.
- **Unknown commands can hang the HTTP request forever** (e.g. there is no `getTimings`). Always call with a timeout (`curl -m`).
- Other useful commands: `getModels`, `getViews`, `getEffectIDs`/`getEffectSettings`, `cloneModelEffects`, `checkSequence` (can hang for minutes — long timeout).
- Verifying API behavior from source: github `xLightsSequencer/xLights` — automation dispatch in `src-ui-wx/automation/xLightsAutomations.cpp`, effect/settings internals in `src-core/render/Effect.cpp` and `src-core/utils/UtilClasses.cpp`.
- Rendered comparison videos live in `/Users/elliott.ohara/xlights/RenderCompare/`.

### Lyric timing from scratch (proven on Holy Forever 2026)

When no lyric timing exists for a song, generate it (reference implementation: `Christmas/Sequences/Holy Forever 2026/Tools/`):

1. Extract audio with ffmpeg → **faster-whisper** (`medium`, int8, `word_timestamps=True`, **`vad_filter=False`** — VAD swallowed the sung vocal entirely; `condition_on_previous_text=False`). Runs in ~1 min on CPU.
2. Align hypothesis words to canonical lyrics (web-sourced) with Levenshtein + fuzzy similarity; interpolate unmatched words. **Clamp phrase starts to the sequence's human-placed section boundaries** — whisper drags sung phrase starts back into instrumental pads; word *ends* are trustworthy.
3. Break words into Preston Blair phonemes using xLights' own dictionaries at `/Applications/xLights.app/Contents/Resources/dictionaries/` (`standard_dictionary` = CMU format incl. contractions like `WE'LL`; `phoneme_mapping` = CMU→PB). Even-split phonemes across each word, snap everything to the frame (25 ms).
4. Write a timing-only template .xsq — each track is 3 layers: **phrases (contiguous, with empty-label gap fillers), words, phonemes** — then `importXLightsSequence` (`mapmethod:"auto"`, `importmedia:"false"`).
5. **Prefer per-voice tracks** (`Lyrics Lead` / `Lyrics Female` / `Lyrics Choir`) over one shared track: each singer's Faces effect can then only mouth its own lines, and a full-lyric track (`Lyrics 1`) is still handy for duet/backup blocks.

## Sequence file format notes (.xsq — read-only reference)

Reading existing sequences for analysis is fine (XML): `ColorPalettes`/`EffectDB` are deduped strings referenced by index, `ElementEffects` holds per-element `EffectLayer`s. Settings prefixes: `B_` = buffer, `C_` = color, `E_` = effect params, `T_` = transition/layer. Effects on the same element+layer must not overlap.

## Tools

- `Tools/xlights_api.py` — shared API client (launch/wait, new_sequence, import_timings, add_effect, save, render_all, export_video_preview).
- `Christmas/Sequences/Holy Forever 2026/Tools/` — Holy Forever build/choreography scripts + lyric-timing pipeline (whisper → alignment → phonemes → timing template) + face/casting helpers. Reference implementation for per-song tooling; see that sequence's `AGENT NOTES.md`.
- `Christmas/Sequences/Holy Forever 2026/Tools/holy_forever_2026_wind_intro.py` — historical wind-intro builder; **refuses to run** (intro was cleared; would undo the 2026-07-19 baseline).
- `Tools/vidstats.swift` — per-frame brightness/motion metrics + sample frames from exported preview videos (must run outside a sandbox for AVFoundation), if present.

## Layout: key models and groups (Christmas)

All names below verified in `xlights_rgbeffects.xml`. **Gotchas in bold.**

- **`Arches - Top ` has a trailing space.** `Arches - All` = Arch 1–4; also `Arches - Middle`, `Arches - Bottom` rows for cascades.
- **`Verts` is a subset of `House Outline`** (both contain the wall models House Left/Right, Wall - *, Garage*). Don't hit both simultaneously with solid effects or the walls double-render.
- **`Windows` contains the window matrices** (`Matrix-Garage Window/Window - Garage`, `Matrix - Downstairs Window/Window - Bedroom`, `Matrix - Entry/Window - Entry` submodels) plus `Window - Bottom Left`, `Window - Play Room`, `Front Door`. A Faces effect here paints outlines on the walls — the user hated that; keep Windows to a steady warm glow.
- **`Matrixes`** = the 3 window matrices + `Matrix - Lantana`. `Column Matrixes` = `Matrix - C1..C6` (on the porch columns). `Downstairs Matrixes` also exists.
- **`Colum Shrubs` includes Rose Bush 1–9** plus Shrub Left/Center/Right and Door Tree Left/Right. Solid static fills on it read as "solid red rose bushes" — the user wants motion there (marquee/twinkle).
- `Mini Trees` = `Mini Tree - 1..4` (individually addressable, each with `Mini Tree - N Star`) — great for beat-count 1-2-3-4 sequencing.
- `House Outline`, `Roof`: multi-segment groups with **non-geographic node order** — a SingleStrand chase looks like scattered streaks. Use Marquee with `B_CHOICE_BufferStyle=Single Line` for uniform motion.
- Other main groups: `Icicles GRP`, `Colums` (3 columns), `Canes`, `Large Spiral Trees` (12), `Mega Tree` + `Tree Topper`, `Tree - Oak`, `Toni - Flat Tree`, `Flakes GRP` (all Boscoyo + GE flakes), `EFL Wings`, `Yard Borders`, `Driveway`, `Floods GRP` (8 floods), `Reindeer and Santa` (deer + sleigh), `GE Merry Christmas` (text prop).
- Whole-scene groups: `Whole Scene`, `Whole Scene w Matrixes`, `Whole Scene Rosa Centered` — use only for short wow hits (user preference).

### Spinners and their submodel groups

Full spinner props: `GE Rosa Grande 1`, `GE Reel Max 1`, `GE Reel Max 2`, `GE Starlord 1`, `GE Starlord 2`, `GE Mini Grand Illusion`, `GE Flake N 1`, `GE Flake N 2`, `BMOAW Left/Right`.

The pro sequences never light a spinner whole — they sequence submodel groups (each ` GRP` spans that part across all fixtures of the type):

- Reel Max: `Arrows`, `Spokes`, `Chevron Rings`, `Chevrons`, `Arcs Even/Odd`, `Kites`, `Outer Triangles`, `Circles Inner/Outer`, `Bulbs` — e.g. `GE Reel Max Arrows GRP`.
- Starlord: `Plunger All/LG/SM`, `Spoke`, `Star`, `Z All/Left/Right`, `Feather Even/Odd`, `Cross`, `Diamond`, `Ribbon`, `Square`.
- Rosa Grande: `Web Spoke`, `Web Ring`, `Hook CW/CCW`, `Spoke`, `Ring`, `Ribbon`, `Snowflake Spoke`, `Torch Long Even/Odd`, `Torch Short Even/Odd`, `Feather Long/Short Even/Odd`, `Flower`, `Outer Ball`.
- Baby Grand Illusion (= GE Mini Grand Illusion): `Rings`, `Spokes`, `Spokes Even/Odd`, `Hook CW/CCW`, `Snowflake Spokes`.
- MOAW (= BMOAW): `Spokes`, `Diamonds`, `Sm Diamonds`, `Rings Even/Odd`, `Snowflake Spoke`, `Zig Zag`, `Swag`.
- Flakes: `Flakes Outline All GRP`, `Flakes Spokes All GRP`, `Flakes Arms GRP` (outline = glow base, spokes = hit target, arms = chase-out target).

Effective pattern (from Christmas Dubstep): slow base on spokes (Pinwheel), sparkle on rings (Twinkle/Spirals), and shockwave stabs on arrows/plungers/webs with `B_CHOICE_BufferStyle=Overlay - Scaled` and `T_TEXTCTRL_Fadeout=.2`, rotating across banks per musical hit.

### Singing faces (face definitions in rgbeffects)

`GE 8ft Snowman Singing` (def `8ft Snowman Singing`, state `Colored`), `EFL Teddy` (def `Teddy ` — trailing space, state `Teddy RedBow static`), `Toni - Penguin 1/2` (`Penguin v.1.1 - No Tongue`), `SingingTree` (`Tree`), `GE Grinch Talk` (`Grinch`), `GE Santa Singing` (`Santa Singing`, state `hat`), `Singing Bulb - Left/Center/Right` (`Boscoyo ChromaBulb Face`). Drive from a lyric timing track. Do NOT put the `Trees` face on `Windows` or `Colum Shrubs` (see gotchas above).

- **Face color rules** (verified in `FacesEffect.cpp`): with `CustomColors=1` the def's per-part colors win and the palette is ignored — but **empty part colors render WHITE**, so a CC=1 def with no colors set (Snowman, Santa) is effectively all-white. With `CustomColors=0` the checked palette colors map in order = **mouth, eyes, FaceOutline, FaceOutline2** (5th/6th = eyes-2/3 variants). Prefer palette colors over submodel effects for coloring face props — e.g. the ChromaBulbs' C9 look (white mouth/eyes, R/G/B glass = FaceOutline, amber base = FaceOutline2) is a single 4-color Faces palette.
- **EFL Teddy has two equivalent defs:** `Teddy ` (trailing space; forces brown mouth `#c16100`, blue/brown eyes) and `No Forced Colors` (identical node ranges, all colors empty → white). Mind the trailing-space landmine on `Teddy ` (`setEffectSettings` trims it and the effect falls back to `Hell Bear`, a Halloween def — another reason to only ever addEffect).
- **User preference (July 2026): white mouths/eyes on all singing faces EXCEPT Teddy**, who keeps his forced-color face (`Teddy ` def). White is already the default everywhere else (empty CC=1 colors render white; palette-driven defs get white palette slots); SingingTree's forced green outline is fine.
- Singing Bulb submodels are inconsistently named per prop (Center = `Base`+`Bulb`; L/R = `Bulb Stem`+`Bulb Outline`) — only relevant for non-face submodel effects.

## Timing tracks (reusable from old sequences on the same mp3)

Old `Christmas/Feliz Navidad.xsq` has (all aligned to `Audio/01 Feliz Navidad.mp3`):

- `Beat Count` — 451 marks labeled `1`–`4` (bar position). Bars = marks labeled `1`.
- `Beats` — 447 unlabeled beats.
- `Lyrics 1` — 3 layers: phrases / words / phonemes. Phrase labels identify sections ("Fay Lease Nav E Dad", "Pro Sparro…", "I want to wish you a merry Christmas…", "…from the bottom of my heart").
- `Strings` — 124 marks; short marks (≤800 ms) are individual string runs, **verses only**.
- `Horns` — 182 marks; short marks are individual horn stabs, **intro riff + choruses + outro**.

Instrument tracks are gold for musicality: map each horn stab / string run to a visual voice. Copy timing elements verbatim into new sequences rather than regenerating.

## Reusable media (in `Christmas/ImportedMedia/Nutcracker Christmas/`)

- **Videos** (dancing characters, used on window matrices): `_Dancing Claus.mp4` (crop L10 R90 T83 B10), `_Dancing Elf.mp4` (10/90/88/11), `_Santa Dance Line.mp4` (10/90/91/9), `Dancing Santa with light.mp4` (15/85/88/20), `_Dancing Nutcracker.mp4` (22/68/72/11), `_Dancing Ginger w Hat.mp4` (20/80/76/19), `_Santa with Elves Dancing.mp4` (no crop), plus bells/candy canes clips. Use `E_CHOICE_Video_DurationTreatment=Loop` to fit any window.
- **Shaders:** `Aurora.fs`, `Circle Tunnel.fs`, `Lightning Flash.fs`, `Voronoi Spiral Vortex.fs`.
- Reference these via the `/Users/elliott.ohara/xlights/...` path (symlinked) to match existing sequences.

## Style reference sequences (user's favorites)

**Deep-dive style report:** `Style References/XTREME SEQUENCES STYLE REPORT.md` — full analysis of all 18 purchased Xtreme Sequences vendor packages (`/Volumes/Personal-Drive/xlights/Imports/xS_*`): their submodel-group ("part bank") technique, Shockwave/SingleStrand recipes, buffer-style choices, layer-stack anatomy, and note-onset timing discipline. Read it before styling a new sequence; regenerate stats with `Tools/analyze_xtreme_sequences.py`.

`The Imperal March.xsq`, `Carol Of the Bells (Instramental).xsq`, `Christmas Every Day.xsq`, `Christmas Dubstep.xsq` — Dubstep is the gold standard. Its signature moves:

1. Submodel groups as separate instruments, heavily layered (4–6 layers per element).
2. Short (200–500 ms) Shockwave/On-shimmer hits over slow bases; `T_CHOICE_LayerMethod` unmask/min tricks; Warp with `T_CHECKBOX_Canvas=1`.
3. Videos on `Matrix - Entry` / `Matrix - Downstairs Window` / `Matrix-Garage Window`; shaders + warp on Mega Tree.
4. Full-display slams on downbeats for punch, dark valleys for contrast.

## User preferences (learned from feedback)

- No sloppy whole-scene effects except short wow hits. Traditional red/green/white/gold palette. Crisp beat-locked timing.
- Wants dynamic range: dark/calm verses vs. bright choruses, full-display color slams on accents.
- Dislikes: scattered per-segment chases on walls, face outlines on windows, vertical VU sweeps across window matrices, static solid fills on rose bushes.
- Values submodel detail, stacked effects, and effects that follow the actual instruments (horns/strings), not just the beat grid.
