# Holy Forever 2026 — Sequence Agent Notes

Working notes for `Christmas/Holy Forever 2026.xsq` (built July 2026). Read alongside the root `AGENTS.md`. Song: Chris Tomlin "Holy Forever" (Jenn Johnson female vocal), media = `Videos/Chris Tomlin - Holy Forever (Lyric Video).mp4`, 308314 ms, 25 ms frames, ModelBlending on.

## ⚠ Session/saved state

2026-07-12 late evening: the session was saved to disk via `saveSequence`, then **the entire intro (everything ending at or before 15520 ms) was deleted by editing the .xsq directly** (`Tools/tmp_holy/clear_intro.py`, kept re-runnable with `--dry-run`) and the sequence was closed/reopened through the API so the live session matches disk. Direct .xsq editing for *deletion* is proven safe: line-oriented (one self-closing `<Effect .../>` per line), leaves EffectDB/ColorPalettes untouched (orphaned entries are harmless), xLights reloads clean.

**Current state: intro (0:00–0:15) carries the downstairs glowing crosses + whole-scene snowfall (brightness pulses on each choir "Holy"; see below).** The old purple/shader/7710/wind intro and Off-park stubs were deleted 2026-07-12 (`clear_intro.py`). Kept from that clear: `Projector` L0 full-length Video, timing tracks, and everything from 15275 (Snowman V1 Faces pickup) onward.

Backups from just before the edit: `Holy Forever 2026.xsq.bak-before-intro-clear` (post-save, pre-delete) and `Holy Forever 2026.pre-save.xsq.bak` (stale pre-session file).

2026-07-13: **all effects on the house-face snowflake and spinner props were deleted** (user request; same save → backup → direct-edit → close/reopen pattern, script `Tools/tmp_holy/clear_house_props.py`, re-runnable with `--dry-run`). 536 effects removed across 25 elements: `Flakes GRP` / `Flakes Outline All GRP` / `Flakes Spokes All GRP`, `GE Flake N 1/2`, `GE Reel Max 1/2`, `GE Starlord 1/2`, `GE Rosa Grande 1`, `GE Mini Grand Illusion`, and every spinner submodel GRP (Reel Max Arrows/Chevron Rings/Spokes, Starlord Plunger All/Spoke/Star, Rosa Grande Ring/Spoke/Web Spoke, Baby Grand Illusion Rings/Spokes, MOAW Diamonds/Snowflake Spoke/Spokes). This removed the verse Twinkle/Pinwheel bases, all chorus Fan hits, the Shockwave stab rotations, and the 207200 Galaxy moment on those props — **the house face now carries only House Outline/Roof/Icicles/window-matrix effects**. Backup: `Holy Forever 2026.xsq.bak-before-house-prop-clear`.

2026-07-13: **from verse 2 on, house/roof marquees flip direction on every snare** (`Tools/tmp_holy/snare_reverse_marquees.py`). Replaces the earlier whole-V2 Reverse=1 block. Snares = 72 BPM backbeat (beats 2 & 4) on the verified grid (anchor 180 ms), snapped to 25 ms — 124 hits from 96025→301025. `House Outline` + `Roof` L0 rebuilt to 136 effects (section palettes preserved; Reverse alternates at each snare). Pre-V2 unchanged. Backup: `Holy Forever 2026.xsq.bak-before-snare-reverse`.

2026-07-13: **verse-2 house/wall marquee direction flipped** (`Tools/tmp_holy/reverse_v2_house.py`). On `House Outline` and `Roof` L0, only the V2 block (95100–127625) now has `E_CHECKBOX_Marquee_Reverse=1`; all other section marquees stay Reverse=0. Wipe+re-add via `House` as empty source (deep layers untouched). Backup: `Holy Forever 2026.xsq.bak-before-v2-reverse`. **Superseded same day by snare-flip script above.**

2026-07-13 (same session): **column matrixes + all yard props except the Mega Tree cleared too** (`Tools/tmp_holy/clear_yard_props.py`, 1327 effects, backup `Holy Forever 2026.xsq.bak-before-yard-clear`). Wiped: `Column Matrixes`, `Yard Borders`, `Driveway`, `Colum Shrubs`, `Canes`, `Tree - Oak`, `Toni - Flat Tree`, all `Arches` rows, `Mini Trees`/`Mini Tree - 1..4`/`Mini Tree Stars`, `EFL Wing - Left/Right`, `Large Spiral Tree - 01..12`. Deliberately KEPT: `Mega Tree` + `Tree Topper`, all singing faces (user: "do not remove"), the `GE Merry Christmas/Christmas` Christ glow (user-requested feature; the 4 effects live on the submodel element, so top-level `GE Merry Christmas` reads 0). `Floods GRP` and `Colums` were initially kept, then **cleared on a follow-up request** (`Tools/tmp_holy/clear_floods_colums.py`, 27 effects — the floods' full-song ColorWash bed and the columns' chorus On slams; backup `Holy Forever 2026.xsq.bak-before-floods-colums-clear`). **What still has effects: Projector video, window matrixes (`Matrixes` group incl. Matrix - Lantana, downstairs/entry text+cross), `House Outline`, `Roof`, `Icicles GRP`, Mega Tree + Topper, faces, Christ glow.**

2026-07-18: **six drum/mood/section timing tracks imported and saved** (details in their own section below). Backup from just before: `Holy Forever 2026.xsq.bak-before-drum-timings`.

## Musical grid (verified — ⚠ anchor corrected 2026-07-18)

- **72.0 BPM, 4/4 — bar = 3333.33 ms. TRUE audio downbeat anchor = 600 ms** (600, 3933, 7267, 10600, 13933, …). Fitted by maximizing backbeat snare flux over V2→C3 and confirmed by section-start crashes landing on 600-grid downbeats (e.g. crashes at 13909, 40583, 93896 are all within ~35 ms of a 600-anchor downbeat but ~400 ms off the 180 grid).
- **The previously documented 180 ms anchor is half a beat (416.7 ms) EARLY vs the audio.** Effects built on it (the chorus Fan hits, and the snare-flip marquee splits from `snare_reverse_marquees.py`) actually sit on offbeat eighths, not beats. They look fine as-is — don't churn them — but **any NEW beat-locked work should use anchor 600**, or better, snap to the imported `Beat Count`/`Kick`/`Snare` timing tracks (below).
- **Section boundaries in the sequence are NOT bar-aligned** — the original sequencer placed them at vocal pickups (e.g. 15520, 67570). Don't "fix" them to the grid.

## Song structure / section times

Original effect-section boundaries: 15520, 41850, 67570, 95100, 127630, 154150, 181900, 207210, 234230, 260760, 287290, 301500 (final hold to 308264).

Sung-phrase spans (whisper-derived, clamped to the boundaries above; also in `Tools/tmp_holy/sections.json`). **This table is the vocal arrangement — who sings what, where.** On the record: Chris Tomlin = male lead (Snowman), Jenn Johnson = female lead (Teddy); our choir = 3 ChromaBulbs, then Santa/Grinch/SingingTree, then Penguins.

| Section | Span (ms) | ≈ time | Lyric | Who sings |
|---|---|---|---|---|
| V1 | 15275–39975 | 0:15–0:40 | "A thousand generations falling down in worship…" | **Snowman solo** |
| PC1 | 40950–66700 | 0:41–1:07 | "Your name is the highest… stands above them all" | **Snowman solo** |
| C1 | 66700–90825 | 1:07–1:31 | "And the angels cry Holy… Holy forever" | Snowman + Bulbs (choir enters) |
| V2 | 94375–126525 | 1:34–2:07 | "If you've been forgiven, if you've been redeemed…" | **Duet: Teddy (her entrance) with Snowman** |
| C2a | 126725–151400 | 2:07–2:31 | chorus first half | Snowman + Teddy + Bulbs |
| C2b | 153250–165750 | 2:33–2:46 | **"Hear Your people sing / To the King of kings" — Teddy's feature** | Teddy leads, Snowman backs up, Bulbs |
| C2c | 166850–178350 | 2:47–2:58 | "You will always be holy / Holy forever" | Snowman + Teddy + Bulbs |
| PC2a | 181450–207775 | 3:01–3:28 | pre-chorus pass 1 (ends "…Jesus") | + Santa, Grinch, SingingTree join |
| PC2b | 207775–233350 | 3:28–3:53 | pre-chorus pass 2 (bigger) | + Penguins → **full cast** |
| C3 | 233350–283550 | 3:53–4:44 | final chorus (both halves) | **Everyone** (fades out at the end) |
| OUT | 286700–296650 | 4:47–4:57 | "You will always be holy / Holy forever" | **Snowman solo tag** (ends as it began) |

## Original design (from 15520 on; the pre-vocal intro was deleted 2026-07-12)

~~Intro: purple ColorWash + shader + 7710 build~~ — deleted with the wind intro. **Current intro canvas:** Projector video + downstairs glowing crosses + whole-scene snowfall (above). Verses: Marquee refs on House Outline, Snowflakes on Matrixes, per-section palettes. ~~Starlord Fan hits / Galaxy moments~~ — spinner/flake props cleared 2026-07-13; final On hold 301500–308264 survives on the non-house elements.

## Added: intro glowing cross on `Matrix - Downstairs Window`

The record opens with an ethereal choir singing **"Holy" twice** before Tomlin's V1. Whisper can't transcribe the pad (too reverbed), so the swells were located by band-limited (250–3500 Hz) mid-channel RMS: **swell 1 rises ~3.9 s, peaks ~4.4–5.1, decays through ~6.4 s; swell 2 rises ~10.55 s, sustains ~10.65–11.6, decays through ~13.3 s** (a smaller mid-bump ~7.2–8.2 s is instrumental, not a "Holy").
Implementation: two Pictures effects on `Matrix - Downstairs Window` L0 (element verified addressable; matrix is 32w×35h portrait — `parm1=4` strands ×`parm2=280` ÷ `parm3=8` strands/string... net 32×35, `Dir=L` `StartSide=B`):

- 3900–6600 ms, `T_TEXTCTRL_Fadein=0.50`, `Fadeout=1.50`
- 10550–13550 ms, `Fadein=0.50`, `Fadeout=1.75`
- Image: `ImportedMedia/Holy Forever/Images/Glowing Cross.png` (AI-generated warm white/gold cross on black, padded to 585×640 ≈ the matrix aspect; referenced via the `/Users/elliott.ohara/xlights/...` symlink path). `Scale To Fit`, white palette. **Note: the API rewrote `E_FILEPICKER_Pictures_Filename` to `E_TEXTCTRL_Pictures_Filename` in the EffectDB — it renders fine; don't "fix" it.**
- Verified in `RenderCompare/holy_forever_cross_intro.mp4` (brightness curve of the matrix region matches both audio swells; measurement script: `Tools/tmp_holy/measure_cross.py`).

## Added 2026-07-18: gentle whole-scene snowfall on the intro (with Holy brightness pulses)

User: snow gently falling over the whole scene; brightness jumps up with each choir "Holy" and darkens slightly when they stop. Rebuild: `Tools/holy_forever_2026_intro_snow.py` (wipe `Whole Scene` L0 via empty `House`, re-add; does not save).

Five abutting `Snowflakes` segments on **`Whole Scene` L0**, 0–15520 (hands off before Matrixes verse snow at 15525):

| Span | Brightness | Role |
|---|---|---|
| 0–3900 | 28 | Soft pad, 2 s fade-in |
| 3900–6600 | 78 | First Holy — abrupt (`Fadein=0`), `.75` fade-out into dim |
| 6600–10550 | 42 | Slightly darker between swells |
| 10550–13550 | 78 | Second Holy — same abrupt lift |
| 13550–15520 | 42 | Afterglow, 1.5 s fade into V1 |

Effect settings: `Falling=Driving`, Count=60, Speed=4, Type=1, palette soft white `#EEEAE2`. Glowing crosses on the downstairs window still run on their own element (unchanged). **Not saved yet — scrub in the editor; save when happy.**

## Added: "Christ" glow on each PC1 "Your name" (user: "when it says Your name… light the Christ part")

Four On effects, element **`GE Merry Christmas/Christmas`** L0, warm gold `#FFC878`, with `B_CUSTOM_SubBuffer=0.00x0.00x69.10x100.00` — the `Christmas` submodel is a horizontal-layout ranges submodel whose node order tracks x (verified 0 violations), and the left 69.1% of its buffer = the cursive letters **C-h-r-i-s-t exactly** (cut lands in the t→m gap at grid x≈262/332; boundary calibrated by rendering candidate cuts from the CustomModel grid — strips in git history of `Tools/tmp_holy/`).
Each effect fades in across the sung "Your name" (start of "Your" → end of "name" from `Lyrics Lead` words layer) and fades out 1.5 s after:

- 40950–44675 (fadein 2.23) · 45300–48125 (1.32) · 48250–51750 (2.00) · 61450–64900 (1.95)
- The 4th "Your name" (48950–50250, "…stands above them all" #1) shares block 3's window; the one at 61450 is the final "Your name stands above them all".

Verified in `RenderCompare/holy_forever_christ_glow.mp4` (region brightness ramps/decays inside all four windows — `Tools/tmp_holy/measure_christ.py`; baseline ~4 outside windows is the blue verse wash bleeding into the crop, not the prop).

## Added: "Holy" text on downstairs + entry windows (every sung "Holy")

44 Text effects — one per "Holy" word mark in `Lyrics 1` (22 marks: 70425, 77275, 83975, 87250; 130075, 138525, 144750, 147300; 156450, 164350, 171025, 173950; 238150, 244375, 251150, 253950, 264425, 273625, 278350, 280575, 290350, 293875) × 2 elements, both **layer 1** (L0 downstairs holds the intro crosses):

- `Matrix - Downstairs Window` (32×35): font `7-7x9 Thin`.
- `Matrix - Entry` (24×25): font `6-5x6 Thin`.
- White, `Text_Dir=none` (static centered), fadein .25 / fadeout .5, `E_TEXTCTRL_Text=Holy`. Effect end = word end, min 700 ms (the 25 ms echo mark at 273625 gets the floor). No overlaps created.
- Blends fine over the `Matrixes`-group Snowflakes (L0 group) in both quiet C1 and busy C3 — verified frames in `RenderCompare/holy_forever_holy_text.mp4` at 71.2 s / 291.5 s.

## Deleted: swaying wind intro (was 180 → 15520)

All wind-intro voices are gone (first Off-parked, later truly deleted by `clear_intro.py`). If a wind intro is ever wanted again, `Tools/holy_forever_2026_wind_intro.py` rebuilds the full 12-voice version (bar-synced Bars gusts, marquee dash streams, mega-tree spiral sway; one lean per bar, flips at 180/3513/6847/10180/13513).

## Added: lyric timing tracks

Five tracks (3-layer: phrases with empty gap-filler marks / words / phonemes, snapped to 25 ms):

- **`Lyrics 1`** — every sung line (76/259/894 marks). The Snowman's V2+chorus-2 duet block drives from it whenever the faces are (re)added — keep it.
- **`Lyrics Lead`** — Tomlin part. ⚠ The in-sequence copy was imported **before** the C2b backup lines were added; the on-disk template now includes them but was deliberately **not re-imported** (re-importing an existing track risks duplicated marks). That's why chorus 2 uses `Lyrics 1` instead.
- **`Lyrics Female`** — Jenn part: V2, C2b, C2c, PC2a/b, C3.
- **`Lyrics Choir`** — ensemble: C1, C2, PC2a/b, C3.
- **`Lyrics Intro Choir`** — ethereal pad choir: two drawn-out **"Holy"**s at 3900–6600 and 10550–13550 (same windows as the glowing crosses / snow pulses; whisper can't hear the reverb pad, so marks are hand-placed from mid-channel RMS). Template: `Timing Templates/Holy Forever Intro Choir.xsq`. Build+import+bulb faces: `Tools/tmp_holy/add_intro_holy_choir.py`. ⚠ Imported once — do not re-import.

Template (main voices): `Timing Templates/Holy Forever Lyrics.xsq`. Pipeline that built it (word-level whisper transcription → lyric alignment → phonemes from xLights' own dictionaries): see root AGENTS.md "Lyric timing from scratch" and `Tools/tmp_holy/`. Phrase *starts* are approximate (clamped to section anchors); word ends track the vocal closely. The "Holy holy holy" echoes in C3 are folded into the "To the King of kings holy" phrase end.

## Added 2026-07-18: drum / mood / section timing tracks (6 new — sequence now has 10)

Template `Timing Templates/Holy Forever Drums and Mood.xsq`, built by `Tools/tmp_holy/build_timing_template.py` (band-limited spectral-flux onset detection on `Tools/tmp_holy/holy_44k.wav`, gated per 16th slot of the TRUE 600-anchor grid, kick/snare validated by onset-spectrum template matching, crashes by a ring/sustain test). Imported once via `importXLightsSequence` (auto, no media) and verified mark-for-mark (`Tools/tmp_holy/verify_timing_import.py` — all 6 OK). All marks snapped to 25 ms. Hit tracks are contiguous: unlabeled gap fillers + short labeled hit marks (Kick=`K` 150 ms, Snare=`S` 150 ms, Cymbals=`C` 400 ms) — sequencers key effects off the labeled marks.

- **`Song Sections`** — 15 labeled blocks on the original effect-section boundaries (Intro 0 / Verse 1 15520 / Pre-Chorus 1 41850 / Chorus 1 67570 / Verse 2 95100 / Chorus 2 127630 / "Hear Your People" female feature 154150 / Holy Forever 166850 / Pre-Chorus 2 pass 1 181900 / pass 2 full cast 207210 / Final Chorus 234230 / Hear Your People 260760 / Holy Forever 273650 / Outro solo tag 287290 / Final hold 301500).
- **`Mood`** — 12 labeled energy arcs on true-grid downbeats: Ethereal 0 → Intimate 13900 → Building 40600 (bass+kick enter, RMS jumps ~4 dB) → Anthemic 67275 → Groove 93925 (kit settles, backbeat starts) → Soaring 127275 → Featured 153925 → Regather 180600 → Climbing 207275 → Climax 233925 (loudest stretch of the song) → Afterglow 287275 (band falls away; low band drops ~19 dB at bar 87) → Silence 300600.
- **`Beat Count`** — 370 marks labeled 1–4 on the corrected grid (first beat 600, last snapped to 308300). Bars = marks labeled `1`.
- **`Kick`** — 123 hits (none in V1 — the verse percussion is muffled strums, kick proper enters at PC1). Mostly beats 1/3 + driving eighths; densest in PC2a/PC2b.
- **`Snare`** — 116 hits: steady 2-and-4 backbeat from V2 (93933) through C3c end (~286850) — grid-locked when the flux peak is weak, peak-snapped when credible — plus strong fills (the V2 pickup bar included). No backbeat before V2 (V1/PC1/C1 have no snare groove; C1's only marks are the two build-in hits at 90600/93100 area) and none in OUT.
- **`Cymbals`** — 38 crash/ride-bell hits that pass the ring test; sparse by design (section starts, chorus punctuation).
- Audition mix (song ducked + synthetic clicks at every mark): `Tools/tmp_holy/holy_drum_audition.mp3` (kick=80 Hz thump, snare=noise burst, cymbal=6 kHz ping). Regenerate with `Tools/tmp_holy/audition_clicks.py`.
- ⚠ Per the root AGENTS.md rule: these tracks are now IN the sequence — never re-import this template (duplicated marks). Rebuild-and-hand-fix in the GUI if they ever need changing.
- Analysis scratch tools (kept): `analyze_drums.py`, `grid_drums.py`, `backbeat_scan.py`, `phase_check.py`/`phase_check2.py`, `anchor_check.py` (the anchor-correction evidence), `extract_marks.py`, `refine_marks.py`, `build_drum_marks.py`.

## Singing faces (casting) — LIVE in the sequence (user-approved: "they were perfect"; do not remove)

Effect-block implementation of the vocal-arrangement table above.

All faces layer 0; **eyes and mouths render white on every prop EXCEPT Teddy**, who keeps his forced-color face (`Teddy ` def: brown mouth, blue/brown eyes) per user preference. (`No Forced Colors` is an identical-nodes all-white def if ever wanted.) Non-bulb palettes are plain white; bulbs use the 4-color C9 palette (below). Non-final blocks get +300 ms tails, final blocks +1500 ms tail with `T_TEXTCTRL_Fadeout=1.5`:

| Prop | Track | Blocks |
|---|---|---|
| GE 8ft Snowman Singing (lead) | Lyrics Lead | V1→C1; **verse 2 + all of chorus 2 as one block on `Lyrics 1`** (duets with Teddy from her 1:34 entrance, backs her up on C2b); PC2a→C3; outro solo |
| EFL Teddy (female lead) — def `Teddy `, colored face | Lyrics Female | V2; C2b→C2c; PC2a→C3 |
| Singing Bulb - L/C/R (choir) | Lyrics Intro Choir → Lyrics Choir | **Intro 3900–13850** (cross-warm, brightness 45); C1; C2a→C2c; PC2b→C3 |
| GE Santa Singing, GE Grinch Talk, SingingTree | Lyrics Choir | PC2a→C3 |
| Toni - Penguin 1/2 | Lyrics Choir | PC2b→C3 |

Regenerate everything above: `python3 Tools/tmp_holy/fix_faces.py` (wipe-and-re-add; verified to reproduce this exact state — 21 effects).

## Bulb colors (C9 look — pure Faces palette, no submodel effects) — LIVE, part of the bulbs' face effects

The ChromaBulb defs map glass = `FaceOutline` and base = `FaceOutline2`, and with `CustomColors=0` the Faces effect assigns checked palette colors **in order: mouth, eyes, FaceOutline, FaceOutline2** (verified in `FacesEffect.cpp`). Each bulb's **chorus** Faces palette is therefore:

- C1 `#FFFFFF` mouth · C2 `#FFFFFF` eyes · C3 glass (Left `#FF0000` / Center `#00FF00` / Right `#0000FF`) · C4 `#FFC800` amber base.

**Intro exception (2026-07-19):** the opening "Holy" Faces block uses a dim warm palette matching the downstairs glowing cross — mouth/eyes `#EEEAE2`, glass `#C8A878`, base `#8B6B3D`, `C_SLIDER_Brightness=45` — no C9 R/G/B. Fadein 0.50 / fadeout 1.50.

The bulb **submodel elements carry no effects** — an earlier submodel-On approach was removed; `fix_faces.py` wipes them to keep it that way. (Submodel names, if ever needed for non-face effects: Center = `Base`/`Bulb`, L/R = `Bulb Stem`/`Bulb Outline`.)

## Tools inventory (`Tools/tmp_holy/`)

- `transcribe.py` — faster-whisper word timestamps (needs a venv with `faster-whisper`; use `vad_filter=False` — VAD ate this vocal).
- `words.json` — transcription output (kept; lets you rebuild timing without re-transcribing).
- `build_lyrics.py` — alignment + phonemes + writes the 4-track template and `sections.json`. Canonical lyrics and per-voice membership live at the top of this file.
- `sections.json` — per-section/per-line sung spans (used by all placement scripts).
- `fix_faces.py` — canonical singing-face rebuild (matches live state; includes intro cross-warm bulb faces + C9 chorus palettes and clears the bulb submodels).
- `add_intro_holy_choir.py` — builds/imports `Lyrics Intro Choir` and adds the intro bulb Faces (skip-safe if already present).
- `clear_intro.py` — direct .xsq edit that deleted every model effect ending ≤15520 (supports `--dry-run`). Pattern to copy for any future time-scoped deletion the API can't do: save session → cp backup → run → close/reopen sequence.
- `migrate_faces.py`, `place_faces.py`, `lead_backup_c2.py` — historical steps, fully superseded by `fix_faces.py`.
- `../holy_forever_2026_wind_intro.py` — wind intro build.
- `reverse_v2_house.py` — (superseded) whole-V2 marquee reverse on House Outline + Roof.
- `snare_reverse_marquees.py` — from V2 on, flip House Outline + Roof marquee direction on every backbeat snare (wipe L0 / re-add; supports `--dry-run`).

## Review checklist (what to scrub)

0:00–0:15 gentle whole-scene snow (brightens on each choir "Holy", dims after) + glowing cross on downstairs window (~0:04 and ~0:11) + singing bulbs mouth the intro "Holy"s in dim warm gold · 0:15 Snowman verse 1 · 1:07 bulbs join in C9 (choir) · 1:34 verse-2 duet (Teddy leads, Snowman with her) · 2:33 female feature, Snowman backup · 3:01 Santa/Grinch/Tree join · 3:28 penguins/full cast · 4:47 Snowman outro solo, fades.
