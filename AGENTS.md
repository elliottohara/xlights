# xLights Show Directory — Agent Notes

## Latest Halloween playback deployment — October 18, 2026

- The garage batch is now fully deployed: all 24 active sequences (25 playback filenames) and 20 media files verified on Master and the projector. Complete remote checksums, matching sequence IDs/frame timing, and every projector frame were verified. Master stayed running and is idle; existing playlists and schedule are preserved. This supersedes earlier pending-render/deployment status notes.
- Latest evidence: `Halloween/garage-batch-upload-latest.json`; current manifest: `Halloween/current-show.json`. The concurrent rename to FPP-KULP-SELFIE-STATION changed only labels; render channel addresses were proved unchanged.

## Garage line on porch Genius port 8 — October 18, 2026

- User moved the existing cable to **GENIUS-PORCH / 192.168.0.9, port 8**. Preserve the original physical chain: **Garage Left Bottom (73 RGB pixels), then Wall - Garage Top (30 RGB pixels), 103 total**, WS2811 at 30%. Wall - Garage Top has `ModelChain=">Garage Left Bottom"`. Both props move together. The old center-shrub cleanup had stripped this chain; the user clarified it is physically installed.
- User explicitly allows channel moves and re-rendering. Native allocation places the line at Genius-relative channel 7018, with Wall - Garage Top at 7237. Genius allocation is now 11250 channels; following controllers moved by 30 channels. All affected controller outputs and Master routes were uploaded and read back. Falcon .249 test settings and oak tombstone split were preserved.
- This is the latest controller revision. **Master output service is stopped for layout testing; playback files still use the previous address generation and require fresh rendering/deployment before playback resumes.** Current layout authority remains the single Halloween root. The earlier single-show consolidation report documents the prior completed playback generation.
- Evidence, original chain source, original/current layouts, network and live hardware snapshots: `Halloween/garage-left-bottom-port8-latest.json` and its backup. Fresh native port maps: `physical-output-reference-after.json` in that backup. Garage Left Bottom and Wall - Garage Top were subsequently added back to House Outline, Verts and the All Pixels/Whole Scene families, including equivalent purchased-song mapping groups. All Pixels wrappers inherit the two props through their nested groups. Memberships were verified without changing routing or other model data; see `Halloween/garage-group-memberships-latest.json`. Re-rendering/deployment is still required before playback resumes.

## Current Halloween policy — October 18, 2026

- User approved replacing per-song show folders with **one Halloween show folder** at `/Users/elliott.ohara/xlights/Halloween`. Open xLights with that folder, then open songs under `Sequences/<Song>/`. The standalone-song instructions below continue to apply to Christmas only.
- `Halloween/xlights_rgbeffects.xml` and `xlights_networks.xml` are the single physical layout/routing authority. Song-specific mapping groups, submodels, faces, states and views are merged into that layout; conflicting definitions receive distinct song-qualified names, and sequence references follow them. Do not refresh songs from an old layout or launch an active Halloween song directory as its own show.
- `Halloween/show-folder-policy.json` prevents sequence scaffolding from creating new Halloween layout copies. Song folders retain their XSQ, media, import packages/maps, tools and notes. Original layouts/configs are preserved under the Single Halloween show backup.
- The user declared layout work finished and explicitly authorized consolidation, sequence repairs, rendering and uploading **everything**, including I Knew It I Knew You. This supersedes the older sequence-transfer pause and that song's prior upload exclusion. Check `Halloween/single-show-consolidation-latest.json` plus the backup progress files for actual completion; authorization is not evidence of successful upload.
- Preserve the Falcon `.249` 16 x 500-pixel test setup, hidden arches on `.205` ports 12/13, and the physically verified oak-controller tombstone split across `.253` ports 11/12. Floods and disconnected hidden flakes/bulbs stay removed.
- Native `checkSequence` closes the sequence in the installed build. Explicitly reopen before rendering. Native save makes show-local asset paths relative, XML-escapes ampersands in settings and adds empty master-view rows; compare resolved assets and authored effects rather than raw XML/ref indexes.

Knowledge gathered while building "Feliz Navidad 2026" and "Holy Forever 2026" (July 2026). Verified against the live layout; re-verify names with `Christmas/xlights_rgbeffects.xml` if the layout has changed since.

**Per-sequence notes:** each song lives under `Christmas/Sequences/<Song Name>/` with `AGENT NOTES.md` next to the `.xsq` (e.g. `Christmas/Sequences/Holy Forever 2026/AGENT NOTES.md`). Read it before editing that sequence; keep it updated after significant work. To scaffold a new song folder, use the project skill `.cursor/skills/setup-sequence/`.

## Per-sequence show folders

**Each sequence folder is a standalone xLights show folder** (since 2026-07-21): it holds its own **copy** of `xlights_rgbeffects.xml` plus relative symlinks (`../../`) to the shared show-root assets (`Faces`, `DownloadedFaces`, `ImportedMedia`, `Images`, `colorcurves`, `palettes`, `valuecurves`, `mhpresets`, `xlights_networks.xml`, `xlights_keybindings.xml`, `xlights_effectpresets.json`). Launch xLights with `-s "<seq folder>"` and edit groups/views/submodels **per sequence** — e.g. add song-specific groups or trim the master view — without touching the master layout.

- **Promote / refresh:** `Tools/make_show_folder.sh "<Show>/Sequences/<Song>"` (idempotent; symlinks and an existing per-sequence layout are kept). `--refresh-layout` re-copies the master `xlights_rgbeffects.xml` over the per-sequence copy — only do that if the song has no layout customizations worth keeping (it clobbers them). The setup-sequence skill promotes new song folders automatically.
- **Which layout is "the layout":** the show-root `Christmas/xlights_rgbeffects.xml` stays the master (user-owned, do-not-edit rule below still applies). The per-sequence copy is where sequence-specific group/view engineering happens — editing it via the xLights GUI/API when the user asks is fine; it diverges from the master by design and there is **no automatic sync** in either direction. If the user updates the master (new props etc.), older per-sequence copies won't have the change until refreshed/hand-merged — flag this rather than silently refreshing.
- **Slots now point at sequence folders, not `Christmas/`.** Launch example (slot B): `open -n -a xLights --args -b -s ".../slot-b/Christmas/Sequences/<Song>"`. Switching a slot to a different song = show-folder change = **kill + relaunch** that slot's instance (`changeShowFolder` doesn't stick). Expect the blocking startup backup on each relaunch; it now only backs up that sequence folder, so it's fast.
- The per-sequence `xlights_rgbeffects.xml` and the symlinks are **tracked in git**; xLights droppings in the sequence folder (`Backup/`, `RenderCache/`, `*.xbkp`, `*.fseq`) are already gitignored.
- The `.xsq`'s `mediaFile` and effect asset paths are absolute — unaffected by which show folder is open.

## Parallel agent work — two permanent worktree slots

**Do not pile concurrent agent work onto `main` in the primary checkout.** Multiple agents (or agent + human) editing the same working tree collide on branches, dirty files, and saves. Agent edits happen in one of **two permanent git worktree "slots"**, each bound for its lifetime to one xLights instance.

Why exactly two: xLights supports **at most two** concurrent instances with working automation APIs (verified in source, `src-ui-wx/automation/`) — the **A port 49913** (`-a` flag) and the **B port 49914** (`-b` flag). Port = 49912 + slot; no other ports are possible. A third instance silently runs with **no API at all** (on a failed bind, xLights flips A↔B, retries once, then gives up). So instead of one worktree per branch (which forced an xLights relaunch + show-dir change every task), the two slots are long-lived and **branches rotate through them**.

### The slots

| Slot | Worktree path | xLights port | Launch flags | API client |
|---|---|---|---|---|
| A | `/Users/elliott.ohara/xlights-worktrees/slot-a` | 49913 | `-a` | default |
| B | `/Users/elliott.ohara/xlights-worktrees/slot-b` | 49914 | `-b` (+ `open -n`) | `XLIGHTS_API_PORT=49914` |

- **Primary checkout** (`/Users/elliott.ohara/xlights`) stays on `main` for review, merges, and one-off reads. It does not run an agent's xLights session.
- The slot↔port pairing never changes. Slot A launches with `open -a xLights --args -a -s "<show folder>"`; slot B with `open -n -a xLights --args -b -s "<show folder>"` (the `-n` forces a second macOS instance; without it `open` just focuses the existing one). `Tools/xlights_api.py` handles both automatically — in slot B, export `XLIGHTS_API_PORT=49914` once at the top of the session and `launch()` adds `-n`/`-b` itself.
- **The show folder is the song's sequence folder** (see "Per-sequence show folders"), e.g. `-s ".../slot-b/Christmas/Sequences/Holy Forever 2026"`.
- **The xLights instance stays running across tasks on the same song.** Switching a slot to a different song is a show-folder change: kill that slot's instance and relaunch with the new song's sequence folder (the startup backup only covers the sequence folder now, so it's quick).
- Between tasks a slot **parks on a detached HEAD at `main`** (slots can't check out `main` itself — the primary holds it).

### Task start (in a slot)

1. Pick a free slot (its worktree is clean and no other agent is using its xLights instance). Open the **slot path** as the Cursor workspace.
2. `git status` must be clean; `git fetch` if tracking remotes, then branch off: `git switch -c <task-branch> main` (short kebab-case slug, e.g. `holy-forever-intro-rebuild`).
3. If the primary tree has uncommitted work the task needs (hand edits to the .xsq, notes), copy those files in and commit them as a baseline-snapshot first commit.
4. If xLights isn't already running for this slot, launch with this slot's flags and poll `getVersion`.
5. **Close before switching:** if the instance has a sequence open from a prior task, `closeSequence` BEFORE any `git switch`/checkout that rewrites the .xsq under it. Then `openSequence` and verify `getOpenSequence` returns the expected `len`/`media` (`openSequence` on a path outside the show folder silently opens a NEW empty sequence instead of failing).
6. Record the branch + slot in the song's `AGENT NOTES.md` when the work is non-trivial.

### Task wrap-up checklist (do this unprompted — don't make the user ask)

When the user approves the work (or asks to ship it):

1. Commit on the task branch (including an updated `AGENT NOTES.md`).
2. From the primary checkout: verify any leftover dirty files in primary match the branch's baseline snapshot (`cmp` against the snapshot commit), clean them, then `git merge --ff-only <task-branch>` into `main`.
3. `git push origin main`.
4. Re-park the slot: `closeSequence` in that slot's xLights, then in the slot `git switch --detach main` and delete the merged branch (`git branch -d <task-branch>`). Leave the xLights instance running for the next task.

### Slot / xLights caveats

- Absolute paths in this file that point at `/Users/elliott.ohara/xlights/...` mean the **primary** tree. In a slot, use paths under that slot root for sequence files, scripts, and `saveSequence` targets.
- **Only one xLights session per show directory.** Each slot's instance owns whatever folder it launched with (`-s`) — never point two instances at the same folder. Two slots can safely work the same song only via their separate worktree copies of that sequence folder.
- **Layout changes still need a relaunch.** `xlights_rgbeffects.xml` is read when the show folder opens; if a branch switch changes it, `kill -9` that slot's xLights pid and relaunch with the same flags (`changeShowFolder` does NOT work — replies OK but doesn't stick; AppleScript `quit` can wedge the app). Most tasks only touch the `.xsq` and don't need this.
- **Claim ports explicitly.** Preferences persist the last-used port (`xFadePort`, last-quit-wins), so always pass `-a`/`-b` on launch; never rely on the saved default.
- Both instances share the same preferences file (`LastDir` etc.) — cosmetic, but a bare `open -a xLights` may open the other slot's show dir. Always pass `-s`.
- Two simultaneous `renderAll`/`exportVideoPreview` runs compete for CPU — stagger heavy renders.
- When killing a wedged instance, `kill -9` the right pid: `pgrep -fl xLights` lists both; match by the `-s <show dir>` in `ps -p <pid> -o command=`, then relaunch and poll `getVersion`.
- Shared on-disk media outside git (legacy `/Users/elliott.ohara/Documents/xlights/...` paths, `/Volumes/Personal-Drive/xlights`) resolves identically from any slot — no per-slot setup needed.
- Legacy per-branch worktrees created under the old convention (e.g. `angels-cry-wings`, `pc1-star-ascent`) finish under the old rules: merge via primary, `git worktree remove`, delete the branch. New tasks use slots.

## Directory layout

- **Show directory (Christmas):** `/Users/elliott.ohara/xlights/Christmas/` — master layout only: `xlights_rgbeffects.xml`, `xlights_networks.xml`, faces, shared `ImportedMedia/`. **Do not** dump song files at this root.
- **Per-sequence folders:** `Christmas/Sequences/<Song Name>/` — `<Song Name>.xsq`, `AGENT NOTES.md`, `Media/` (lyric video + song images), `Timing Templates/`, `Tools/` (song scripts), optional `Backups/`, plus the per-sequence show-folder files (layout copy + shared-asset symlinks; see "Per-sequence show folders").
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

## xLights automation API — prefer the API for authoring; edit `.xsq` when the API can't

### Purchased sequence mapping (user requirement, 2026-10-15)

For any request to map a purchased sequence, create a new sequence on the user's current layout and use xLights **Import Effects / Map Effects** from the original ZIP/XSQZ (or its intact vendor show folder), with a saved `.xjmap`. Inspect the vendor's layout, groups, submodels, and sequencing roles; open its show folder when needed. Match similar physical props and corresponding submodels. Preserve the donor's effects, timing, layers, ordering, palettes, blending, and render styles through the native importer. Do not reconstruct the purchased sequence through batches of `addEffect`. Avoid collapsing independent vendor spinner families onto the same destination props. Adjust face definitions to the user's physical characters after import, and document genuinely unavailable props. Keep packaged media in the song's Media folder, retain the original package and map for reuse, render, and inspect the result before uploading. This applies to Something In The Way, Halfway To Hell, and future mapping requests.

**Add / build effects via the API** (survives xLights file-format changes). Full command reference: `documentation/xlDo Commands.txt` in the xLights repo. Use `Tools/xlights_api.py` (thin Python client).

**Deleting or surgically removing effects is fine as a direct `.xsq` edit** — the API has no delete command. Prefer that over inventing workarounds. Pattern: save session → `cp` backup → line-oriented edit (one `<Effect .../>` per line; see `Christmas/Sequences/Holy Forever 2026/Tools/clear_intro.py` and siblings) → close/reopen the sequence in xLights. If the deletion scope is unclear or risky, **stop, tell the user the problem, and ask for guidance** — do not Off-park, stub, or otherwise hack around it.

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
- **ALWAYS check a model's submodels FIRST** (in `xlights_rgbeffects.xml`) before resorting to per-pixel/custom-grid analysis to light part of a prop. If no submodel matches exactly, combine the nearest submodel with `B_CUSTOM_SubBuffer` (works because ranges-submodel node order is usually geographic — verify x-monotonicity). `GE Merry Christmas` has a dedicated `Christ` submodel — address it as `GE Merry Christmas/Christ` with no `B_CUSTOM_SubBuffer`.
- **The master layout file is user-owned.** Do **not** edit `Christmas/xlights_rgbeffects.xml` (or `xlights_networks.xml`) unless the user explicitly asks. The **per-sequence** layout copy (in the song's show folder) may be edited when the task calls for it — that's what it's for. In particular, never rewrite, regenerate, "fix," or restore `GE Merry Christmas/Christ` ranges from old notes/backups — the user hand-maintains that submodel (2026-07-20: multi-line custom-grid ranges, not the old flat 241-node list). Sequence work targets the element name only; leave the layout definition alone.
- **NEVER edit effects with `setEffectSettings` — it corrupts them.** Verified in source (`SettingsMap::ParseJson`): it parses the settings param as `key:value` with values **whitespace-trimmed** (destroys the `Teddy ` face def → silently falls back to another def), and JSON-object params are **silently dropped** (dict settings/palette = no-op that still reports `worked:true`). Round-tripping `getEffectSettings` output back in re-defaults the effect. To change an effect via the API: **wipe the element** with `cloneModelEffects` (`source` = any effect-free element like `House`, `eraseModel:"true"`) **and re-add** via `addEffect`, whose `key=value` parser preserves values verbatim. To remove effects: edit the `.xsq` directly (below) — do not Off-park or use `setEffectSettings` as a fake delete.
- **No API command deletes individual effects or timing tracks.** Timing tracks: GUI only (plan track names before importing). For effects:
  - **OK / preferred:** edit the `.xsq` directly (backup first; see `clear_intro.py` / `clear_*.py` in Holy Forever Tools). Selective, time-scoped, and deep-layer deletes are all legitimate this way.
  - **OK when the whole layer is yours:** `cloneModelEffects` wipe from an empty source. Note it only touches target layers up to the SOURCE's layer count — a 1-layer empty source (e.g. `House`) wipes layer 0 only.
  - **Not OK:** Off-parking, shrinking effects into dark windows, renaming to `Off`, or other API hacks that leave garbage in the sequence. If you are unsure what to delete or how far to go, **tell the user the problem and ask for guidance.**
- **`importXLightsSequence` adds timing tracks by name; import each track ONCE.** Re-importing a template containing a track that already exists in the sequence risks duplicated marks — rebuild the template, but don't re-import existing tracks; add-only.
- `getEffectSettings` also reads **timing tracks** (marks come back as effects; `name` = the mark label) — useful for verifying imported timing.
- **Unknown commands can hang the HTTP request forever** (e.g. there is no `getTimings`). Always call with a timeout (`curl -m`).
- **Effect names must match the UI spelling, spaces included:** `addEffect` with `"ColorWash"` fails (`worked:"false"`); it's `"Color Wash"`. On failure, suspect the name before the settings.
- **`renderAll`/`exportVideoPreview` can hang the whole API** if the export destination folder doesn't exist — `mkdir -p` output dirs (e.g. `RenderCompare/`) before exporting. A hung instance won't recover: `kill -9` + relaunch (see worktree section).
- **Part-bank submodel GRPs are in the master view** (verified 2026-07-19: `Canes`, `Mini Tree Stars`, `GE Rosa Grande * GRP`, `GE Starlord * GRP`, `GE Reel Max * GRP`, `GE Baby Grand Illusion * GRP`, `Flakes * GRP` all accept addEffect) even though their parent whole-prop groups (`Spinners` etc.) are not. Probe with `getEffectIDs` before assuming.
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

## Sequence file format notes (.xsq)

Reading sequences for analysis is fine (XML): `ColorPalettes`/`EffectDB` are deduped strings referenced by index, `ElementEffects` holds per-element `EffectLayer`s. Settings prefixes: `B_` = buffer, `C_` = color, `E_` = effect params, `T_` = transition/layer. Effects on the same element+layer must not overlap.

**Direct deletes are allowed** when the API can't do the job: remove `<Effect .../>` lines under `ElementEffects` (timing elements stay put). Always backup first; prefer a small script with `--dry-run` over ad-hoc edits. Do not invent new EffectDB/palette indices by hand when authoring — use `addEffect` for that.

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
- Other main groups: `Icicles GRP`, `Colums` (3 columns), `Canes`, `Large Spiral Trees` (12), `Mega Tree` + `Tree Topper`, `Tree - Oak`, `Toni - Flat Tree`, `Flakes GRP` (all Boscoyo + GE flakes), `EFL Wings`, `Yard Borders`, `Driveway`, `Floods GRP` (8 floods), `Reindeer and Santa` (deer + sleigh), `GE Merry Christmas` (text prop; submodels `Merry` / `Christmas` / **`Christ`** — use `Christ` for the word Christ; **do not edit its node map**).
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
- **Hard Penguin color rule (user, 2026-07-19): never color/cover the outside of `Toni - Penguin 1/2`; only their bellies may carry color.** With `Penguin v.1.1 - No Tongue`, keep palette slots 1–3 white (mouth, eyes/wings, body/feet) and put any accent only in slot 4 (`FaceOutline2` = Belly).
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

**Xtreme-style playbook (READ BEFORE SEQUENCING A NEW SONG):** `Style References/XTREME SEQUENCES STYLE REPORT.md` — step-by-step guide for building sequences in the Xtreme Sequences style on this layout: song-type budgets, per-instrument timing first, matrix-first planning, element casting, part-bank choreography (Starlord/Rosa/Baby Grand A-list), layer architecture, exact Shockwave/SingleStrand settings recipes, dynamics rules. Derived from 18 vendor packages + 38 Xtreme sequences mapped onto this layout (~187k effects analyzed); evidence in its appendices. Regenerate stats with `Tools/analyze_xtreme_sequences.py`. **⚠ For any "make it Xtreme" request, render/buffer style is the whole game — read that report's "INSPECT RENDER STYLES FIRST" section and pull the pros' actual `B_CHOICE_BufferStyle`/`BufferTransform` strings from the share's `.xsq` files for the exact banks you're sequencing before writing effects (Per Model Per Preview + 2D camera for geometry-aware pinwheels, Flip-Horizontal mirror pairs, Vertical Per Model/Strand for per-part drips).**

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

## Additional user preference — October 17, 2026

- **Singing props are singing-only (user, 2026-10-17):** exclude physical singers and their submodels from decorative effects and all whole-scene/outline/accent mapping groups. Keep lyric-driven Faces effects on them. **Latest user correction: leave the singers visible all the time, with resting mouths between lyrics; do not suppress them when not singing.** Keep their Faces effects across the full song without fades that switch them off. Do not animate their outlines as musical accents.

## User workflow override — October 17, 2026

For ordinary Halloween work, work directly in `/Users/elliott.ohara/xlights/Halloween`, including its xLights show folder. Use worktree slots only for substantial parallel/multithreaded work. This explicit user preference overrides the earlier mandatory-slot convention for ordinary Halloween tasks.

## New-sequence display defaults — October 17, 2026

- **Tune To mirrors Projector, with the radio frequency overlaid (user requirement):** for every new sequence, copy the Projector's complete native effect stack onto `Tune To`, preserving timing, media, layers, palettes and blending. Keep white `Tune to 87.9` legible on a black backing strip for the entire song. Do not replace projector motion with a static sign or allow bright content to hide the frequency.
- The setup-sequence scaffold creates `Tools/sequence_defaults.json` and `Tools/finalize_sequence.py`. Shared `Tools/xlights_api.py::render_all()` applies the defaults automatically for scaffolded songs; before a direct `xl('renderAll')`, run the generated finalizer or `python3 Tools/apply_sequence_defaults.py "<full xsq path>"`. Reapply after changing Projector effects. Use native importXLightsSequence and addEffect; never setEffectSettings. The helper backs up and replaces only Tune To, handles imported Projector-only groups, and avoids duplicate layers on reruns. **Do not use cloneModelEffects for repeated applications across close/reopen:** this build's CloneXLightsEffects implementation has a function-static source pointer that becomes stale; a later copy can silently use another element. The shared helper uses a saved snapshot and native map instead.
- Check rendered sign pixels for both motion and readable frequency, including bright frames. Keep singers continuously visible with resting mouths, and include the full roof ridges/peaks when mapping roof outline choreography.

## Falcon 1602 test controller — October 18, 2026

- User designated **FALON-16V3-02 / Falcon 1602**, the F16V3 at **192.168.0.249**, as a test controller. This is NOT the inactive `Falcon-16V4-02` at 192.168.254.100.
- Physical controller now has exactly **500 WS2811 RGB pixels on each of its 16 local ports** (8,000 total), descriptions `TEST Port 1` through `TEST Port 16`, forward direction, group 1, no nulls, no zigzag, no gamma, and the prior 30% brightness. DDP base remains 176731; starts advance by 1500 channels per port. These are test ranges on this controller, not assignments of neighboring controllers' props.
- User said the old props do not belong on it and will supply destinations. Hardware labels/strings were replaced; **xLights model/controller assignments have not yet been changed** while that scope/destination is pending. Do not upload the old xLights port map to 192.168.0.249 or run a broad controller-upload/deployment that overwrites the test setup. Do not relocate these props by guessing.
- Old xLights assignments awaiting the user's direction: Column Left; Flood Column Left; Flood Column Right; Flood House Left; Flood House Right; Flood Tree; GE Grinch Talk (already inactive); House Left. Preserve their models and effects.
- Before/after hardware XML, complete recoverable controller settings, master/per-song layout copies and master output routing snapshot: `Halloween/Backups/Falcon 1602 test controller 20261018-114928/`. Evidence and old assignments: `Halloween/falcon1602-test-controller-latest.json`. Hardware readback verified all 16 counts, labels, starts and unchanged brightness; UI reloaded and confirmed. This conversion did not alter xLights channels, layouts, sequences, show playback, playlists, schedules, or other controllers. Built-in test patterns were not enabled automatically.

## Column Left physical location — October 18, 2026

- Final user correction: **Column Left is on FPP-KULP16-01 / Kulp 1601, port 14, at 192.168.0.253**, the oak-tree controller. The earlier statement of port 16 was corrected by the user. Evil Clown remains on port 16; do not displace it.
- Column Left has 66 pixels (24 top + 21 each side), 30% brightness. Its previous Falcon 1602 port 12 assignment is wrong. Falcon 1602 retains its physical 16 x 500-pixel test setup.
- User explicitly said channel preservation is unnecessary and re-rendering is allowed. xLights native automatic allocation moved Column Left to port 14 and repacked the affected ranges. Do not reuse an occupied/inactive-model channel range or extend a controller into another controller's allocation by hand. Native allocation/backups/render/deployment progress: `Halloween/column-left-port14-native-latest.json` and its backup directory.
- Updated routing is propagated to current standalone song layouts with their custom groups, submodels and effects preserved. The superseded original `Thriller` folder remains historical; active playback uses `Thriller Xtreme Remap`. That replacement has its own controller-network file, which must also be synchronized for routing changes.
- Re-render/deployment progress is recorded separately; do not assume hardware or playback uploads completed merely because the layout changed. I Knew It I Knew You remains unapproved for live upload unless the user explicitly approves it.

- Current port-14 revision status: all 24 current sequences re-rendered and checked locally; the new xLights assignment is saved. Automatic approval review rejected the separate live deployment (service stop plus production file replacement) until the user explicitly approves it. Live hardware outputs, playback files, schedule, playlist and idle service state are unchanged. Removed only this task's disposable remote staging copies to recover disk space; every new render and the staged routing plan remain local. On approval, use verified local recovery copies and per-file replacement rather than holding two complete show generations on the nearly-full FPP storage.

## House Left after bottom-left window — October 18, 2026

- User confirmed **House Left is connected to FPP-KULP08-FrontPorch / 192.168.0.250, port 3, immediately after Window - Bottom Left**. Order: 134 window pixels, then 86 House Left pixels. House Left stays RGB/WS2811, forward, at 30% brightness, with no null pixels. It no longer belongs on Falcon 1602 port 16.
- Native allocation verified `ModelChain=">Window - Bottom Left"`, House Left start channel 172495, and port 3 total 220 pixels. Apply routing changes to standalone layouts while preserving song-specific groups, views, geometry, submodels and effects. The superseded original Thriller remains historical; current playback uses Thriller Xtreme Remap, whose separate network copy also needs synchronization.
- Current progress, recoverable layouts/renders, full local live-playback recovery copies, and hardware deployment/readback status: `Halloween/house-left-porch-port3-latest.json` and its backup directory. Do not infer hardware deployment from layout changes or completed renders alone. Preserve Falcon 1602's physical 16 x 500-pixel test setup and do not upload the obsolete xLights Falcon map. I Knew It I Knew You remains excluded from live upload.
- In this installed xLights build, the attempted `setModelProperty` Controller/port calls returned success without reliably editing the intended model. Those unsaved changes were discarded. This correction used a backed-up routing-only layout edit followed by reopening xLights for native allocation and checking the actual model/port map. Always verify actual assignments after property API calls.
- **Controller testing comes first (user correction, 2026-10-18): upload controller outputs and let the user verify the physical lights before sending sequences. Do not resume sequence transfers until the user finishes testing and authorizes them.** The earlier transfer was interrupted partway through; six playback replacements were confirmed and a seventh rename was in flight. Complete recovery copies and per-file progress are in the House Left backup. Master FPP output service is intentionally stopped while the user tests with xLights/controller tests; do not start playback against the mixed old/new playback files.


## Eleven Halloween Lantanas — October 18, 2026

- User corrected the total to **11 lantanas** on FPP-KULP08-FrontPorch (192.168.0.250): **port 1 = Lantana 01–08; port 2 = Lantana 09–11**. “0 to 8” was interpreted as 01–08 to match the explicit total of eleven. Each plant has 60 RGB pixels; preserve 20 leading null pixels between plants, with none on the first plant of each port.
- Added Lantana 11 as a copy of Lantana 07, positioned beside Lantana 10, and included it in corresponding Lantanas/whole-scene groups and views. Existing model names and sequence effects preserved. Native xLights allocation verified eight plants on port 1 and three on port 2; 24 current standalone layouts synchronized while preserving custom geometry, groups and submodels. Historical original Thriller left alone.
- **Local layout correction only**: no hardware/playback uploads or sequence renders. Native allocation added 180 channels to the porch controller and shifted downstream ranges. Earlier renders, physical-output-reference files and deployment plans are stale relative to this correction and must be regenerated before use. Preserve Falcon 1602 physical test settings and the pause on playback transfers.
- Backups and verification: `Halloween/lantana-eleven-layout-latest.json`, with original files under its `backup` directory. Obsolete ten-lantana helper `Halloween/Tools/update_lantana_strings.py` disabled to prevent undoing the correction.

## No physical floods — October 18, 2026

- User confirmed **there are no floods anymore at all**. Do not reintroduce flood models, flood-only mapping groups or flood output assignments in future work.
- Removed all eight floods from the Halloween master and 24 current standalone layouts: Flood Column Center/Left/Right, Flood House Left/Right, Flood Roof, Flood Tree, and Flood house - large. Removed Floods GRP, flood-only views/groups and their references, plus obsolete flood-only model rows in 19 local sequence files. Non-flood model geometry/submodels and non-flood sequence content were verified unchanged. Historical original Thriller and vendor/backups remain archival.
- Cleared and read back the three remaining physical flood outputs: porch Kulp 192.168.0.250 port 10, Genius Porch 192.168.0.9 port 14, roof Falcon 192.168.0.252 port 9. Other physical string settings and start addresses were preserved. Falcon 1602's 16 x 500-pixel test setup was verified unchanged.
- Backups and verification: `Halloween/remove-all-floods-latest.json`. Native layout allocation was recalculated and synchronized to active standalone layouts. The cumulative Lantana/flood layout changes still require a fresh full controller/address refresh when layout work is ready; do not reuse the earlier House Left deployment plan or stale physical-output references/renders. No sequence rendering or transfers were performed for flood removal. Sequence transfers remain explicitly on hold pending the user's instruction after layout testing.

## Halloween visibility is physical inventory — October 18, 2026

- User clarified: **if a prop is not visible in the Halloween layout, it is not physically on a controller**. Do not treat inactive/hidden Christmas props as installed Halloween props or automatically upload their saved assignments.
- Read-only live audit found ten hidden (`Active=0`) props still programmed: FPP-KULP16-02 / 192.168.0.205 port 12 Arch 1/2 and port 13 Arch 3/4; FPP-KULP16-01 / 192.168.0.253 port 9 Elliott - GE Flake N 1, port 10 GE Flake A 1 / Elliott - GE Flake N 2 / GE Flake A 2, port 19 Singing Bulb - Left, port 20 Singing Bulb - Right. These are findings only; this audit did not remove them or change outputs.
- Nine live controllers were read successfully, and hidden flags were checked against the open xLights session. Evidence: `Halloween/hidden-controller-audit-latest.json`. The Falcon 1602's intentional 16 x 500-pixel test strings remain an explicit exception and must be preserved. Grinch's old saved assignment does not mean Grinch is programmed on that test controller. The unnamed three-channel Genius DMX output is the visible Fog model; truncated Falcon ports 3/4 labels refer to the visible Mini Grand Illusion.

## Hidden-prop cleanup and arches exception — October 18, 2026

- User explicitly allowed the **four arches to remain on their controllers**, even though they are inactive/hidden in the Halloween layout. Preserve FPP-KULP16-02 / 192.168.0.205 port 12 = Arch 1/2 and port 13 = Arch 3/4. This is an exception to the visibility rule.
- User removed the **four hidden flakes and both programmed singing bulbs**: Elliott - GE Flake N 1/2, GE Flake A 1/2, Singing Bulb - Left/Right. Cleared FPP-KULP16-01 / 192.168.0.253 ports 9, 10, 19 and 20, restarted its output service and verified the hardware readback. Every other oak-controller output and the entire arches controller configuration were verified unchanged.
- The six inactive models remain saved for archival use but now have **No Controller and no ControllerConnection** in the master and 24 active standalone layouts. Native unassigned ranges were verified outside every controller allocation. Geometry, submodels, groups, custom song-only models and sequence effects are preserved. No sequence files were edited, rendered or transferred. Evidence/backups: `Halloween/disconnect-hidden-flakes-bulbs-latest.json`. Existing full address-refresh plans/renders remain stale while layout corrections continue; sequence transfers remain on hold.
