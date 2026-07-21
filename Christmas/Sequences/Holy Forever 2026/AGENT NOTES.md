# Holy Forever 2026 — Sequence Agent Notes

Working notes for `Christmas/Sequences/Holy Forever 2026/Holy Forever 2026.xsq` (built July 2026). Read alongside the root `AGENTS.md`. Song: Chris Tomlin "Holy Forever" (Jenn Johnson female vocal), media = `Media/Chris Tomlin - Holy Forever (Lyric Video).mp4`, 308314 ms, 25 ms frames, ModelBlending on.

**Current task:** branch `holy-c1-flakes-blue-amber` in permanent **Slot A** (`/Users/elliott.ohara/xlights-worktrees/slot-a`, API 49913). C1 flakes sparkles + Mini Grand glowing cross.

**Prior task (Slot A):** branch `holy-c1-house-icicles` — C1 house Rosa-red reveal + BMOAW red/amber motion; merged to main.

**2026-07-21 (Slot B, branch `sequence-show-folders`):** this folder is now a **standalone xLights show folder** — it has its own `xlights_rgbeffects.xml` copy (may diverge from the master for song-specific groups/views) plus `../../` symlinks to shared show-root assets. Launch xLights with `-s` pointing at this folder. See "Per-sequence show folders" in root `AGENTS.md`; promotion/refresh via `Tools/make_show_folder.sh`. No layout customizations yet — the copy matches the master as of this date.

## ⚠ Baseline (hand-approved 2026-07-19)

**The on-disk `.xsq` is the starting point. Do not re-add effects the user removed.**

Saved from the live xLights session after hand edits. Live model effects now:

- **Intro + intimate V1 (0–41850):** Whole Scene snow + Mega Tree glowing cross + dim Singing Bulb Faces; from 0:15 Snowman + `Arches - All` piano-chord SingleStrand + mini-tree note fills + oak cymbal Twinkles.
- **Windows:** `Matrix - Entry`, `Matrix - Downstairs Window`, `Matrix-Garage Window`, and `Matrix - Lantana` = **empty** (script "Holy" Text removed 2026-07-21 — do not restore; Lantana piano removed 2026-07-19). `Matrixes` group = empty. C1 Rosa marquee is on the `Windows` group (frames).
- **House / icicles:** `Icicles GRP` = **empty**. `House Outline` = empty except the **8 C3 climax drum-riff strobe flashes** (see below; L0 only, layers 1–3 still empty). `Roof` L0 = final On hold only (301500–308275).
- **Also live:** Tree Topper bass accents; **four** Mega Tree meteor windows on sung **"name"**; **four** `Whole Scene w Matrixes` implosions phase-locked into `Christ` (same four moments — not thrones/powers/positions); Christ bass blinks matching those windows; "angels cry" EFL Wing stacks; and the verified Teddy/Bulb/Penguin/PiXeL Paradise choir described below.
- **Timing tracks (13):** Lyrics 1, Lyrics Lead/Female/Choir + Intro Choir, Song Sections, Mood, Beat Count, Kick, Snare, Cymbals, Piano Chords, Piano Notes.

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

## Xtreme V1 pass (2026-07-19 — built on branch `xtremeify`, MERGED to main same day; worktree removed)

Applied the Xtreme Sequences techniques (see `Style References/XTREME SEQUENCES STYLE REPORT.md`) to Verse 1 only, at verse brightness — five changes on top of the hand-approved baseline. All V1 starts verified 100% quantized (±25 ms) to labeled timing marks (`Tools/work/audit_v1_quantization.py`).

1. **Rotating chord banks** (`Tools/xtreme_v1_chord_banks.py`): each `Piano Chords` `P` mark gets a dim (b30) warm Shockwave (Xtreme skeleton, `Per Model Per Preview`) on a rotating bank — Canes → `GE Rosa Grande Web Ring GRP` → `GE Starlord Plunger All GRP` → `GE Baby Grand Illusion Rings GRP` → `GE Reel Max Circles Outer GRP` → `Flakes Outline All GRP` → `Mini Tree Stars`+Canes. All these part-bank GRPs ARE addressable in the master view (probed 2026-07-19). L0 of each bank is owned by this script.
2. **Arch reveal pair** (`Tools/xtreme_v1_arch_reveal.py`): the approved From-Middle chase is now L0 white SingleStrand `T_CHOICE_LayerMethod=1 reveals 2` over L1 ivory→gold Color Wash (`--restore-flat` rebuilds the old flat look). Effect name for the API is `Color Wash` (with space) — `ColorWash` fails with worked:false.
3. **Mini trees on real onsets** (`Tools/xtreme_v1_mini_tree_notes.py`): replaces the 19 hand-curated pulses with 15 pulses, one per labeled `Piano Notes` mark in V1 (chord-coincident marks ±50 ms excluded), top MIDI note rank-mapped to `Mini Tree - 1..4` (low→left).
4. **Oak odd/even split** (`Tools/xtreme_v1_oak_split.py`): V1 cymbal Twinkles alternate left/right `B_CUSTOM_SubBuffer` halves (the tight 39750/40575 pair answers itself); the two PC1 hits stay full-tree. Supersedes `intimate_oak_cymbals.py` on this branch.
5. **Snow rest dips** (`Tools/xtreme_v1_snow_phrase_dips.py`): rebuild of `intro_snow_inverse.py` whose verse hold (28/400) dips to 16/400 in `Lyrics Lead` word-layer gaps ≥500 ms. V1's vocal is nearly continuous — exactly ONE rest qualifies (18150–18950).

On this branch the superseded builders are `intimate_arch_chords.py`, `intimate_mini_tree_piano.py`, `intimate_oak_cymbals.py`, `intro_snow_inverse.py` — running them would undo the pass. Preview: `RenderCompare/holy_forever_xtremeify_v1.mp4` (primary tree); per-chord fire verified numerically (`Tools/work/frame_diff_check.py`).

**Session quirks learned:** `changeShowFolder` reports success but does NOT stick — relaunch xLights with `-s <worktree>/Christmas` instead. `openSequence` on a file outside the active show folder silently opens an empty 30 s sequence (media="", len=30000) — always verify `getOpenSequence` length. `renderAll`/`exportVideoPreview` hung once when `RenderCompare/` didn't exist; create output dirs first, and a hung xLights needs kill -9 (AppleScript quit leaves it wedged).

## Musical grid (verified — ⚠ anchor corrected 2026-07-18)

- **72.0 BPM, 4/4 — bar = 3333.33 ms. TRUE audio downbeat anchor = 600 ms** (600, 3933, 7267, 10600, 13933, …). Fitted by maximizing backbeat snare flux over V2→C3 and confirmed by section-start crashes landing on 600-grid downbeats (e.g. crashes at 13909, 40583, 93896 are all within ~35 ms of a 600-anchor downbeat but ~400 ms off the 180 grid).
- **The previously documented 180 ms anchor is half a beat (416.7 ms) EARLY vs the audio.** Old effects built on it (cleared Fan hits / marquees) sat on offbeat eighths. **Any NEW beat-locked work should use anchor 600**, or better, snap to the imported `Beat Count`/`Kick`/`Snare` timing tracks (below).
- **⚠ Intimate-V1 piano chords are NOT on Beat Count downbeats.** The big wide piano hits land ~1.6 s after each bar `1` (near beat 3 of the grid). Do **not** key piano-reactive effects off `Beat Count` 1 or 1+3 — use the dedicated **`Piano Chords`** track.
- **Section boundaries in the sequence are NOT bar-aligned** — the original sequencer placed them at vocal pickups (e.g. 15520, 67570). Don't "fix" them to the grid.

## Song structure / section times

Original effect-section boundaries: 15520, 41850, 67570, 95100, 127630, 154150, 181900, 207210, 234230, 260760, 287290, 301500 (final hold to 308264).

Sung-phrase spans (whisper-derived, clamped to the boundaries above; also in `Christmas/Sequences/Holy Forever 2026/Tools/sections.json`). **This table is the vocal arrangement — who sings what, where.** On the record: Chris Tomlin = male lead (Snowman), Jenn Johnson = female lead (Teddy); our chorus choir = 3 ChromaBulbs + both Penguins + the seven-face `PiXeL Paradise Xmas Tree Choir` from C1, with Santa/Grinch/SingingTree joining in PC2.

| Section | Span (ms) | ≈ time | Lyric | Who sings |
|---|---|---|---|---|
| V1 | 15275–39975 | 0:15–0:40 | "A thousand generations falling down in worship…" | **Snowman solo** |
| PC1 | 40950–66700 | 0:41–1:07 | "Your name is the highest… stands above them all" | **Snowman solo** |
| C1 | 66700–90825 | 1:07–1:31 | "And the angels cry Holy… Holy forever" | Snowman + Bulbs + Penguins + PiXeL Paradise Tree Choir |
| V2 | 94375–126525 | 1:34–2:07 | "If you've been forgiven, if you've been redeemed…" | **Duet: Teddy (her entrance) with Snowman** |
| C2a | 126725–151400 | 2:07–2:31 | chorus first half | Snowman + Teddy + Bulbs + Penguins + PiXeL Paradise Tree Choir |
| C2b | 153250–165750 | 2:33–2:46 | **"Hear Your people sing / To the King of kings" — Teddy's feature** | Teddy leads, Snowman backs up, Bulbs + Penguins + PiXeL Paradise Tree Choir |
| C2c | 166850–178350 | 2:47–2:58 | "You will always be holy / Holy forever" | Snowman + Teddy + Bulbs + Penguins + PiXeL Paradise Tree Choir |
| PC2a | 181450–207775 | 3:01–3:28 | pre-chorus pass 1 (ends "…Jesus") | + Santa, Grinch, SingingTree join |
| PC2b | 207775–233350 | 3:28–3:53 | pre-chorus pass 2 (bigger) | Bulbs + Penguins + PiXeL Paradise Tree Choir rejoin → **full cast** |
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

## Moved/rebuilt 2026-07-20: intimate V1 piano notes → dense onsets on `All Shrubs GRP` (LIVE, branch `shrub-verse-piano-notes`, Slot A)

User moved the "mini trees in front of the arches" verse effect onto the shrub bank, then refined it across several iterations (whole-group flash → per-prop → 5-prop → 14-prop keyboard → sparse melody off the `Piano Notes` track → **dense audio-detected onsets**). The mini trees (`Mini Tree - 1..4`) are now **empty** in V1; `All Shrubs GRP` members carry the verse piano.

- **Master view fix (⚠ .xsq edit, reproducible):** the 9 `Rose Bush N` models are excluded from this sequence's master view, so the API rejects them ("target element doesn't exists."; no API adds master-view elements). `Tools/add_rosebush_masterview.py` (idempotent; sequence CLOSED → reopen) adds each to `<DisplayElements>` (next to the shrubs) + an empty `<EffectLayer/>` in `<ElementEffects>`. **General fix for any non-addressable group member.** Re-run after any revert.
- **Left→right prop order (by layout X):** `Shrub Left, Rose Bush 1, Rose Bush 2, Door Tree Left, Rose Bush 3, Rose Bush 4, Door Tree Right, Shrub Center, Rose Bush 5, Rose Bush 6, Rose Bush 7, Rose Bush 8, Shrub Right, Rose Bush 9`. Spatial rule: **lower pitch → farther left.**
- **Dense onsets (LIVE):** `Tools/v1_piano_dense.py` (run via `Tools/.venv/bin/python`). The imported `Piano Notes` track is deliberately sparse (~15–22 V1 marks) and felt thin; instead detect real note attacks from audio. Pipeline (numpy in `Tools/.venv`): `Tools/holy_44k.wav` (ffmpeg mono 44.1k of the media) → STFT (2048/441) → band flux (150–2500 Hz) → adaptive peak pick (×1.35, min sep 150 ms) = **~109 onsets in V1 (~4.4/s)**. Pitch proxy = spectral centroid in 160–1600 Hz (a single peak bin collapsed onto the vocal fundamental; centroid is stable), onsets **percentile-ranked** across the 14 props (low→left) for even use (~7–8/prop). ONE prop per onset. Warm gold `#FFD89A` On, brightness 55, `.02`/`.20` fade, 260 ms; same-prop overlaps shortened to stay on L0. **109 live effects, all L0** (verified close/reopen, len 308314 ms). Knobs (`THRESH_MULT`, `MIN_SEP_MS`, `PULSE_MS`, bands) in its CONFIG block.
- ⚠ **`cloneModelEffects` only clears L0 in 2026.13** (probed: 1-layer House AND 4-layer group source both leave L1 intact). To reset upper layers use the direct-.xsq `Tools/clear_shrub_props.py` (closed → reopen). This design is L0-only so normal reruns are fine.
- **Superseded — do not run alongside:** `mini_tree_notes_to_shrubs.py` (sparse melody off the timing track), `intimate_mini_tree_piano.py` / `xtreme_v1_mini_tree_notes.py` (old mini-tree pulses).
- Backups (`*.xsq.bak-*`, gitignored): `-before-shrubs-mini-tree-move`, `-before-shrubs-per-prop-notes`, `-before-rosebush-masterview`, `-before-melody-single`, `-before-clear-shrub-props`, `-before-dense-piano`, `-before-add-rosebush-masterview`.

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

## Added 2026-07-19: PC1 Mega Tree ascents on "name" bass pairs

- **Four** PC1 bass pairs (those landing on sung **"name"**) get sparse amber/gold **`Meteors Up`** on Mega Tree L1, starting 1375 ms before the pair's first star hit. Tree Topper still accents all eight pairs.
- First-star anchors kept: **42325 / 45650 / 49000 / 62325** (removed 52325, 55650, 58975, 65650 — thrones/powers/positions and "stands above" tails).
- Rebuild: `Tools/pc1_star_ascent.py` (name-word filter). Trim existing build: `Tools/pc1_your_name_only.py`.

## Added 2026-07-19: Christ bass blinks + whole-scene meteor convergence

- **`GE Merry Christmas/Christ` blinks on the four PC1 bass pairs that land on sung "name"** (not thrones/powers/positions or "stands above them all" tails). Tree Topper still hits all eight pairs; meteor/Christ choreography is limited to "Your name is the highest/greatest", the first "name" in "stands above them all", and the final "name" before chorus. **Layout note (2026-07-20):** user reworked the `Christ` submodel in the layout (custom-grid ranges). Sequence scripts may target the element name; **never rewrite the submodel in `xlights_rgbeffects.xml`.**
- `GE Merry Christmas` parent L0 carries **four** Off masks (one per meteor window) so scene implosions do not light `Merry`/`mas`; Christ submodel pulses render back over each mask.
- **2026-07-20 (branch `holy-pc1-house-chase`, LIVE in Slot B):** `Whole Scene w Matrixes` L0 **four** amber/gold `Meteors Implode` windows on sung **"name"** bass pairs, Per Preview with Christ offsets (−17, −7) so the house **and matrices** chase into Christ. Christ blinks + sign Off masks unchanged. Rebuild: `Tools/pc1_house_name_chase.py` after `cleanup_pc1_convergence.py`, then `Tools/pc1_star_descent.py`.
- **Rejected same day:** house-adjacent-only split (`Colum Shrubs` / `House Outline` / `Roof` / `Verts` / `Windows` / `Colums` / `Icicles GRP`) — looked like icicles+outlines only because `Windows` is outline submodels (not matrix panels) and Per Model Per Preview imploded each prop into itself. Do not restore that split.
- **2026-07-20 (same branch):** on the **four star pairs where Christ does not fire** (thrones/powers/positions + "stands above" tail — first stars **52325 / 55650 / 58975 / 65650**), amber/gold **`Meteors Down`** on **`Mega Tree` L1**, starting at the lead Tree Topper hit for **1375 ms**. Rebuild: `Tools/pc1_star_descent.py` (cleanup wipes these — re-run after house chase).
- Legacy: `Tools/pc1_christ_convergence.py` (same Whole Scene recipe; house_name_chase is the current owner). `pc1_star_ascent.py` superseded. One-shot trim: `Tools/pc1_your_name_only.py` (close xLights first).
- Backup: `Backups/Holy Forever 2026.xsq.bak-before-pc1-clean-reapply`.

## Deleted 2026-07-21: script "Holy" Text (Projector + Entry + Downstairs)

Removed — user tired of fighting window-marquee overlap. `Projector` / `Matrix - Entry` / `Matrix - Downstairs Window` L0 are empty. Do **not** restore. `Tools/angels_cry_holy_text.py` **refuses** to rebuild (clear-only still works). Backup from when it was first added: `Holy Forever 2026.xsq.bak-before-angels-cry-holy-text`.

Earlier history (all gone): (1) 22 static Entry-only `6-5x6 Thin` Texts; (2) 2026-07-20 Brush Script + brightness breath on 9 triad holys; (3) Additive / SubBuffer inset attempts vs `Windows` marquees.

## Historical: "Holy" text on entry window only (removed before 2026-07-20)

~~Baseline: 22 Text effects on `Matrix - Entry` L0 only~~ — no longer in the file.

## Deleted: swaying wind intro (was 180 → 15520)

Gone via `clear_intro.py`. `Tools/holy_forever_2026_wind_intro.py` now **refuses** (would re-add marquees/bars onto the empty intro).

## Added: lyric timing tracks

The copied sequence currently contains four lyric tracks (3-layer: phrases with empty gap-filler marks / words / phonemes, snapped to 25 ms):

- **`Lyrics Lead`** — Tomlin part. The in-sequence copy was imported before the C2b backup lines were added.
- **`Lyrics Female`** — Jenn part: V2, C2b, C2c, PC2a/b, C3.
- **`Lyrics Choir`** — ensemble: C1, C2, PC2a/b, C3.
- **`Lyrics Intro Choir`** — two hand-placed “Holy” swells at 3900–6600 and 10550–13550; the dim bulb Faces block driven by it extends through 41850.

✅ **Fixed 2026-07-19 (branch `teddy-pink-expressive`):** `Lyrics 1` (the full-lyric track) was missing from the `.xsq`, which is why the Snowman went silent during his V2/Chorus-2 duet+backup block (94375–178650, `E_CHOICE_Faces_TimingTrack=Lyrics 1` with no matching timing element — Faces effect had nothing to sync mouths to). Restored by importing `Christmas/Sequences/Holy Forever 2026/Timing Templates/Holy Forever Lyrics 1.xsq` once (`importXLightsSequence`, auto, no media) — verified 1229 marks landed across 3 layers (76 phrase / 259 word / 894 phoneme), matching the extracted template exactly. Saved, closed/reopened to confirm `getOpenSequence` length unchanged (308314 ms). Backup: `Holy Forever 2026.xsq.bak-before-lyrics1-restore`. **Track is now present — never re-import this template again** (would duplicate marks).

Templates: `Christmas/Sequences/Holy Forever 2026/Timing Templates/Holy Forever Lyrics.xsq` contains the three per-voice tracks; `Christmas/Sequences/Holy Forever 2026/Timing Templates/Holy Forever Lyrics 1.xsq` is the full-lyric recovery track; `Christmas/Sequences/Holy Forever 2026/Timing Templates/Holy Forever Intro Choir.xsq` contains the preserved intro track. The main pipeline is `Christmas/Sequences/Holy Forever 2026/Tools/build_lyrics.py`; `Christmas/Sequences/Holy Forever 2026/Tools/add_intro_holy_choir.py` is the older intro-track builder. Phrase *starts* are approximate (clamped to section anchors); word ends track the vocal closely. The "Holy holy holy" echoes in C3 are folded into the "To the King of kings holy" phrase end.

## Added 2026-07-18: drum / mood / section timing tracks (6) — plus Piano Chords + Piano Notes 2026-07-19 → **12 timing tracks total**

Template `Christmas/Sequences/Holy Forever 2026/Timing Templates/Holy Forever Drums and Mood.xsq`, built by `Christmas/Sequences/Holy Forever 2026/Tools/build_timing_template.py` (band-limited spectral-flux onset detection on `Christmas/Sequences/Holy Forever 2026/Tools/holy_44k.wav`, gated per 16th slot of the TRUE 600-anchor grid, kick/snare validated by onset-spectrum template matching, crashes by a ring/sustain test). Imported once via `importXLightsSequence` (auto, no media) and verified mark-for-mark (`Christmas/Sequences/Holy Forever 2026/Tools/verify_timing_import.py` — all 6 OK). All marks snapped to 25 ms. Hit tracks are contiguous: unlabeled gap fillers + short labeled hit marks (Kick=`K` 150 ms, Snare=`S` 150 ms, Cymbals=`C` 400 ms) — sequencers key effects off the labeled marks.

(Current total: full **`Lyrics 1`** + 3 per-voice lyric tracks + Intro Choir + these 6 tracks + **`Piano Chords`** + **`Piano Notes`** = 13.)

- **`Song Sections`** — 15 labeled blocks on the original effect-section boundaries (Intro 0 / Verse 1 15520 / Pre-Chorus 1 41850 / Chorus 1 67570 / Verse 2 95100 / Chorus 2 127630 / "Hear Your People" female feature 154150 / Holy Forever 166850 / Pre-Chorus 2 pass 1 181900 / pass 2 full cast 207210 / Final Chorus 234230 / Hear Your People 260760 / Holy Forever 273650 / Outro solo tag 287290 / Final hold 301500).
- **`Mood`** — 12 labeled energy arcs on true-grid downbeats: Ethereal 0 → Intimate 13900 → Building 40600 (bass+kick enter, RMS jumps ~4 dB) → Anthemic 67275 → Groove 93925 (kit settles, backbeat starts) → Soaring 127275 → Featured 153925 → Regather 180600 → Climbing 207275 → Climax 233925 (loudest stretch of the song) → Afterglow 287275 (band falls away; low band drops ~19 dB at bar 87) → Silence 300600.
- **`Beat Count`** — 370 marks labeled 1–4 on the corrected grid (first beat 600, last snapped to 308300). Bars = marks labeled `1`.
- **`Kick`** — 123 hits (none in V1 — the verse percussion is muffled strums, kick proper enters at PC1). Mostly beats 1/3 + driving eighths; densest in PC2a/PC2b.
- **`Snare`** — 116 hits: steady 2-and-4 backbeat from V2 (93933) through C3c end (~286850) — grid-locked when the flux peak is weak, peak-snapped when credible — plus strong fills (the V2 pickup bar included). No backbeat before V2 (V1/PC1/C1 have no snare groove; C1's only marks are the two build-in hits at 90600/93100 area) and none in OUT.
- **`Cymbals`** — 38 crash/ride-bell hits that pass the ring test; sparse by design (section starts, chorus punctuation).
- Audition mix (song ducked + synthetic clicks at every mark): `Christmas/Sequences/Holy Forever 2026/Tools/holy_drum_audition.mp3` (kick=80 Hz thump, snare=noise burst, cymbal=6 kHz ping). Regenerate with `Christmas/Sequences/Holy Forever 2026/Tools/audition_clicks.py`.
- ⚠ Per the root AGENTS.md rule: these tracks are now IN the sequence — never re-import this template (duplicated marks). Rebuild-and-hand-fix in the GUI if they ever need changing.
- Analysis scratch tools (kept): `analyze_drums.py`, `grid_drums.py`, `backbeat_scan.py`, `phase_check.py`/`phase_check2.py`, `anchor_check.py` (the anchor-correction evidence), `extract_marks.py`, `refine_marks.py`, `build_drum_marks.py`.

## Singing faces (casting) — LIVE in the sequence

Effect-block implementation of the vocal-arrangement table above.

The original cast is user-approved ("they were perfect"; do not remove). Standard singers use layer 0; the PiXeL Paradise prop uses layers 1–7 because each ornament/present/star is a separate face. **Eyes and mouths render white on every standard prop EXCEPT Teddy**, who keeps his forced-color face (`Teddy ` def: brown mouth, blue/brown eyes) per user preference. (`No Forced Colors` is an identical-nodes all-white def if ever wanted.) Bulbs use the 4-color C9 palette; Penguins keep their entire exterior white and color only their bellies as described below. Non-final blocks get +300 ms tails, final blocks +1500 ms tail with `T_TEXTCTRL_Fadeout=1.5`:

| Prop | Track | Blocks |
|---|---|---|
| GE 8ft Snowman Singing (lead) | Lyrics Lead | V1→C1; **verse 2 + all of chorus 2 as one block on `Lyrics 1`** (duets with Teddy from her 1:34 entrance, backs her up on C2b); PC2a→C3; outro solo |
| EFL Teddy (female lead) — def `Teddy `, **UseState `Teddy PinkBow`** (not red) | Lyrics Female (+ Lyrics Choir on C2a) | V2; **C2a**; C2b→C2c; PC2a→C3 — plus L0–L2 State expression (see Teddy section) |
| Singing Bulb - L/C/R (choir) | Lyrics Intro Choir (dim) then Lyrics Choir | **intro Holys + intimate V1** (`3900–41850`, muted ivory/gold palette, brightness 40); then C1; C2a→C2c; PC2b→C3 (full C9) |
| GE Santa Singing, GE Grinch Talk, SingingTree | Lyrics Choir | PC2a→C3 |
| Toni - Penguin 1/2 | Lyrics Choir | C1; C2a→C2c; PC2b→C3 (exactly matches the bulbs' chorus blocks) |
| PiXeL Paradise Xmas Tree Choir — Star + 5 Ornaments + Present | Lyrics Choir | C1; C2a→C2c; PC2b→C3 (exactly matches the Penguins) |

Verified saved spans after close/reopen: bulbs = `3900–41850`, `66700–91125`, `126725–178650`, `207775–285050`; Penguins and PiXeL Paradise = the latter three blocks. `chorus_choir_faces.py` safely rebuilds the Bulbs/Penguins and preserves the dim intro; `pixel_paradise_tree_choir.py` independently rebuilds the seven-face tree choir. `fix_faces.py` requires `Lyrics 1` (now present) but does not recreate the dim intro/V1 bulb block; do not use it for this targeted repair.

## EFL Teddy — pink bow + expressive States (LIVE 2026-07-19, branch `teddy-pink-expressive`)

Rebuild: `Tools/teddy_expressive.py` (`--dry-run` / default saves). Backup: `Holy Forever 2026.xsq.bak-before-teddy-expressive`.

Teddy keeps the forced-color face def `Teddy ` (brown mouth, blue/brown eyes). Costume state is **`Teddy PinkBow`** (pink bowtie/knot/shade — not `Teddy RedBow static`).

| Layer | Effect | Role |
|---|---|---|
| L0 | State arms (beat-driven + poses) | Beat-animated blocks (`Mode=Default`, `TimingTrack=Beat Count` — the 1–4 labels step the 1–4 states): `leaning (beats)` in V2/C2c, `flapping (beats)` in choruses/PC2, one-arm `left/right wave (beats)` on her C2b + C3b features and PC2b. Held `arms` poses (`mid`/`up`, Fade_Time 80) punctuate peaks: "amen", "Holy forever", "above them all", "Jesus", "lifted high", final raise into the fade. |
| L1 | State `eye direction` | up / upleft / upright / left / right — heavenward on worship lines; side glances in PC2 |
| L2 | State `Brows` | `sad` on V2 redemption lines; `highbrows` on praise; occasional `spockleft`/`spockright` in PC2 |
| L3 | Faces | mouth sync; `UseState=Teddy PinkBow`; Auto blink |

Faces blocks: V2 `Lyrics Female` → C2a `Lyrics Choir` (Female track has no C2a phrases) → C2b–C2c `Lyrics Female` → PC2a–C3 `Lyrics Female` (+1.5 s final fade). 93 effects (34 arm blocks). Script clears Teddy via .xsq (multi-layer) then re-adds — safe to re-run.

Beat-state recipe (verified against the vendor sequences that ship these defs — You Make It Feel Like Christmas, Happily Ever After, Can-Can): `E_CHOICE_State_Color=Graduate, E_CHOICE_State_Mode=Default, E_CHOICE_State_StateDefinition=<def> (beats), E_CHOICE_State_TimingTrack=Beat Count, E_SLIDER_State_Fade_Time=0`. The existing `Beat Count` track's 1–4 labels drive the animation — no new timing tracks were needed. (`Brows (Beats)` exists too but only defines states 1–2, so it's unused.)

## Bulb colors (C9 look — pure Faces palette, no submodel effects) — LIVE, part of the bulbs' face effects

The ChromaBulb defs map glass = `FaceOutline` and base = `FaceOutline2`, and with `CustomColors=0` the Faces effect assigns checked palette colors **in order: mouth, eyes, FaceOutline, FaceOutline2** (verified in `FacesEffect.cpp`). Each bulb's Faces palette is therefore:

- C1 `#FFFFFF` mouth · C2 `#FFFFFF` eyes · C3 glass (Left `#FF0000` / Center `#00FF00` / Right `#0000FF`) · C4 `#FFC800` amber base.

The bulb **submodel elements carry no effects** — an earlier submodel-On approach was removed; `fix_faces.py` wipes them to keep it that way. (Submodel names, if ever needed for non-face effects: Center = `Base`/`Bulb`, L/R = `Bulb Stem`/`Bulb Outline`.)

## Penguin colors (belly only — LIVE, pure Faces palettes)

`Penguin v.1.1 - No Tongue` uses `CustomColors=0`, so checked colors map in order to **mouth, eyes/wings, body/feet, belly**. Eyes and wings share one slot and therefore remain white together:

- **Hard user rule:** never color/cover the outside of either Penguin. Mouth, eyes/wings, body, and feet stay `#FFFFFF`; color is allowed only on `FaceOutline2` = the belly.
- **Toni - Penguin 1:** C1 mouth `#FFFFFF` · C2 eyes/wings `#FFFFFF` · C3 body/feet `#FFFFFF` · C4 belly burgundy `#9D1D25`.
- **Toni - Penguin 2:** C1 mouth `#FFFFFF` · C2 eyes/wings `#FFFFFF` · C3 body/feet `#FFFFFF` · C4 belly sapphire `#2864FF`.

Model-video review verified the exterior is white and only the belly is colored on both Penguins. They remain dark in the intimate intro, sing in C1/C2/PC2b/C3, visibly fade at 284.0 s, and are fully dark by 286.0 s. The Center bulb retained its dim intro treatment, switches to green glass + amber base in every chorus, and follows the same final fade.

## PiXeL Paradise Xmas Tree Choir (seven simultaneous faces — LIVE, preview pending approval)

Exact target: **`PiXeL Paradise Xmas Tree Choir`** (not `Toni - Flat Tree` and not `SingingTree`). All seven built-in CustomColors faces sing simultaneously on `Lyrics Choir`: `Star`, `Blue Ornamnet` (canonical typo), `Green Ornament`, `Red Ornament`, `Yellow Ornament`, `Purple Ornament`, and `Present`.

- Faces occupy parent layers 1–7 at brightness 82 and use their designed ornament/present colors; all share the Penguin spans and fades.
- Supporting submodel Ons make the full prop read without overpowering the faces: `Tree Outline` muted evergreen `#0B6B3A` at b38, `Candy Canes White Stripes` ivory `#EEEAE2` at b52, and `Candy Canes Red Stripes` burgundy `#9D1D25` at b48.
- Rendered/model-reviewed at C1, C2, C3, and the final fade. It is open in Slot A xLights for user review.
- Rebuild/clear: `Tools/pixel_paradise_tree_choir.py` (`--dry-run` / `--clear-only`).

## Added 2026-07-21: Rosa Grande C1 constant motion (branch `rosa-c1-constant-motion`, Slot A — pending user review)

First Rosa Grande feature. Window **67275–93925** (Anthemic Mood downbeat → Groove/V2 downbeat). Live version = **v2**: 4 slow continuous full-window effects, one per bank, each in its own traditional color.

- **v1 REJECTED same day** ("positively awful... It'll cause seizures"): 8 bar-downbeat Shockwave blooms (Snowflake Spoke) + 12 kick Shockwave stabs (Torch Long Even/Odd) over fast bases (Pinwheel speed-ramp 10→26, Spirals −6, Fan 720 rev), all warm gold. **Do not restore short Shockwave hits or fast rotation on the Rosa in this song.**
- **v2 REJECTED same day** (user: not using submodel render style the way Xtreme does): flat Overlay-Centered bases (Pinwheel/Spirals/Fan/Twinkle, one color pair each) ignore the prop's real geometry.
- **v3 (LIVE — user-approved "much better" 2026-07-21)** — direct port of the pros' Rosa stacks in `/Volumes/Personal-Drive/xlights/Christmas/The Christmas Song .xsq` (their ballad: ONE long slow effect per bank, 4–6 banks per ~27 s section, stacked mirrored pinwheels on the whole-prop GRP as the hero move):
  - `GE Rosa Grande GRP` **L0+L1**: identical slow 2-arm **3D-Inverted twisted Pinwheel** (ArmSize 271, Twist −65, Speed 3, Thickness 40, Blur 3), **`Per Model Per Preview` + `PerPreviewCamera=2D`**, L1 adds `BufferTransform=Flip Horizontal` → the two sweeps counter-rotate through each other over the prop's real geometry. Gradient palette red→gold→green.
  - `Torch Long Even GRP` L0: slow 4-arm Pinwheel (Thickness 82, Speed 2, Twist −60), Per Model Per Preview 2D, deep red `#B01212`.
  - `Spoke GRP` L0: Fan, Overlay-Centered, **overscanned End_Radius=333**, Blur 2 (their exact recipe), gold `#FFD89A`.
  - `Feather Long Odd GRP` L0: Spirals rot 20 / move 4, Overlay-Centered + Flip Horizontal, evergreen `#0B6B3A`.
  - `Outer Ball GRP` L0: SingleStrand `Bounce from Left`, 8 rotations across the chorus, 2.5 s fades, Rosa amber (`#FFD89A`) — no white on house-face spinners (2026-07-21).
  - **Key style lesson (measured, 64 sequences):** the pros' Rosa continuous-motion vocabulary is Per Model Per Preview (+2D camera, often Blur + Flip-Horizontal mirror pairs) for pinwheels through the geometry; Overlay-Centered for Spirals/Fan/chases; `Vertical Per Model/Strand` for SingleStrand drips on feather/torch/ball banks. Long effects = one per bank per section (~27 s), 2 s fades; NOT short hits.
- Owns the window on: whole GRP L0–L1 + the four banks' L0. `Web Ring GRP` untouched (V1 chord-bank effect). Rebuild: `Tools/rosa_c1_constant_motion.py` (`--dry-run` / `--clear-only` / `--rework` = clear all owned banks' window effects via direct .xsq edit [close → strip → reopen] then re-add).
- Backups: `Holy Forever 2026.xsq.bak-before-rosa-c1` (pre-v1), `.bak-before-rosa-c1-v2` (v1 state), `.bak-before-rosa-c1-v3` (v2 state).

## Added 2026-07-21: Starlords C1 constant motion (branch `rosa-c1-constant-motion`, Slot A — pending user review)

Blue-led companion to the approved Rosa C1 treatment — same window (67275–93925), same style rules (long slow geometry-aware effects, 2 s fades, no hits), **contrasting motion**, ported from the pros' Starlord verse stack in The Christmas Song. Both fixtures via the shared GRPs. 6 effects:

- `GE Starlord GRP` **L0**: Fan Per Model Per Preview 2D + Blur 2, overscanned radius 333, gold — runs UNDER the pinwheel pair (their exact verse trio).
- `GE Starlord GRP` **L1+L2**: identical fat 4-arm **3D** Pinwheel (Speed 2, Thickness 82, **Twist value-curve wobble** — verbatim pro curve), Per Model Per Preview 2D, L2 Flip Horizontal → counter-rotating pair. Blue gradient (sapphire→amber; no white). Contrast vs Rosa: fat upright 3D arms with wobble vs Rosa's thin 3D-Inverted −65° twist sweeps.
- `Plunger All GRP` L0: Spirals on **`Vertical Per Model/Strand`** — each plunger drips its own spiral (their exact recipe), sapphire `#2864FF`. ⚠ this layer also holds the V1 chord Shockwave @22225 (outside the window — rework only clears window effects).
- `Spoke GRP` L0: SingleStrand Left-Right, 3 chases, rotations 4, Vertical Per Model/Strand (TSO recipe slowed), Rosa amber.
- `Cross GRP` L0: SingleStrand From Middle drip, Vertical Per Model/Strand (Imperial recipe slowed), ice blue/sapphire.
- Rebuild: `Tools/starlord_c1_constant_motion.py` (`--dry-run` / `--clear-only` / `--rework`, same .xsq-clear pattern as the Rosa script).
- Backup: `Holy Forever 2026.xsq.bak-before-starlord-c1`.

## Added 2026-07-21: Reel Maxes C1 constant motion (branch `rosa-c1-constant-motion`, Slot A — pending user review)

Third spinner in the C1 set (Rosa red-led approved, Starlord blue-led). Blue-led like the Starlords, same window (67275–93925) / rules (long slow, 2 s fades, no hits), Reel Max's own measured vocabulary (crisp Twist=82 pinwheel + linear chases on ring banks). Both fixtures via shared GRPs. 6 effects:

- `GE Reel Max GRP` **L0+L1**: mirrored 4-arm 3D Pinwheel pair, fixed **Twist 82 / Thickness 47** (the pros' signature Reel Max whole-prop pinwheel, slowed to Speed 3), Per Model Per Preview 2D, L1 Flip Horizontal. Same sapphire→amber gradient as Starlord (no white).
- `Spokes GRP` L0: thin Spirals (Rot 85, Thick 10, Move 4, flipped) — spoke shimmer, Rosa amber.
- `Chevrons GRP` L0: SingleStrand Left-Right rot 4 (their Christmas Song chevron recipe), ice blue/sapphire.
- `Kites GRP` L0: SingleStrand Bounce rot 3 (TSO recipe), sapphire.
- `Circles Outer GRP` L0: SingleStrand on **Vertical Per Model/Strand** rot 8 — each circle drips individually (I Saw Mommy recipe), gold. ⚠ layer also holds the V1 chord Shockwave @28850 (outside window).
- Rebuild: `Tools/reelmax_c1_constant_motion.py` (`--dry-run` / `--clear-only` / `--rework`).
- Backup: `Holy Forever 2026.xsq.bak-before-reelmax-c1`.

## Added 2026-07-21: C1 Mini Grand glowing cross (branch `holy-c1-flakes-blue-amber`, Slot A — pending user review)

Intro Pictures image (`Glowing Cross.png`, Scale To Fit, white) on **`GE Mini Grand Illusion`** L0 for Song Sections Chorus 1 (**67575–95100**), 2 s fades. **Render style hand-tuned to `Per Preview`** (default did not paint). Rebuild: `Tools/c1_mini_grand_cross.py` (`--dry-run` / `--clear-only` / `--rework`).

## Added 2026-07-21: C1 Mega Tree cross + blue/amber Aurora shader, amber sparkle star (branch `holy-c1-flakes-blue-amber`, Slot A — pending user review)

User ask: "cross in the foreground and some cool shader that uses the blue and amber color" for the chorus, on the Mega Tree + star. Window 67275–93925 (same as the other C1 sets), 2 s fades, ballad dosage (3 long effects, no hits).

- **`Mega Tree` L1**: intro `Glowing Cross.png` Pictures (Scale To Fit, white) with **`E_CHECKBOX_Pictures_TransparentBlack=1` (threshold 30)** so the shader beneath shows around the cross. L1 also holds the PC1 meteors — they end before this window; script only owns the window.
- **`Mega Tree` L2**: `Aurora.fs` **Shader**, `uColMode=Alternate Color Palette (3 used) ` (maps palette slots 1–3 → shader r/g/b: amber `#FFC800` on the pulsing r, dim navy `#0A1E50` on g, sapphire `#2864FF` on the hot b channel — verified in shader source), `Shader_Speed=50`, intensity 80. Renders as slow blue ribbons with amber pulses behind the warm gold cross.
- **`Tree Topper` L3**: steady amber (`#FFC800`) **On** at b70 with ivory sparkles (`C_SLIDER_SparkleFrequency=40`) — user rejected the aurora on the star same day ("just make it be that amber color with sparkles"). Its existing L1/L2 white On bass pops render over it.
- Shader: **`Media/Shaders/Aurora Solid.fs`** — user rejected stock `Aurora.fs` ("don't like the hole in the middle"), then a clamped-inversion fix (still a center "bubble" — any radial math leaves circular structure), then v2's motion ("not moving like the other one did" — the inversion was what amplified motion). **v3 (LIVE):** no radial math (constant `p *= 1.09` zoom + PI/60 rotation per tap, output `col*0.13 − 0.18`) **plus per-layer time speed** `TIME*(0.45 + 0.18*i)` in the sine phase so the 18 curtains slide at different rates (parallax). Effects run `Shader_Speed=60`. Motion validated numerically: mean |Δframe| over lit pixels ≈0.085 vs stock 0.086 (v2 was 0.036). All variants prototyped offline with a numpy emulation of the GLSL before touching xLights (grid-render the math; check ring-wise luminance for holes, frame-pair deltas for motion). Stock `Aurora.fs` kept alongside for reference; both git-tracked. ⚠ The saved `.xsq` references the **slot-a absolute path** for the shader and this cross image (the permanent slot path renders fine from any instance; xLights only relativized the intro cross, not these).
- Pro shader survey (share `.xsq`s): shaders always run on `Default` buffer; Mega Tree/Tree Topper favorites there are Spacels/Lightning Flash/Black Cherry Cosmos/Aurora/Voronoi Spiral Vortex; `Everybody Loves Christmas` uses long low-intensity Silexars beds like this.
- Rebuild: `Tools/c1_megatree_cross_shader.py` (`--dry-run` / `--clear-only` / `--rework`). Backup: `Holy Forever 2026.xsq.bak-before-c1-megatree-cross-shader`. Preview: `RenderCompare/holy_forever_c1_megatree_cross_shader.mp4` (33 s C1 clip; `_full.mp4` = whole song).

## Added 2026-07-21: C1 snowflakes — Aurora shader per flake (branch `holy-c1-flakes-blue-amber`, Slot A — pending user review)

- **v1 REJECTED:** per-bank washes + Kick Twinkles on Outline/Spokes/Arms — wrong look, heavy.
- **v2 REJECTED (same day):** sapphire Color Wash (`Single Line`) + Color-panel music sparkles — replaced after the Mega Tree aurora was approved ("apply the same shader to the snowflakes, render per model per preview, instead of the blue with sparkles").
- **v3:** `Aurora Solid.fs` on **`Flakes GRP`** L0 with `Per Model Per Preview` (each flake its own aurora) — superseded by the user's hand tune below.
- **v4 (LIVE — user hand-edited in the GUI 2026-07-21, "use what I did"):** same effect/palette but **`B_CHOICE_BufferStyle=Per Preview`** — ONE aurora field sweeps across all flakes as a group — with **continuous rotation `uRotate=-6083`** and **`uZoom=301`**. Window 67275–93925, blue/amber alternate palette (amber `#FFC800` / navy `#0A1E50` / sapphire `#2864FF`), Speed 60, intensity 220, 2 s fades. Script matches the live values verbatim — don't "correct" them. Stale part-bank C1 effects cleared. Outline L0 V1 Shockwave @32200 untouched.
- Rebuild: `Tools/c1_flakes_blue_amber.py` (`--dry-run` / `--clear-only` / `--rework`). Backup: `Holy Forever 2026.xsq.bak-before-flakes-aurora` (v2 state).

## Added 2026-07-21: BMOAW C1 constant motion (branch `holy-c1-house-icicles`, MERGED to main)

Red/amber companion for both `BMOAW Left`/`Right` via shared `GE MOAW * GRP` banks — same C1 window (67275–93925) / ballad rules (long slow, 2 s fades, no hits, no white).

- **v1 REJECTED** ("looks like shit"): guessed Rosa-style `Per Model Per Preview` pinwheels/chases on MOAW — wrong. Pros' mapped MOAW continuous motion does **not** use PMPP; surveyed 8 sequences.
- **v2 (LIVE):** measured render styles only:
  - `GE MOAW GRP` **L0+L1**: Hallelujah **default-buffer** 3D Inverted Pinwheel (7 arms, Speed 2, Twist 67, Thickness 80, Blur 4); L1 Flip Horizontal. Red↔amber gradient.
  - `Spokes GRP` L0: Carol **`Single Line`** SingleStrand Bounce + `Group_All=1`, Mix 28, rot 1.4, gold/red.
  - `Snowflake Spoke GRP` L0: Hallelujah **`Per Preview` + 2D** Galaxy, red/amber.
  - `Swag GRP` L0: Feliz **`Overlay - Scaled`** Bars (count 3, cycles 2), red/amber.
  - `Diamonds GRP` L0: corpus **`Single Line`** Color Wash, gold/red.
- Rebuild: `Tools/moaw_c1_constant_motion.py` (`--dry-run` / `--clear-only` / `--rework`).

## Added 2026-07-21: C1 house walls + icicles (branch `holy-c1-house-icicles`, Slot A — pending user review)

Idea 1 from the Xtreme house/icicle pass: Rosa-red reveal motion on the house, same Anthemic window as the C1 spinners (**67275–93925**), 2 s fades, no hits / no brightness breath.

- `Verts` / `Roof`: L1 Rosa red (`#B01212`) **Color Wash** (b80) + L0 sparse **Marquee** (`Single Line`) with **`1 reveals 2`** + Rosa amber (`#FFD89A`) mask.
- `Windows` group (outline frames — Bottom Left / Play Room / Garage / Bedroom / Entry / Front Door): same L0/L1 reveal with **`Per Model Per Preview` + `PerPreviewCamera=2D`** (2026-07-21 — was per-member `Single Line`; user asked for the group + PMPP). Matrix panels empty (Holy Text deleted).
- `GE Merry Christmas/Christ`: white wash + white mask marquee. PC1 blinks (≤63875) untouched.
- `Icicles GRP`: same red wash, L0 Vertical Per Model **SingleStrand** drip (rot 3) with **`1 reveals 2`** + amber mask.
- Rebuild: `Tools/c1_house_icicles.py` (`--dry-run` / `--clear-only` / `--rework`; also clears stale per-member window + flake C1 leftovers).

## Added 2026-07-20: C3 climax drum-riff — dramatic `House Outline` strobe flash

**User request (3 iterations):** (1) "show that hard drum riff, like 8 hits... a single line effect just on the roof line where it changes directions with each hit" → Roof-line Marquee, disliked; (2) "Let's use shockwaves... on individual snowflakes on the roof instead" → 8 Shockwave pops on individual roof-snowflake props, disliked ("too subtle"); (3) **"Let's use house outline instead. Just flash it, fairly dramatically."** Live version is (3).

- **Timing correction after user review:** the first build guessed 8 eighth notes from the beat grid (**233925–236850**) and did not match the audible riff. Do not restore those times. Targeted analysis of `holy_44k.wav` around 232.6–235.1 s (1024-point STFT, 128-sample hop, combined low/tom/attack spectral flux) found the actual fill as **8 consecutive ~16th-note transients straddling the 233925 Climax downbeat**: raw peaks **233287.9, 233494.0, 233697.1, 233909.0, 234112.2, 234321.2, 234536.0, 234742.0 ms**; live 25 ms-snapped starts = **233300, 233500, 233700, 233900, 234100, 234325, 234525, 234750**.
- **Effect:** one full-brightness white **On** flash per measured hit on the whole **`House Outline`** group L0 (26-model group = walls + roof + icicle eaves — the entire house silhouette). Each flash keeps the user-approved shape at **175 ms** (7 frames), `T_TEXTCTRL_Fadein=0` (instant snap on) / `Fadeout=.15` (quick decay); the corrected fast spacing leaves 25–50 ms dark gaps between hits.
- Owns `House Outline` L0 only inside the 8 short hit windows; layers 1–3 remain empty (untouched, same as the pre-existing baseline).
- Rebuild/idempotent tool: `Tools/climax_house_flash.py` (`--dry-run` / `--clear-only`). Superseded/removed: `climax_drum_riff.py` (Roof-line Marquee) and `climax_snowflake_shocks.py` (roof-snowflake Shockwaves) — both deleted, do not recreate.
- Built on branch `climax-drum-riff` in **Slot B** (Slot A was in use for other work when this task restarted, so it moved here rather than colliding with it — the Slot A copy of the earlier attempts was fully reverted).
- Backup: `Holy Forever 2026.xsq.bak-before-climax-drum-riff` (taken before the very first Roof-Marquee attempt; still valid as a pre-this-feature snapshot).
- Preview: `RenderCompare/holy_forever_climax_house_flash.mp4` (7 s clip centered on the riff).

## Added 2026-07-20: subtle blue House Outline marquee across the Final Chorus

- One slow sapphire-blue (`#2864FF`) **Marquee** on `House Outline` L1 from **234225–287275 ms**: starts exactly with the live `Song Sections` = `Final Chorus` label and ends at the `Mood` Climax→Afterglow boundary.
- Uses `Single Line` so the 26-model house group reads as one coherent outline rather than scattered segment chases. Narrow/sparse recipe: band 4, skip 9, thickness 2, speed 2, `.60` fade in / `.75` fade out.
- Custom palette brightness curve breathes only **38→46→38** within each bar: midpoint dips and peaks on every live `Beat Count` bar downbeat from **237275 through 283925**. The effect enters 300 ms after the preceding 233925 downbeat and the final 287275 boundary is the next downbeat under the fadeout. This is intentionally super subtle.
- L0's eight dramatic white drum-riff flashes at 233.3–234.9 s are preserved; the marquee begins under the final flashes but remains isolated on L1.
- `Tools/climax_blue_house_marquee.py` (`--dry-run`) adds/verifies the live version. It also recognizes and replaces the superseded 273650 start via one targeted closed-sequence delete followed by API re-add; any other L1 contents cause a refusal.
- Backup: `Holy Forever 2026.xsq.bak-before-final-chorus-marquee`.
- Built on branch `holy-climax-blue-marquee` in **Slot B**.

## Tools inventory (`Christmas/Sequences/Holy Forever 2026/Tools/`)

- `transcribe.py` — faster-whisper word timestamps (needs a venv with `faster-whisper`; use `vad_filter=False` — VAD ate this vocal).
- `words.json` — transcription output (kept; lets you rebuild timing without re-transcribing).
- `build_lyrics.py` — alignment + phonemes + writes the 3-track per-voice template and `sections.json`. Canonical lyrics and per-voice membership live at the top of this file.
- `sections.json` — per-section/per-line sung spans (used by all placement scripts).
- `chorus_choir_faces.py` — targeted, idempotent Bulb + Penguin chorus rebuild; preserves/validates the dim intro bulb block, restores bulb C9, applies belly-only Penguin colors, verifies, then saves.
- `pixel_paradise_tree_choir.py` — seven PiXeL Paradise faces + subdued tree/candy-cane support, matched exactly to the Penguin choir blocks.
- `teddy_expressive.py` — wipe/rebuild EFL Teddy pink-bow Faces + arms/brows/eye-direction States for the whole female part (`--dry-run`).
- `fix_faces.py` — canonical C1+ all-face rebuild (includes bulb C9 + belly-only Penguin palettes and clears the bulb submodels). It requires the now-present `Lyrics 1` track but does not recreate the dim intro/V1 bulb block. **Does not rebuild Teddy's L0–L2 States** — use `teddy_expressive.py` for Teddy.
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
- `pc1_star_ascent.py` — Mega Tree `Meteors Up` on "name" pairs. **Superseded**; do not re-run unless restoring tree ascent.
- `pc1_star_descent.py` — **CURRENT** Mega Tree L1 `Meteors Down` on the four star-only (no-Christ) bass pairs.
- `pc1_house_name_chase.py` — **CURRENT** PC1 chase: Christ/sign + `Whole Scene w Matrixes` Implode toward Christ (includes house + matrices). Run after `cleanup_pc1_convergence.py`, then `pc1_star_descent.py`.
- `pc1_christ_convergence.py` — same Whole Scene recipe as house_name_chase (kept; either rebuilds Christ/scene/sign).
- `pc1_your_name_only.py` — direct .xsq trim from eight windows → four (close xLights first).
- `cleanup_pc1_convergence.py` — direct-delete reset for superseded PC1 effects/stubs before a clean rebuild; run `--dry-run`, close xLights, then run once.
- `climax_house_flash.py` — CURRENT owner of the C3 climax drum riff: 8 short, dramatic white strobe flashes on `House Outline` L0. `--dry-run` / `--clear-only`. (Superseded/deleted: `climax_drum_riff.py` [Roof-line Marquee], `climax_snowflake_shocks.py` [roof-snowflake Shockwaves] — both tried and rejected first.)
- `climax_blue_house_marquee.py` — add/verify the subtle sapphire `House Outline` L1 Marquee across the full Final Chorus; brightness breathes 38↔46 with the bar downbeats (`--dry-run`; safely migrates the superseded 273650 start only).
- `c1_house_icicles.py` — C1 `Verts`/`Roof`/`Windows`/`Christ` Marquee + `Icicles GRP` drip, Rosa-red `1 reveals 2` (67275–93925). `--dry-run` / `--clear-only` / `--rework`.
- `moaw_c1_constant_motion.py` — C1 BMOAW Left/Right red/amber constant motion via MOAW GRPs (67275–93925). `--dry-run` / `--clear-only` / `--rework`.
- `c1_flakes_blue_amber.py` — C1 `Flakes GRP` sapphire Color Wash + amber music sparkles (Color panel; 67275–93925). `--dry-run` / `--clear-only` / `--rework`.
- `c1_mini_grand_cross.py` — C1 `GE Mini Grand Illusion` Pictures Glowing Cross (67575–95100). `--dry-run` / `--clear-only` / `--rework`.
- `c1_megatree_cross_shader.py` — C1 Mega Tree cross-over-Aurora + Tree Topper aurora (67275–93925). `--dry-run` / `--clear-only` / `--rework`.
- `angels_cry_holy_text.py` — **refuses** rebuild (Holy Text deleted 2026-07-21). `--clear-only` / `--dry-run` still work.
- `lantana_piano.py` — wipe/rebuild full-song True Piano on `Matrix - Lantana` (`--dry-run` / `--clear-only`). **Removed 2026-07-19 (user: not working) — refuse to re-run its build mode; `--clear-only` is safe/idempotent.**
- `migrate_christ_submodel.py` — historical one-shot Christ-submodel migration; **do not run** (its four lyric glows were superseded by bass blinks).
- `migrate_faces.py`, `place_faces.py`, `lead_backup_c2.py` — historical; superseded by `fix_faces.py`.
- **REFUSE / deleted:** `holy_forever_2026.py`, `holy_forever_2026_wind_intro.py`, `holy_forever_2026_intro_snow.py`, `snare_reverse_marquees.py`, `reverse_v2_house.py`; deleted `migrate_matrixes_snow_to_windows.py`.

## Review checklist (baseline — do not “restore” removed bits)

0:00–0:42 Whole Scene snow + Mega Tree cross + dim bulbs; Penguins + PiXeL Paradise dark · 0:15 Snowman + arch piano chords + shrub-bank piano notes + oak cymbal Twinkles · Lantana empty · Projector/Entry/Downstairs empty (script Holy Text removed 2026-07-21) · C1 (1:07–1:34): `Verts`/`Roof`/`Windows`/`Christ`+`Icicles GRP` Rosa-red reveal + BMOAW red/amber + `Flakes GRP` rotating blue/amber Aurora Solid shader (Per Preview, whole roof as one field) under the spinner beds + Mega Tree cross-over-aurora with amber sparkle star · House Outline dark except 8 dramatic white strobe flashes at 3:53 and the subtle blue bar-breathing Marquee across 3:54–4:47; Roof = final hold only; Tree Topper accents kept · C1/C2/PC2b→C3 Bulbs + both white-exterior, belly-accented Penguins + all seven PiXeL Paradise faces sing together · 4:47 Snowman outro solo.
