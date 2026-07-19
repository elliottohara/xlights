# Holy Forever 2026 — Sequence Agent Notes

Working notes for `Christmas/Sequences/Holy Forever 2026/Holy Forever 2026.xsq` (built July 2026). Read alongside the root `AGENTS.md`. Song: Chris Tomlin "Holy Forever" (Jenn Johnson female vocal), media = `Media/Chris Tomlin - Holy Forever (Lyric Video).mp4`, 308314 ms, 25 ms frames, ModelBlending on.

## ⚠ Baseline (hand-approved 2026-07-19)

**The on-disk `.xsq` is the starting point. Do not re-add effects the user removed.**

Saved from the live xLights session after hand edits. Live model effects now:

- **Intro + intimate V1 (0–41850):** Whole Scene snow + Mega Tree glowing cross + dim Singing Bulb Faces; from 0:15 Snowman + `Arches - All` piano-chord SingleStrand + mini-tree note fills + oak cymbal Twinkles.
- **Windows:** `Matrix - Entry` = "Holy" Text only (L0). `Matrix - Downstairs Window`, `Matrix-Garage Window`, and `Matrix - Lantana` = **empty** (Lantana's True Piano MIDI effect removed 2026-07-19 — user reported it wasn't working; do not restore). `Matrixes` group = empty.
- **House / icicles:** `House Outline` and `Icicles GRP` = **empty** (all accent/twinkle/hold effects hand-deleted). **`Roof` = final On hold only** (301500–308275). No Marquees anywhere.
- **Also live:** Tree Topper (On accents + hold), singing faces, `GE Merry Christmas/Christ` PC1 glow.
- **Timing tracks (12):** Lyrics Lead/Female/Choir + Intro Choir, Song Sections, Mood, Beat Count, Kick, Snare, Cymbals, Piano Chords, Piano Notes. (`Lyrics 1` still missing — see faces section.)

**Do not run / deleted (would undo this baseline):**
- deleted: `Tools/migrate_matrixes_snow_to_windows.py` (window snow)
- refuse: `Tools/snare_reverse_marquees.py`, `Tools/reverse_v2_house.py` (marquees)
- refuse: `Tools/holy_forever_2026.py` (original full build), `Tools/holy_forever_2026_wind_intro.py`, `Tools/holy_forever_2026_intro_snow.py`
- no rebuild script for downstairs "Holy" Text, House Outline, Icicles GRP, or Roof accent Ons — do not recreate them

### History (clears / prior work — context only)

2026-07-12: intro cleared via `clear_intro.py` (wind/purple wash gone). Direct .xsq deletion is safe (line-oriented effects). Backups: `*.bak-before-intro-clear`.

2026-07-13: house-face flakes/spinners cleared (`clear_house_props.py`); yard props cleared (`clear_yard_props.py`); floods/columns cleared (`clear_floods_colums.py`). Marquee snare-flip / V2-reverse scripts ran then — **later cleared; those scripts now refuse**.

2026-07-18: drum/mood/section timing tracks imported. Backup: `*.bak-before-drum-timings`.

2026-07-19: Piano Chords + arch SingleStrand; mini-tree piano fills; all Marquees cleared (`clear_marquees.py`); Lantana Piano Notes; oak cymbal Twinkles; then **hand-edit baseline above** (removed window snow, downstairs Holy text, Roof accent Ons, **all House Outline + Icicles GRP effects**).

## Musical grid (verified — ⚠ anchor corrected 2026-07-18)

- **72.0 BPM, 4/4 — bar = 3333.33 ms. TRUE audio downbeat anchor = 600 ms** (600, 3933, 7267, 10600, 13933, …). Fitted by maximizing backbeat snare flux over V2→C3 and confirmed by section-start crashes landing on 600-grid downbeats (e.g. crashes at 13909, 40583, 93896 are all within ~35 ms of a 600-anchor downbeat but ~400 ms off the 180 grid).
- **The previously documented 180 ms anchor is half a beat (416.7 ms) EARLY vs the audio.** Old effects built on it (cleared Fan hits / marquees) sat on offbeat eighths. **Any NEW beat-locked work should use anchor 600**, or better, snap to the imported `Beat Count`/`Kick`/`Snare` timing tracks (below).
- **⚠ Intimate-V1 piano chords are NOT on Beat Count downbeats.** The big wide piano hits land ~1.6 s after each bar `1` (near beat 3 of the grid). Do **not** key piano-reactive effects off `Beat Count` 1 or 1+3 — use the dedicated **`Piano Chords`** track.
- **Section boundaries in the sequence are NOT bar-aligned** — the original sequencer placed them at vocal pickups (e.g. 15520, 67570). Don't "fix" them to the grid.

## Song structure / section times

Original effect-section boundaries: 15520, 41850, 67570, 95100, 127630, 154150, 181900, 207210, 234230, 260760, 287290, 301500 (final hold to 308264).

Sung-phrase spans (whisper-derived, clamped to the boundaries above; also in `Christmas/Sequences/Holy Forever 2026/Tools/sections.json`). **This table is the vocal arrangement — who sings what, where.** On the record: Chris Tomlin = male lead (Snowman), Jenn Johnson = female lead (Teddy); our choir = 3 ChromaBulbs, then Santa/Grinch/SingingTree, then Penguins.

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

## Original design (historical — superseded by baseline)

~~Intro wash/wind~~ deleted 2026-07-12. ~~Marquees / Matrixes snow / spinner Fans / Galaxy~~ all cleared in later passes or the 2026-07-19 hand edit. Do not restore from `holy_forever_2026.py`.

## Added: glowing cross on `Mega Tree` (intro + intimate V1)

The record opens with an ethereal choir singing **"Holy" twice** before Tomlin's V1. Whisper can't transcribe the pad (too reverbed), so the swells were located by band-limited (250–3500 Hz) mid-channel RMS: **swell 1 rises ~3.9 s, peaks ~4.4–5.1, decays through ~6.4 s; swell 2 rises ~10.55 s, sustains ~10.65–11.6, decays through ~13.3 s** (a smaller mid-bump ~7.2–8.2 s is instrumental, not a "Holy").

**2026-07-19:** user wanted the cross **on the whole intro**, brightening with each Holy (not discrete on/off hits). Continuous Pictures on L0, originally `0–15275`, `Fadein=1.00` / `Fadeout=1.50`, `Glowing Cross.png` (`Scale To Fit`, white). Brightness via palette `C_VALUECURVE_Brightness` Custom curve (Min=0/Max=400): dim baseline ≈30 between Holys, peak 100 on each swell.

**2026-07-19 (later):** moved the cross from `Matrix - Downstairs Window` L0 → **`Mega Tree` L0** (same timing/curve/image). Downstairs later emptied entirely in the hand-edit baseline. Backup: `Holy Forever 2026.xsq.bak-before-cross-to-megatree`.

**2026-07-19 (intimate V1):** extended cross through the acoustic verse to PC1 — now `0–41850` on Mega Tree L0. After the intro Holys, holds soft glow ≈22 through V1 (Snowman lead), eases out into PC1 (`Fadeout=2.00`). Mega Tree L0 is cross-only (verse Spirals gone), so the rebuild House-wipes L0 + re-adds. Rebuild: `Christmas/Sequences/Holy Forever 2026/Tools/continuous_cross_intro.py`. Backup: `Holy Forever 2026.xsq.bak-before-intimate-extend`.

- Image: `Media/Images/Glowing Cross.png` (AI-generated warm white/gold cross on black; referenced from the local `/Users/elliott.ohara/xlights/...` repo path). **Note: the API rewrote `E_FILEPICKER_Pictures_Filename` to `E_TEXTCTRL_Pictures_Filename` in the EffectDB — it renders fine; don't "fix" it.**

## Added: Whole Scene snow (inverse of cross; dimmed through intimate V1)

**2026-07-19:** `Whole Scene` L0 continuous Snowflakes (`Driving`, count 90, speed 4, ivory `#eeeae2`). Brightness VC is the **inverse** of the Mega Tree cross curve at the Holy-swell keypoints: quiet baseline ≈55, dips to ≈18 under each Holy peak.

**2026-07-19 (intimate V1):** extended with the cross to `0–41850`. After the intro, holds a dimmed (not zero) presence ≈28 through the acoustic verse so the atmosphere stays under the Snowman; eases toward PC1. Rebuild: `Christmas/Sequences/Holy Forever 2026/Tools/intro_snow_inverse.py` (House-wipe L0 + re-add). Backup: `Holy Forever 2026.xsq.bak-before-intimate-extend`.

## Added 2026-07-19: `Piano Chords` timing track (intimate V1 — audio-detected)

**Do not use Beat Count for these.** First attempts keyed off grid downbeats / half-notes were wrong — the user hears big wide piano *chords*, which sit ~1.6 s after each bar downbeat.

Template: `Christmas/Sequences/Holy Forever 2026/Timing Templates/Holy Forever Piano Chords.xsq` (single track, imported once). Builder: `Christmas/Sequences/Holy Forever 2026/Tools/build_piano_chords_timing.py` (on `Christmas/Sequences/Holy Forever 2026/Tools/holy_44k.wav`: low+mid spectral-breadth flux + RMS jump, min sep ~2.8 s, score ≥ 1.5). Audition (ducked song + 1 kHz clicks): `Christmas/Sequences/Holy Forever 2026/Tools/piano_chord_audition.mp3`.

- Track name: **`Piano Chords`** — contiguous marks; labeled hit = `P` (400 ms), unlabeled gap fillers to song end.
- **7 live `P` marks (user-approved "Beautiful"):** 15550, 18875, 22225, 25550, 28850, 32200, 36150.
- ⚠ **Already imported — never re-import** this template (duplicated marks). Nudge times in the GUI or rebuild template + hand-replace if detection ever needs revisiting.

## Added 2026-07-19: intimate V1 arch piano-chord SingleStrand

On each `Piano Chords` `P` mark: one SingleStrand on **`Arches - All`**, all four arches together.

- **Buffer:** `B_CHOICE_BufferStyle=Per Model Per Preview` (required — each Arch - N is a Custom triple; whole-model `Single Line` only chased one strand path).
- **Chase:** `From Middle`, `Rotations=1.0`, `Number_Chases=1`, `Color_Mix1=16`, `Fade_Type=From Head` — expands apex→both feet once and **stops at the bottom** (no Bounce types).
- **Duration:** gap to next `P` mark (~3.3 s) so the expand is slow; warm ivory `#F0E6D0`, brightness 70.
- **Arch layout note:** each `Arch - N` is Custom 126 nodes with submodels `Arch 1`/`Arch 2`/`Arch 3` (three parallel strands). Prefer the group + Per Model Per Preview over sequencing submodels by hand. Groups `Arches - Top`/`Middle`/`Bottom` are the strand rows across all four props (different use).
- Rebuild: `python3 Christmas/Sequences/Holy Forever 2026/Tools/intimate_arch_chords.py` (wipes `Arches - All` + leftover per-arch/submodel effects, re-reads `Piano Chords`). Backup: `Holy Forever 2026.xsq.bak-before-arch-chords`.

## Added 2026-07-19: intimate V1+PC1 oak cymbal sparkles

On each labeled `C` mark from the live **`Cymbals`** track from Verse 1 through Pre-Chorus 1 (`15520–67570`): one soft Twinkle on **`Tree - Oak`** L0.

- **Why Twinkle, not a chase:** the oak is a 3600-node poly-line behind the Snowman. A SingleStrand/Marquee chase reads busy and pulls focus; sparse Twinkle gives a quiet bloom with the cymbal ring.
- **7 hits:** 21425, 28075, 34750, 39750, 40575 (V1) + 43075, 54750 (PC1). Default span 2500 ms (clamped before the next hit / C1) — the 39750/40575 pair is shortened because they sit ~825 ms apart.
- Settings: Count 10 / Steps 50, warm ivory `#F0E6D0`, brightness **35**, fadein .20 / fadeout 1.40.
- Rebuild/clear: `python3 Christmas/Sequences/Holy Forever 2026/Tools/intimate_oak_cymbals.py` (`--dry-run` / `--clear-only`). Also wipes member model `Tree` so leftovers don't double.

## Added 2026-07-19: intimate V1 individual piano notes on mini trees

The arches remain the **wide-chord voice**. Six deliberately sparse fills use the smaller between-chord tonal attacks to step across **`Mini Tree - 1..4`**:

- **19 On pulses total**, 425 ms each, warm gold `#FFD89A`, brightness 55, fast 40 ms attack / 300 ms fade.
- Run starts: **16.375, 23.900, 26.175, 30.100, 33.475, 36.775 s**. Individual frame-snapped note times and tree orders are canonical in `RUNS` inside the rebuild script.
- Runs move left→right or right→left rather than counting every beat. The sequence intentionally leaves broad gaps, preserving the acoustic intimacy.
- Individual trees use **layer 0**, owned by this feature. `Mini Trees` group effects and `Mini Tree Stars` remain empty; Whole Scene snow still supplies the quiet atmospheric bed.
- Rebuild or remove: `python3 Christmas/Sequences/Holy Forever 2026/Tools/intimate_mini_tree_piano.py` (`--dry-run`, or `--clear-only` to remove the 19 pulses). The script wipes only layer 0 of the four individual mini-tree models.

## Added 2026-07-19: `Piano Notes` timing track (whole song — audio-detected)

MIDI-labeled note/chord marks for the xLights **Piano** effect (not the V1-only `Piano Chords` `P` track).

Template: `Christmas/Sequences/Holy Forever 2026/Timing Templates/Holy Forever Piano Notes.xsq`. Builder: `Christmas/Sequences/Holy Forever 2026/Tools/build_piano_notes_timing.py` (piano-band spectral flux + FFT peak → MIDI; section-gated density so choruses stay sparse; kick/cymbal flux penalty). Audition (0–90 s ducked + clicks): `Christmas/Sequences/Holy Forever 2026/Tools/piano_notes_audition.mp3`. Needs Tools `.venv` with `numpy`.

- Track name: **`Piano Notes`** — contiguous marks; labeled hit = space-separated MIDI integers (e.g. `50 55 60 68`), 350 ms; unlabeled gap fillers to song end.
- **230 labeled marks** whole song (MIDI ~42–95). V1 wide chords land on the same times as `Piano Chords` (15.55 / 18.88 / 22.23 / …).
- ⚠ **Already imported — never re-import.** Rebuild template + hand-replace in GUI if detection needs revisiting.

## Deleted 2026-07-19 (hand edit): window-matrix Snowflakes

Briefly migrated from `Matrixes` onto Entry/Downstairs/Garage so Lantana could own Piano — **user then removed all of that snow**. `Matrixes`, downstairs, and garage stay empty. Script deleted (`migrate_matrixes_snow_to_windows.py`). Do not restore window snow.

## Added 2026-07-19, removed 2026-07-19: True Piano on `Matrix - Lantana` (whole song)

One Piano effect `0–308275` on Lantana L0 (True Piano, Show Sharps, Fade Notes, track `Piano Notes`, MIDI range 44–88, Scale 100, warm ivory/gold/white palette, brightness 55). **User reported it wasn't working; removed same day via `lantana_piano.py --clear-only`.** Lantana is now empty — do not re-add. Script `Christmas/Sequences/Holy Forever 2026/Tools/lantana_piano.py` still exists (its non-clear mode would rebuild this effect) — **refuse to run it** without new user direction to re-add Lantana piano.

## Added 2026-07-19: Tree Topper (Mega Tree star) on PC1 bass thumps

Mood **Building - bass and kick enter** through Pre-Chorus 1. **Not keyed off the Kick timing track** — those marks are early / miss the bass figure. Audio (low-passed envelope onset on `holy_44k.wav`) finds **8 pairs** of thumps (~625–650 ms apart, pairs ~2.7 s apart), e.g. 42325+42975 (not Kick’s 42250+42700).

- Gold **Shockwave** per thump (lead: Fadeout=1.00 / 1100 ms). Pair follow-ups nudged **50 ms early**, snappier Shockwave (Accel 12, zero fadein, Fadeout=.85 / 950 ms), hotter gold/white — so the 2nd doesn’t feel delayed.
- Alternates **`Tree Topper` L1/L2/L3** so decays can overlap the next hit.
- Owns L1–L3 only inside 42000–67570. Detect + rebuild: `Tools/.venv/bin/python …/pc1_double_kick_star.py` (`--dry-run` / `--clear-only` / `--audition` → `Tools/pc1_bass_thump_audition.mp3`).
- Backup: `Holy Forever 2026.xsq.bak-before-pc1-double-kick-star`.

## Added: "Christ" glow on each PC1 "Your name" (user: "when it says Your name… light the Christ part")

Four On effects, element **`GE Merry Christmas/Christ`** L0, warm gold `#FFC878`, with **no custom buffer**. `Christ` is now a dedicated horizontal-layout ranges submodel: 241 unique nodes, exactly the left prefix of the existing `Christmas` ordering through custom-grid x=262; the remaining `mas` starts at x=264. The same submodel row is present in both the live local show layout and canonical `Christmas/xlights_rgbeffects.xml`.
Each effect fades in across the sung "Your name" (start of "Your" → end of "name" from `Lyrics Lead` words layer) and fades out 1.5 s after:

- 40950–44675 (fadein 2.23) · 45300–48125 (1.32) · 48250–51750 (2.00) · 61450–64900 (1.95)
- The 4th "Your name" (48950–50250, "…stands above them all" #1) shares block 3's window; the one at 61450 is the final "Your name stands above them all".

Migrated target-only with `Christmas/Sequences/Holy Forever 2026/Tools/migrate_christ_submodel.py` (replacement effects verified before the old buffered row was wiped). Render/export verified in `RenderCompare/holy_forever_christ_submodel.mp4`; the 43.0 s frame lights only the dedicated gold `Christ` segment.

## Live: "Holy" text on entry window only

**Baseline:** 22 Text effects on **`Matrix - Entry` L0** only (one per sung "Holy"; font `6-5x6 Thin`, white, static centered, fadein .25 / fadeout .5). Downstairs Holy Text were **hand-deleted 2026-07-19** — do not restore. No rebuild script.

## Deleted: swaying wind intro (was 180 → 15520)

Gone via `clear_intro.py`. `Tools/holy_forever_2026_wind_intro.py` now **refuses** (would re-add marquees/bars onto the empty intro).

## Added: lyric timing tracks

The copied sequence currently contains four lyric tracks (3-layer: phrases with empty gap-filler marks / words / phonemes, snapped to 25 ms):

- **`Lyrics Lead`** — Tomlin part. The in-sequence copy was imported before the C2b backup lines were added.
- **`Lyrics Female`** — Jenn part: V2, C2b, C2c, PC2a/b, C3.
- **`Lyrics Choir`** — ensemble: C1, C2, PC2a/b, C3.
- **`Lyrics Intro Choir`** — two hand-placed “Holy” swells at 3900–6600 and 10550–13550; the dim bulb Faces block driven by it extends through 41850.

⚠ **Copied-source inconsistency:** `Lyrics 1` (the full-lyric track) is absent from the current `.xsq`, even though the Snowman's V2-through-chorus-2 Faces block still references it. Do not assume that block will mouth correctly, and do not run `fix_faces.py`, until the track is deliberately restored. A mark-for-mark recovery template was extracted from the last complete backup as `Christmas/Sequences/Holy Forever 2026/Timing Templates/Holy Forever Lyrics 1.xsq` (76/259/894 phrase/word/phoneme marks). Import it **once**.

Templates: `Christmas/Sequences/Holy Forever 2026/Timing Templates/Holy Forever Lyrics.xsq` contains the three per-voice tracks; `Christmas/Sequences/Holy Forever 2026/Timing Templates/Holy Forever Lyrics 1.xsq` is the full-lyric recovery track; `Christmas/Sequences/Holy Forever 2026/Timing Templates/Holy Forever Intro Choir.xsq` contains the preserved intro track. The main pipeline is `Christmas/Sequences/Holy Forever 2026/Tools/build_lyrics.py`; `Christmas/Sequences/Holy Forever 2026/Tools/add_intro_holy_choir.py` is the older intro-track builder. Phrase *starts* are approximate (clamped to section anchors); word ends track the vocal closely. The "Holy holy holy" echoes in C3 are folded into the "To the King of kings holy" phrase end.

## Added 2026-07-18: drum / mood / section timing tracks (6) — plus Piano Chords + Piano Notes 2026-07-19 → **12 timing tracks total**

Template `Christmas/Sequences/Holy Forever 2026/Timing Templates/Holy Forever Drums and Mood.xsq`, built by `Christmas/Sequences/Holy Forever 2026/Tools/build_timing_template.py` (band-limited spectral-flux onset detection on `Christmas/Sequences/Holy Forever 2026/Tools/holy_44k.wav`, gated per 16th slot of the TRUE 600-anchor grid, kick/snare validated by onset-spectrum template matching, crashes by a ring/sustain test). Imported once via `importXLightsSequence` (auto, no media) and verified mark-for-mark (`Christmas/Sequences/Holy Forever 2026/Tools/verify_timing_import.py` — all 6 OK). All marks snapped to 25 ms. Hit tracks are contiguous: unlabeled gap fillers + short labeled hit marks (Kick=`K` 150 ms, Snare=`S` 150 ms, Cymbals=`C` 400 ms) — sequencers key effects off the labeled marks.

(Current total: 3 per-voice lyric tracks + Intro Choir + these 6 tracks + **`Piano Chords`** + **`Piano Notes`** = 12.)

- **`Song Sections`** — 15 labeled blocks on the original effect-section boundaries (Intro 0 / Verse 1 15520 / Pre-Chorus 1 41850 / Chorus 1 67570 / Verse 2 95100 / Chorus 2 127630 / "Hear Your People" female feature 154150 / Holy Forever 166850 / Pre-Chorus 2 pass 1 181900 / pass 2 full cast 207210 / Final Chorus 234230 / Hear Your People 260760 / Holy Forever 273650 / Outro solo tag 287290 / Final hold 301500).
- **`Mood`** — 12 labeled energy arcs on true-grid downbeats: Ethereal 0 → Intimate 13900 → Building 40600 (bass+kick enter, RMS jumps ~4 dB) → Anthemic 67275 → Groove 93925 (kit settles, backbeat starts) → Soaring 127275 → Featured 153925 → Regather 180600 → Climbing 207275 → Climax 233925 (loudest stretch of the song) → Afterglow 287275 (band falls away; low band drops ~19 dB at bar 87) → Silence 300600.
- **`Beat Count`** — 370 marks labeled 1–4 on the corrected grid (first beat 600, last snapped to 308300). Bars = marks labeled `1`.
- **`Kick`** — 123 hits (none in V1 — the verse percussion is muffled strums, kick proper enters at PC1). Mostly beats 1/3 + driving eighths; densest in PC2a/PC2b.
- **`Snare`** — 116 hits: steady 2-and-4 backbeat from V2 (93933) through C3c end (~286850) — grid-locked when the flux peak is weak, peak-snapped when credible — plus strong fills (the V2 pickup bar included). No backbeat before V2 (V1/PC1/C1 have no snare groove; C1's only marks are the two build-in hits at 90600/93100 area) and none in OUT.
- **`Cymbals`** — 38 crash/ride-bell hits that pass the ring test; sparse by design (section starts, chorus punctuation).
- Audition mix (song ducked + synthetic clicks at every mark): `Christmas/Sequences/Holy Forever 2026/Tools/holy_drum_audition.mp3` (kick=80 Hz thump, snare=noise burst, cymbal=6 kHz ping). Regenerate with `Christmas/Sequences/Holy Forever 2026/Tools/audition_clicks.py`.
- ⚠ Per the root AGENTS.md rule: these tracks are now IN the sequence — never re-import this template (duplicated marks). Rebuild-and-hand-fix in the GUI if they ever need changing.
- Analysis scratch tools (kept): `analyze_drums.py`, `grid_drums.py`, `backbeat_scan.py`, `phase_check.py`/`phase_check2.py`, `anchor_check.py` (the anchor-correction evidence), `extract_marks.py`, `refine_marks.py`, `build_drum_marks.py`.

## Singing faces (casting) — LIVE in the sequence (user-approved: "they were perfect"; do not remove)

Effect-block implementation of the vocal-arrangement table above.

All faces layer 0; **eyes and mouths render white on every prop EXCEPT Teddy**, who keeps his forced-color face (`Teddy ` def: brown mouth, blue/brown eyes) per user preference. (`No Forced Colors` is an identical-nodes all-white def if ever wanted.) Non-bulb palettes are plain white; bulbs use the 4-color C9 palette (below). Non-final blocks get +300 ms tails, final blocks +1500 ms tail with `T_TEXTCTRL_Fadeout=1.5`:

| Prop | Track | Blocks |
|---|---|---|
| GE 8ft Snowman Singing (lead) | Lyrics Lead | V1→C1; **verse 2 + all of chorus 2 as one block on `Lyrics 1`** (duets with Teddy from her 1:34 entrance, backs her up on C2b); PC2a→C3; outro solo |
| EFL Teddy (female lead) — def `Teddy `, colored face | Lyrics Female | V2; C2b→C2c; PC2a→C3 |
| Singing Bulb - L/C/R (choir) | Lyrics Intro Choir (dim) then Lyrics Choir | **intro Holys + intimate V1** (`3900–41850`, muted ivory/gold palette, brightness 40); then C1; C2a→C2c; PC2b→C3 (full C9) |
| GE Santa Singing, GE Grinch Talk, SingingTree | Lyrics Choir | PC2a→C3 |
| Toni - Penguin 1/2 | Lyrics Choir | PC2b→C3 |

⚠ The current scripts are not yet a one-command full rebuild: `fix_faces.py` requires the missing `Lyrics 1` track and removes the dim intro/V1 bulb block, while `intimate_bulb_faces.py` only extends an intro block that already exists. Preserve the live effects; restore `Lyrics 1` and reconcile those two scripts before rebuilding all faces.

## Bulb colors (C9 look — pure Faces palette, no submodel effects) — LIVE, part of the bulbs' face effects

The ChromaBulb defs map glass = `FaceOutline` and base = `FaceOutline2`, and with `CustomColors=0` the Faces effect assigns checked palette colors **in order: mouth, eyes, FaceOutline, FaceOutline2** (verified in `FacesEffect.cpp`). Each bulb's Faces palette is therefore:

- C1 `#FFFFFF` mouth · C2 `#FFFFFF` eyes · C3 glass (Left `#FF0000` / Center `#00FF00` / Right `#0000FF`) · C4 `#FFC800` amber base.

The bulb **submodel elements carry no effects** — an earlier submodel-On approach was removed; `fix_faces.py` wipes them to keep it that way. (Submodel names, if ever needed for non-face effects: Center = `Base`/`Bulb`, L/R = `Bulb Stem`/`Bulb Outline`.)

## Tools inventory (`Christmas/Sequences/Holy Forever 2026/Tools/`)

- `transcribe.py` — faster-whisper word timestamps (needs a venv with `faster-whisper`; use `vad_filter=False` — VAD ate this vocal).
- `words.json` — transcription output (kept; lets you rebuild timing without re-transcribing).
- `build_lyrics.py` — alignment + phonemes + writes the 3-track per-voice template and `sections.json`. Canonical lyrics and per-voice membership live at the top of this file.
- `sections.json` — per-section/per-line sung spans (used by all placement scripts).
- `fix_faces.py` — canonical C1+ singing-face rebuild (includes bulb C9 palettes and clears the bulb submodels). It requires the currently missing `Lyrics 1` track and does not recreate the dim intro/V1 bulb block.
- `add_intro_holy_choir.py` — preserved builder/importer for `Lyrics Intro Choir`; do not re-import when the track exists. Its short original Faces treatment is historical; `intimate_bulb_faces.py` defines the current longer treatment.
- `clear_intro.py` — direct .xsq edit that deleted every model effect ending ≤15520 (supports `--dry-run`). Pattern to copy for any future time-scoped deletion the API can't do: save session → cp backup → run → close/reopen sequence.
- `continuous_cross_intro.py` — rebuild Mega Tree L0 cross through intro + intimate V1 (`0–41850`); clears leftover downstairs L0 if any.
- `intro_snow_inverse.py` — Whole Scene L0 Snowflakes through intro + intimate V1 (`0–41850`, inverse of cross then dimmed verse hold ≈28).
- `intimate_bulb_faces.py` — extend muted dim Faces on Singing Bulb L/C/R through intro + intimate V1 (`3900–41850`, brightness 40); preserves later C9 choir blocks.
- `build_piano_chords_timing.py` — detect + write Piano Chords template + audition. Track already imported — do not re-import.
- `build_piano_notes_timing.py` — whole-song Piano Notes template + audition. Track already imported — do not re-import. Run via `Tools/.venv/bin/python`.
- `intimate_arch_chords.py` — wipe/rebuild `Arches - All` piano SingleStrand from live `Piano Chords` `P` marks.
- `intimate_mini_tree_piano.py` — wipe/rebuild mini-tree piano-note fills (`--dry-run` / `--clear-only`).
- `intimate_oak_cymbals.py` — wipe/rebuild oak V1+PC1 cymbal Twinkles (`--dry-run` / `--clear-only`).
- `lantana_piano.py` — wipe/rebuild full-song True Piano on `Matrix - Lantana` (`--dry-run` / `--clear-only`). **Removed 2026-07-19 (user: not working) — refuse to re-run its build mode; `--clear-only` is safe/idempotent.**
- `migrate_christ_submodel.py` — one-shot Christ-submodel migration (already done).
- `migrate_faces.py`, `place_faces.py`, `lead_backup_c2.py` — historical; superseded by `fix_faces.py`.
- **REFUSE / deleted:** `holy_forever_2026.py`, `holy_forever_2026_wind_intro.py`, `holy_forever_2026_intro_snow.py`, `snare_reverse_marquees.py`, `reverse_v2_house.py`; deleted `migrate_matrixes_snow_to_windows.py`.

## Review checklist (baseline — do not “restore” removed bits)

0:00–0:42 Whole Scene snow + Mega Tree cross + dim bulbs · 0:15 Snowman + arch piano chords + mini-tree fills + oak cymbal Twinkles · Lantana empty (Piano MIDI effect removed 2026-07-19, wasn't working) · Entry "Holy" Text only (no downstairs/garage/window snow) · House Outline + Icicles empty; Roof final-hold only; Tree Topper accents kept · faces casting as below · 4:47 Snowman outro solo.
