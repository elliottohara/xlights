# xLights Show Directory — Agent Notes

Knowledge gathered while building "Feliz Navidad 2026" and "Holy Forever 2026" (July 2026). Verified against the live layout; re-verify names with `Christmas/xlights_rgbeffects.xml` if the layout has changed since.

**Per-sequence notes:** sequences with agent history have a companion file next to the .xsq, named `<sequence> - AGENT NOTES.md` (e.g. `Christmas/Holy Forever 2026 - AGENT NOTES.md`). Read it before editing that sequence; keep it updated after significant work.

## Directory layout

- **Show directory (Christmas):** `/Users/elliott.ohara/xlights/Christmas/` — sequences (`.xsq`), `xlights_rgbeffects.xml` (models/groups/faces), `ImportedMedia/` (videos, shaders).
- **Audio:** `/Users/elliott.ohara/xlights/Audio/` (e.g. `01 Feliz Navidad.mp3`).
- **Old media paths:** many sequences reference `/Users/elliott.ohara/xlights/...`. A symlink makes them resolve: `/Users/elliott.ohara/xlights -> /Users/elliott.ohara/xlights`. If media fails to load, check this symlink first (`fixallpaths.sh` at the root documents the path conventions).
- **Halloween:** separate show directory at `/Users/elliott.ohara/xlights/Halloween/`.
- **Videos:** `/Users/elliott.ohara/xlights/Videos/` — matrix/background video media.

## YouTube downloads

If a user wants a YouTube video for the show, **do not invent a one-off download workflow**. Use the existing helper at the show root:

```bash
./yt2mp4.sh "https://www.youtube.com/watch?v=VIDEO_ID"
```

- Default output: `/Users/elliott.ohara/xlights/Videos/<video title>.mp4`
- Optional second arg for another folder (e.g. `./Audio`):
  `./yt2mp4.sh "<url>" "/Users/elliott.ohara/xlights/Audio"`
- Requires `yt-dlp` and `ffmpeg` (`brew install yt-dlp ffmpeg`). Ask before installing if they are missing.
- Prefer saving video media under `Videos/`; use `Audio/` only when the user wants audio-only / audio-folder placement.

## xLights automation API — build sequences through it, don't write .xsq by hand

**Sequences are authored via the API** (survives xLights file-format changes). Full command reference: `documentation/xlDo Commands.txt` in the xLights repo. Use `Tools/xlights_api.py` (thin Python client).

- Launch attached to the GUI session (a headless shell launch will hang):
  `open -a xLights --args -a -s "/Users/elliott.ohara/xlights/Christmas"`
- The API is **HTTP POST** to `http://127.0.0.1:49913/xlDoAutomation` with a JSON body — not raw TCP.
  Example: `curl -s -X POST -d '{"cmd":"getVersion"}' http://127.0.0.1:49913/xlDoAutomation`
- On startup xLights runs a **blocking show-directory backup** (slow on this network volume). Poll `getVersion` until it responds.

### Sequence-authoring workflow (proven, see `Tools/feliz_navidad_2026.py`)

1. `newSequence` (`mediaFile`, `frameMS:25`, `force:"true"`) — response includes exact duration (`len` ms).
2. `importXLightsSequence` (`mapmethod:"auto"`, `importmedia:"false"`) with a timing-only template to bring in timing tracks — templates live in `Timing Templates/` at the xlights root (shared across Christmas/Halloween/etc. shows; each template is an old sequence with all model effects stripped).
3. `addEffect` per effect: `{"cmd":"addEffect","target":"<element>","effect":"On","settings":"T_TEXTCTRL_Fadeout=.25","palette":"C_BUTTON_Palette1=#FF0000,C_CHECKBOX_Palette1=1","layer":0,"startTime":1000,"endTime":2000}`. Settings/palette use the same key=value strings as the .xsq EffectDB. Layers auto-create. ~1 ms per call.
4. `saveSequence` (`seq` = **full path**, else it saves relative to cwd), `renderAll`, `exportVideoPreview`.

### API quirks (learned the hard way)

- **Transient 503s** under rapid-fire addEffect — retry with backoff (client handles it).
- **Element names are trimmed** by the API: layout name `Arches - Top ` (trailing space) must be sent as `Arches - Top`.
- **addEffect fails (503) for elements not in the sequence's master view**, and there is no API to add display elements. The default master view here excludes some groups (notably `EFL Wings`, `Large Spiral Trees`, `Spinners`, individual `Rose Bush N`). Workaround: sequence their member models instead (see `EXPAND` in `Tools/feliz_navidad_2026.py`).
- **Submodels ARE addressable** as `Model/Submodel` (e.g. `Singing Bulb - Center/Base`) for `addEffect`/`getEffectIDs` — no wrapper group needed.
- **ALWAYS check a model's submodels FIRST** (in `xlights_rgbeffects.xml`) before resorting to per-pixel/custom-grid analysis to light part of a prop. If no submodel matches exactly, combine the nearest submodel with `B_CUSTOM_SubBuffer` (works because ranges-submodel node order is usually geographic — verify x-monotonicity). Example: `GE Merry Christmas` has submodels `Merry` + `Christmas`; "Christ" alone = element `GE Merry Christmas/Christmas` + `B_CUSTOM_SubBuffer=0.00x0.00x69.10x100.00` (left 69.1% of the horizontal-layout buffer ends exactly after the cursive t).
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

When no lyric timing exists for a song, generate it (reference implementation: `Tools/tmp_holy/`):

1. Extract audio with ffmpeg → **faster-whisper** (`medium`, int8, `word_timestamps=True`, **`vad_filter=False`** — VAD swallowed the sung vocal entirely; `condition_on_previous_text=False`). Runs in ~1 min on CPU.
2. Align hypothesis words to canonical lyrics (web-sourced) with Levenshtein + fuzzy similarity; interpolate unmatched words. **Clamp phrase starts to the sequence's human-placed section boundaries** — whisper drags sung phrase starts back into instrumental pads; word *ends* are trustworthy.
3. Break words into Preston Blair phonemes using xLights' own dictionaries at `/Applications/xLights.app/Contents/Resources/dictionaries/` (`standard_dictionary` = CMU format incl. contractions like `WE'LL`; `phoneme_mapping` = CMU→PB). Even-split phonemes across each word, snap everything to the frame (25 ms).
4. Write a timing-only template .xsq — each track is 3 layers: **phrases (contiguous, with empty-label gap fillers), words, phonemes** — then `importXLightsSequence` (`mapmethod:"auto"`, `importmedia:"false"`).
5. **Prefer per-voice tracks** (`Lyrics Lead` / `Lyrics Female` / `Lyrics Choir`) over one shared track: each singer's Faces effect can then only mouth its own lines, and a full-lyric track (`Lyrics 1`) is still handy for duet/backup blocks.

## Sequence file format notes (.xsq — read-only reference)

Reading existing sequences for analysis is fine (XML): `ColorPalettes`/`EffectDB` are deduped strings referenced by index, `ElementEffects` holds per-element `EffectLayer`s. Settings prefixes: `B_` = buffer, `C_` = color, `E_` = effect params, `T_` = transition/layer. Effects on the same element+layer must not overlap.

## Tools

- `Tools/xlights_api.py` — API client (launch/wait, new_sequence, import_timings, add_effect, save, render_all, export_video_preview).
- `Tools/feliz_navidad_2026.py` — full API-driven build of Feliz Navidad 2026: timing-mark loading, palette + effect-settings library (borrowed from the favorite sequences), choreography helpers (`add()`, `slam()`, `horn_stabs()`, `string_runs()`, verse/chorus functions), overlap validation, push loop. **Copy this as the starting point for any new sequence** — the top half is song-agnostic, the choreography half is per-song.
- `Tools/tmp_holy/` — the lyric-timing pipeline (whisper transcription → alignment → phoneme breakdown → timing template) plus the Holy Forever face/casting scripts. Despite the name it's kept as the reference implementation; see the Holy Forever sequence notes for what each script does.
- `Tools/holy_forever_2026_wind_intro.py` — bar-synced "swaying wind" intro build (phase-continuous Bars direction flips + marquee streams + spiral sway).
- `Tools/vidstats.swift` — per-frame brightness/motion metrics + sample frames from exported preview videos (must run outside a sandbox for AVFoundation).

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
