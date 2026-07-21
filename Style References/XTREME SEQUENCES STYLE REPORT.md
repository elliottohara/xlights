# Building Sequences in the Xtreme Sequences Style — Agent Playbook

**Goal of this document:** guide an agent building a NEW sequence on Elliott's Christmas layout to produce work in the style of [Xtreme Sequences](https://xtremesequences.com/sequences/christmas-sequences) — the vendor behind most of the purchased sequences in this show, and the style Elliott wants. It is a *how-to*, not an inventory. Every rule below was extracted by analyzing 18 original vendor packages (`/Volumes/Personal-Drive/xlights/Imports/xS_*`, 62k effects) plus 38 Xtreme sequences already mapped onto this exact layout (`/Volumes/Personal-Drive/xlights/Christmas/*.xsq`, 125k effects). Evidence and inventories are in the appendices; regenerate stats with `Tools/analyze_xtreme_sequences.py`.

Use this together with `AGENTS.md` (API workflow, layout gotchas, user preferences). Where the two conflict, AGENTS.md wins — though note the pros' mapped files independently agree with the house rules (they use `Verts` not `House Outline`, Faces only on singing props, floods as color beds).

---

## The one-sentence style

**Sequence body parts, not props; lock every effect start to an instrument timing mark; keep a tiny effect vocabulary but fire it relentlessly; put art on the matrices and rhythm on everything else.**

---

## Step 0 — Classify the song and set a budget

Pick the closest template. These budgets come from measured pro sequences on this layout (~3–4 min songs):

| Song type | Total effects | Typical layers | Reference (mapped, on this layout) |
|---|---|---|---|
| Ballad / worship / crooner | 600–1,300 | 1–2, a few 3+ | `We Three Kings`, `The Christmas Song`, `O Come O Come Emmanuel` |
| Mid-energy pop / cheerful | 1,800–2,900 | 2–4, heroes 6–8 | `Hark The Herald Angels Sing`, `Home for the Holidays`, `Takin' Care Of Christmas` |
| Rock / orchestral power | 4,300–8,600 | 4–8, heroes 12–18 | `We Will Rock You`, `TSO Chistmas Medley`, `01 - The Imperial March` |
| Groove / novelty / rap | 4,000–7,000 | matrix stacks huge (40+), yard moderate | `Snoop Winter Wonderland `, `Twas the Night…`, `Little Drummer Boy` |
| Faces feature | 300–500 | 2 | `01 - Grandma Got Run Over By A Reindeer` (380 Faces effects, 4 props, nothing else) |

Don't inflate a ballad. The pros' quiet songs are *sparse but wide*: only 1–2 layers, long fades on nearly every effect (`We Three Kings`: fadein+fadeout on ~75% of 1,305 effects), yet 40–70 elements still participate.

## Step 1 — Build per-instrument timing tracks FIRST

Every modern Xtreme sequence ships far more than `Beats`: they separate **Kick, Snare, Toms, cymbals, hat, bass, piano, Guitar, Piano Solo, Synth Punches, Intro High/Low Bells**, plus `Note Onsets` split by instrument (`Note Onsets Piano/Other/Drums`) and per-voice lyric tracks (`Male`/`Female`/`Backup Vocals`, `Lyrics 1..4`). Some ship `Tree 1–4` tracks for per-mini-tree choreography.

This is the exact approach already proven here (Holy Forever drum timings, Feliz Navidad horn/string tracks) — keep doing it. The payoff is measurable: in `Fight Song`, **100% of effect starts land within one frame of a timing mark**. Nothing free-floats, ever.

**Rule: every `addEffect` startTime must be a mark from some instrument track, and each visual voice follows ONE instrument** (kick → one bank, snare → another, piano runs → chases). Hit *density* then automatically follows the music.

## Step 2 — Plan the matrices first, then the yard

On this layout ~30% of all pro effects live on four surfaces: `Matrix - Entry` (workhorse: Morph tails + Pictures art), `Matrix - Downstairs Window`, `Matrix-Garage Window`, `Matrix - Lantana`. Decide the matrix story per section (video clip? Morph tail-chase? shader? lyrics as Text?) before touching the yard. The yard then plays rhythm around that anchor.

Matrix content by era/energy: Video + Pictures for novelty songs, Morph tail-chases + Ripple for emotional builds (`Hallelujah` runs a 95-layer Morph/Ripple stack on the entry matrix), Shader/Warp for intensity. `Projector` and `Tune To` get the same treatment (Text/Video/Shader).

## Step 3 — Cast the elements (this layout's roles)

Assign roles the way the pros consistently do on this exact display:

- **Hero / accent:** `Mega Tree` (deep stack), `Tree Topper` (hit target in 33/38 sequences — don't forget it), `Toni - Flat Tree` (first-class prop, 28/38), `GE Merry Christmas` (pulse it like an instrument — Shockwave-heavy).
- **House rhythm:** `Roof`, `Windows`, `Verts` — Shockwave + SingleStrand chases. Windows can move during high-energy sections (pros do), but respect the standing rule: no face outlines, default to warm glow in calm sections.
- **Linear sweeps:** `Arches - All` (the single most-used element, 36/38 — SingleStrand-first), `Icicles GRP`, `Canes`, `Colums`, `Column Matrixes` (C1–C6 as one bank), `Driveway`, `Yard Borders`.
- **Count patterns:** `Mini Trees` and `Mini Tree Stars` are TWO separate voices (trees = body hits, stars = sparkle answers). Same for `Large Spiral Trees` (12 units — great for runs).
- **Color beds + punches:** `Floods GRP` = On/Color Wash only, never patterned. `Colum Shrubs` needs motion (marquee/twinkle), never static fills.
- **Spinner part-banks:** see Step 4 — this is the heart of the style.
- **Faces:** only on the actual singing props (`SingingTree`, `Singing Bulb - L/C/R`, `GE Grinch Talk`, `GE 8ft Snowman Singing`, `EFL Teddy`, `Toni - Penguin 1/2`, `GE Santa Singing`), driven by the per-voice lyric tracks. White mouths/eyes except Teddy (see AGENTS.md).
- **Whole-scene groups:** sub-second slams on downbeats only.

## Step 4 — Choreograph part-banks, never whole spinners

The core Xtreme move. In their HD-era work, 60–75% of the timeline is `<part> GRP` submodel groups; whole props barely appear. On this layout, use the proven A-list (ranked by how hard the pros lean on each across 38 mapped sequences — see Appendix B for the full table):

1. `GE Rosa Grande Ribbon GRP` — the most-used spinner bank on this display
2. `GE Baby Grand Illusion Spokes GRP` (+ `Snowflake Spokes`, `Flower`, `Hook CW`, `Rings`, `Whirlwig Even/Odd`)
3. **Starlord banks — the pros' favorite prop here:** `Plunger All/LG/SM`, `Spoke`, `Cross`, `Feather Even/Odd`, `Ribbon`, `Square`, `Z All`, `Star`, `Diamond`
4. `GE Reel Max`: `Outer Triangles`, `Spokes`, `Kites`, `Circles Inner/Outer`, `Chevrons`
5. `GE Rosa Grande`: `Torch Long Even/Odd`, `Feather Long Even/Odd`, `Snowflake Spoke`, `Spoke`, `Ring`, `Web Spoke`
6. `Flakes Arms GRP` / `Flakes Spokes All GRP` / `Flakes Outline All GRP` (outline = glow base, spokes = hit, arms = chase-out)
7. `GE MOAW Snowflake Spoke GRP`, `GE MOAW Spokes GRP`, `GE MOAW Swag GRP`

How to use them:

- **Whole-prop group carries the base, part-banks take the hits.** Both coexist: e.g. slow Pinwheel on `GE Starlord GRP` layer 0, Shockwave stabs on `Plunger All GRP` above. The pros do this on the same props simultaneously.
- **Rotate which banks take each hit.** Measured pattern (Imperial HD): downbeat fires 2 banks, next accent fires 6 *different* banks 575 ms later, next bar rotates again. Never park one bank on every beat.
- **Even/Odd pairs alternate** — hit Even on beat 1, Odd on beat 3, or counter-rotate colors. The pros use them strictly as pairs (Torch Long Even 706 uses / Odd 486).
- **Pick 3–6 banks per prop per song**, not all of them. Different songs feature different banks.
- Unexplored on this layout (no pro sequence touches them): `Arches - Middle`, `GE Reel Max Arcs Even/Odd GRP` — safe territory for original moves.

## Step 5 — Layer architecture per element

Anatomy of a pro hero stack (measured on We Will Rock You's 18-layer Mega Tree, Snoop HD's 13-layer Priem Cube):

- **Top 1–2 layers: the base.** Long effects (3–24 s): Spirals, Fan, Pinwheel, Meteors, Shader. Sets the tone; changes per song section.
- **Middle 3–7 layers: hit layers.** Dense 300–825 ms Shockwave/Pinwheel/Warp/SingleStrand hits (median 725 ms). Multiple parallel layers exist SO OVERLAPPING ACCENTS NEVER COLLIDE — when two hits overlap in time, they sit on different layers.
- **Bottom layers: specials.** One-off Text, a 375 ms shockwave run, a Fan finale.

Non-hero elements: 2–4 layers (base + 1–2 hit layers). Ballads: 1–2 layers everywhere.

**Blending is choreography, not decoration.** The signature methods (corpus-wide counts):

- `2 reveals 1` / `1 reveals 2` (27k uses) — a *moving* effect on one layer reveals a *color field* on the other: motion draws the shape, the partner supplies the color. This is their default trick for colored chases/rings.
- Unmask family (`1/2 is (True) Unmask`, ~6k) — high-contrast effect stamps a moving window into a rich base. **VU Meter as unmask source = music-reactive color.**
- Newer era adds `Additive`, `Max`, `Min`, `Brightness` for stacking glows without blowing out.
- `T_CHECKBOX_Canvas=1` + Warp over composed layers below (the Dubstep trick) — used ~950× corpus-wide, heavily in Home Alone (667).

Almost no fancy transitions — just `T_TEXTCTRL_Fadein/Fadeout=.1–.5` on nearly everything. Fades are what keep thousands of short hits from strobing.

## Step 6 — The two bread-and-butter recipes (exact settings)

### Shockwave hit (37% of everything they do)

```
effect:  Shockwave
settings: E_CHECKBOX_Shockwave_Blend_Edges=1,E_NOTEBOOK_Shockwave=Position,
          E_SLIDER_Shockwave_Accel=0,E_SLIDER_Shockwave_CenterX=50,E_SLIDER_Shockwave_CenterY=50,
          E_SLIDER_Shockwave_Start_Radius=1,E_SLIDER_Shockwave_Start_Width=5,
          E_SLIDER_Shockwave_End_Radius=<13 small | 28 med | 42 large>,
          E_SLIDER_Shockwave_End_Width=<25 | 65 | 77>,
          T_TEXTCTRL_Fadeout=.25
duration: 375–825 ms, start ON a timing mark
buffer:   B_CHOICE_BufferStyle=Overlay - Centered        → ONE wave across the whole bank
          B_CHOICE_BufferStyle=Per Model Per Preview     → wave re-renders INSIDE each part (every spoke pulses) ← HD signature
          B_CHOICE_BufferStyle=Per Model Single Line     → each part as a line (messy wiring)
```

### SingleStrand chase (their linear workhorse)

```
effect:  SingleStrand
settings: E_NOTEBOOK_SSEFFECT_TYPE=Chase,E_CHOICE_SingleStrand_Colors=Palette,
          E_CHOICE_Chase_Type1=<Left-Right | Bounce from Left | Dual Bounce>,
          E_TEXTCTRL_Chase_Rotations=0.4–1.0,E_SLIDER_Number_Chases=1–4,
          E_SLIDER_Color_Mix1=10–42
duration: ~375 ms typical
buffer:   Vertical Per Model/Strand   → identical simultaneous drip down EVERY member (icicles, arches, feathers)
          Horizontal Per Model/Strand + E_CHECKBOX_Chase_Group_All=1 → one chase traveling ACROSS members in order
```

**Buffer style is chosen per musical job, not per prop** — the same GRP legitimately gets `Overlay - Centered` (boom), `Per Model Per Preview` (per-part shimmer), and `Horizontal Per Model/Strand` (traveling run) on different layers in the same song.

### Continuous motion on spinners — INSPECT RENDER STYLES FIRST (verified 2026-07-21 on Rosa + Starlord + Reel Max; user-approved on Holy Forever C1)

**⚠ Mandatory step for ANY Xtreme-style request:** before writing spinner effects, open real pro sequences on the share (`/Volumes/Personal-Drive/xlights/Christmas/*.xsq`) and read the **`B_CHOICE_BufferStyle` / `B_CHOICE_BufferTransform` / `B_CHOICE_PerPreviewCamera`** strings the pros used on the exact banks you're targeting (parse `EffectDB` refs — 5-line python, see the survey pattern in this section's history). Do NOT guess buffer styles from effect names. A flat `Overlay - Centered` Pinwheel reads as a generic square wash and was explicitly rejected by the user ("not using submodel render style the way Xtreme does"); the exact same effect with the right render style was approved ("much better" / "Perfect").

The measured pro vocabulary:

- **Pinwheels/Fans through the prop's real geometry:** `B_CHOICE_BufferStyle=Per Model Per Preview` + `B_CHOICE_PerPreviewCamera=2D`, usually `B_SLIDER_Blur=2-3`. This is what makes arms sweep along the actual spokes/torches instead of across an abstract grid (and, on multi-fixture GRPs, makes each fixture spin about its own center).
- **The mirror-pair hero move** (their signature): stack the SAME slow pinwheel on two layers, second one with `B_CHOICE_BufferTransform=Flip Horizontal` → two sweeps counter-rotate through each other. Give it a gradient palette so color travels along the arms.
- **`Overlay - Centered` is still correct** for Spirals / overscanned Fan (End_Radius ~333 + blur = blades wash rather than pop) / SingleStrand chases on radial ring banks; **`Vertical Per Model/Strand`** makes SingleStrand/Spirals render per-part (each plunger/torch/circle drips its own copy).
- **Ballad dosage:** ONE long effect per bank per section (~27 s), 4–6 banks at once, `T_TEXTCTRL_Fadein/Fadeout=2`, one color family per bank. No short hits — repeated sub-second Shockwave stabs were rejected as seizure-inducing on a worship song.
- **Per-prop motion signatures** (each spinner keeps its own character; contrast is the point):
  | Prop | Whole-GRP hero | Part-bank texture |
  |---|---|---|
  | Rosa Grande | thin 2-arm `3D Inverted` sweeps, ArmSize 271, Twist −65, Speed 3, Thickness 40, Blur 3 | Overlay Spirals on feathers, overscanned Fan on Spoke, bounce chase on Outer Ball |
  | Starlord | Fan (PMPP 2D, Blur 2) UNDER a mirrored pair of fat 4-arm `3D` pinwheels, Speed 2, Thickness 82, Twist value-curve wobble | `Vertical Per Model/Strand` Spirals on Plunger All (per-plunger drips), vertical chases on Spoke/Cross |
  | Reel Max | mirrored 4-arm `3D` pair, fixed Twist 82, Thickness 47, Speed 3 (crisp, no wobble) | thin Spirals (Rot 85/Thick 10) on Spokes, Left-Right/Bounce chases on Chevrons/Kites, per-circle vertical drip on Circles Outer |
- Working reference implementations (addEffect-ready settings strings, idempotent, with `--rework` .xsq-clear): `Christmas/Sequences/Holy Forever 2026/Tools/rosa_c1_constant_motion.py`, `starlord_c1_constant_motion.py`, `reelmax_c1_constant_motion.py`.

Beyond these two: Pinwheel/Galaxy/Fan for rotation, Spirals for tree bases, On for punches, Morph for matrix tails, VU Meter for reactivity. That's the whole vocabulary — resist exotic effects.

## Step 7 — Dynamics pass

- **Dark valleys between phrases.** The pros' loud songs go near-black between sections; contrast is the punch.
- **Downbeat slams:** stack the same hit on 5–10 banks at once (staggered 200–600 ms), or use `Whole Scene` for <1 s.
- **Builds:** add one layer/voice per 4–8 bars rather than turning everything on.
- **Endings:** a long Fan or Shader (13–24 s) as the final gesture is a repeated pro move.

## Build workflow recap (API)

Per AGENTS.md: `newSequence` → import timing template(s) (each track once) → `addEffect` everything (settings strings above are `addEffect`-ready) → `saveSequence` (full path) → `renderAll` → `exportVideoPreview`. Never `setEffectSettings`.

---

# Appendix A — Evidence: the vendor originals (Imports/xS_*)

18 packages, 62,157 effects / 1,367 sequenced elements, spanning 2017 → 2020-HD era.

**Evolution to part-banks:** elements that are submodel-groups: Classic Medley 2017 = 0/95 → Home Alone 2019 = 20/61 → Fight Song V2 2020 = 64/107, Imperial HD = 54/82, Snoop HD = 58/77. Their own layouts define 2,100–2,400 submodels and 120+ `<part> GRP` groups whose members are `Model/Submodel` paths. Direct `Model/Submodel` elements in sequences: zero — always via a GRP (the group provides the buffer).

**Part vocabulary** (submodel names across HD layouts): Spoke (669), Ring (258), Arm (244), Hook CW/CCW (200 ea), Arrow (122), Flower, Track, Circles, Diamond, Feather, Wiggly CW/CCW, Rib, Outer Leg, Bird, Outer Ball, Ribbon, Outline, Star, Cross, Square, Point, Crown. One prop = up to 11 sequenced banks (GE XLS in Imperial HD).

**Aggregate effect vocab:** Shockwave 23,090; SingleStrand 8,430; On 6,346; Morph 3,267; Galaxy 2,605; Fan 2,351; Pinwheel 1,995; VU Meter 1,758; Spirals 1,586; Color Wash 1,345; Pictures 1,229; then Warp/Wave/Marquee/Curtain/Shimmer/Meteors/Shader in the hundreds.

**Buffers:** Overlay-Centered 14,901; Vertical Per Model/Strand 5,247; Per Model Per Preview 3,659; Default 2,587; Per Preview 2,316; Horizontal Per Model/Strand 1,364; Per Model Single Line 517.

**Layer methods:** 2 reveals 1 (5,768), Average (4,325), 1 reveals 2 (2,339), Effect 1 (1,305), True Unmask variants (~2,000), Unmask (~1,600), Subtractive/Shadow/Mask accents.

**Timing:** `Beats` + `Note Onsets` in 16/18 packages; extras like Drums, Bass Drum, Intro High Bells, Lyrics, hand tracks. Fight Song: 633/633 effect starts within 1 frame of a mark.

**Per-package one-liners:** Fight Song V2 = purest HD (sparse, surgical, 64 banks); Imperial HD = shockwave bible + bank rotation; We Will Rock You = 18-layer hero stacks + fades everywhere; Home Alone Carol = linear-prop cascades (1,863 SingleStrand) + canvas Warp; Snoop HD = gentle shimmer/unmask groove; TSO = mega-tree orchestral builds (`1 reveals 2` ×1,692); It's Christmas Medley = brute shockwave-reveals (×4,139); Christmas Can Can = 144-layer Morph star stunt; Skrillex = uniform 6-layer dubstep stacks + 1,352 value curves; 2017 titles (Childrens/GhostBusters/SelfishElf/ClassicMedley/MonsterMash) = pre-submodel era, mostly useful as contrast.

# Appendix B — Evidence: 38 Xtreme sequences mapped onto THIS layout

Matched share `.xsq` files against the vendor's website catalog (84 filename matches → 38 unique analyzable sequences, mostly saved by xLights 2025.12). 125,252 effects, all in Elliott's element names. They use **101 of the layout's 120 submodel-groups**.

**Top elements** (effects / #sequences): Matrix - Entry 13,433/29 · Matrix - Downstairs Window 7,872/18 · Mega Tree 6,340/35 · Matrix-Garage Window 4,045/28 · Tree Topper 3,145/33 · Toni - Flat Tree 2,757/28 · Column Matrixes 2,498/26 · Mini Trees 2,184/35 · Roof 2,172/35 · Projector 2,142/30 · Verts 2,076/33 · Arches - All 1,970/36 · Flakes GRP 1,968/32 · GE Merry Christmas 1,900/26 · Windows 1,894/34 · Floods GRP 1,709/32 · Icicles GRP 1,659/28 · Large Spiral Trees 1,657/32 · Mini Tree Stars 1,626/26 · Canes 1,607/32.

**Submodel-bank A-list** (effects / #seqs): Rosa Grande Ribbon 1,331/26 · Baby Grand Illusion Spokes 1,068/20 · Starlord Plunger All 955/25 · Starlord Spoke 871/25 · Starlord Plunger LG 805/22 · Reel Max Outer Triangles 795/8 · Flakes Arms 729/21 · Starlord Cross 715/18 · Starlord Feather Odd 710/17 · Rosa Torch Long Even 706/21 · BGI Snowflake Spokes 689/12 · Reel Max Spokes 661/25 · Starlord Ribbon 657/23 · Rosa Feather Long Even 612/24 · Rosa Torch Long Odd 486/20 · Rosa Snowflake Spoke 464/16 · MOAW Snowflake Spoke 408/22 · Flakes Spokes All 333/21 · Reel Max Kites 317/16 · Reel Max Circles Outer 283/16 · MOAW Spokes 264/15 · Starlord Z All 232/13 · Rosa Ring 228/14 · BGI Hook CW 217/12.

**Element effect-mixes:** Roof = SW 826/SS 506/On 195 · Arches = SS 703/SW 498 · Floods = On 634/ColorWash 326 · Mini Trees = SW 882/SS 339 · GE Merry Christmas = SW 725 · Matrix-Entry = Morph 8,658/Pictures 2,212. Faces: SingingTree 403, Singing Bulbs ~70 each, Grinch/Snowman/Teddy/Penguins/Santa 40–63 — nothing on windows/walls.

**Newer-era (2022–2025 titles) shifts:** Morph 9,959 (matrix tail-chases; Hallelujah = Morph 3,869 + Ripple 2,259, 95-layer matrix element; Snoop remaster = 43–73-layer matrix stacks); new blends Additive 1,598 / Max 1,298 / Min 717 / Brightness 583; per-instrument timing tracks (Kick/Snare/Toms/cymbals/hat/bass/piano/Guitar/Synth Punches/per-voice lyrics/Tree 1–4); Video effects on matrices; `We Three Kings` = fade-everything ballad discipline (fades on ~75% of effects).

**High-signal reference files on the share** (by style): rock = `We Will Rock You` (8,574), `TSO Chistmas Medley` (8,055), `01 - The Imperial March` (4,557); matrix-art = `Hallelujah` (7,462), `Snoop Winter Wonderland ` (6,944 — trailing space in filename); cascades = `Home Alone` (6,710); percussion-On style = `Little Drummer Boy` (6,165); mid-energy = `Hark The Herald Angels Sing` (2,033), `01 - Takin' Care Of Christmas` (2,883), `Home for the Holidays` (1,844), `Happily Ever After` (1,752, Additive); ballads = `We Three Kings` (1,305), `The Christmas Song` (628), `Human Nature - White Christmas` (760); faces-feature = `01 - Grandma Got Run Over By A Reindeer` (385).

**Never touched by any pro sequence** (19 banks; excluding Halloween parts and test groups): `Arches - Middle`, `GE Reel Max Arcs Even GRP`, `GE Reel Max Arcs Odd GRP`, `Grand Illusion Hooks CW`, `GE Rosa Grande Torch Long V2 GRP`.

*Caveat:* the share's `xlights_rgbeffects.xml` differs slightly from the local repo copy (local has newer edits, e.g. `GE Merry Christmas/Christ`); all element names cited here were verified to exist in the current local layout.
