# Xtreme Sequences — Style Analysis Report

**Purpose:** Reference for future sequencing work. Elliott's favorite vendor is [Xtreme Sequences](https://xtremesequences.com/sequences/christmas-sequences); most purchased sequences in this show come from them. This report mines the 18 original vendor packages in `/Volumes/Personal-Drive/xlights/Imports/xS_*` (each ships its own `xlights_rgbeffects.xml` layout + sequence file) to document *why* their work looks good — especially their submodel technique — so agents can reproduce the style on Elliott's layout.

**How it was produced:** `Tools/analyze_xtreme_sequences.py` (in this repo) parses every vendor layout and sequence, classifies sequenced elements, and aggregates effect/buffer/layer statistics. Raw JSON output can be regenerated any time (`python3 Tools/analyze_xtreme_sequences.py out.json`). Analysis date: July 2026.

**Corpus:** 18 packages, 62,157 effects on 1,367 sequenced elements. Spans 2017 (`Selfish Elf`, `Ghost Busters`, `Classic Christmas Medley`) through the 2020 High-Density era (`Fight Song V2`, `Imperial March HD Add-On Pack`, `Snoop Winter Wonderland HD Add-On Pack`, `We Will Rock You`, `Christmas Every Day`, `Twas the Night Before Christmas V2`).

---

## 1. The core insight: they never sequence a prop — they sequence its parts

This is the single most important finding, and it grew over time:

| Era | Example | Elements that are submodel-groups |
|---|---|---|
| 2017 | Classic Christmas Medley | 0 of 95 |
| 2018–19 | Home Alone Carol | 20 of 61 |
| 2020 HD | Fight Song V2 | **64 of 107** |
| 2020 HD | Imperial March HD Add-On | **54 of 82** |
| 2020 HD | Snoop HD Add-On | **58 of 77** |

In the HD packs the sequenced timeline is *mostly submodel-groups*. Whole models barely appear (Fight Song: 18 of 107; Imperial HD: 15 of 82) and are usually matrices, mega tree, or the "All Pixels" wow group.

### 1a. The mechanism: `<part> GRP` model groups whose members are `Model/Submodel` paths

They define hundreds of submodels per prop in the layout (Fight Song layout: 2,115 submodels, 121 submodel-groups; Imperial HD: 2,378 submodels, 124 submodel-groups). Then they build a model group per *part-type*, spanning all fixtures of that type. Examples from Fight Song V2:

- `Eaves GRP` = `Ice 1/Eave Upper 1`, `Ice 2/Eave Upper 2`, … (12 house segments unified into one sweepable element)
- `Icicles GRP` = `Ice 1/Icicles 1` … `Ice 8/Icicles 8`
- `GE SpinReelMax Spokes GRP` = `GE MegaSpinReel Max/Spoke 1..14`
- `Starburst xTreme Point GRP` = `StarBurst xTreme/Point 1..8`
- `GE RosaWreath Feather Odd GRP` = `Feather 1,3,5,7,9,11,13,15` (odd/even splits are everywhere)

**Why groups instead of addressing submodels directly:** the group gives them a *buffer* across all the parts, so one Shockwave/SingleStrand/Pinwheel effect animates the whole bank coherently — and `Per Model` buffer styles then re-render that effect per part. In the sequences themselves, direct `Model/Submodel` elements are essentially never used (0 across all 18 packages). Everything goes through a named ` GRP`.

### 1b. Part-bank vocabulary (submodel taxonomy)

Across the HD layouts, submodel names collapse to a consistent part vocabulary — this is what they carve every spinner/flake/star prop into:

**Spoke** (669), **Ring** (258), **Arm** (244), **Hook CW / Hook CCW** (200 each — spiral arms in both directions), **Arrow** (122), **Flower**, **Track**, **Circle Inner/Outer Small/Large**, **Diamond**, **Feather**, **Wiggly CW/CCW**, **Rib**, **Outer Leg**, **Bird**, **Outer Ball**, **Ribbon**, **Outline**, **Star**, **Cross**, **Square**, **Point**, **Crown**.

Per prop they sequence **many separate banks**. In Imperial HD, one prop (`GE XLS`) gets 11 independently-sequenced banks (Arms, Arrows, Center, Drum Stick L/R, Outer Leg, Outline, Ring, Snowflake, Spokes); `GE Grand Illusion` gets 9 (Flower, Hook CW, Snowflake Center, Snowflake Spokes, Spokes Even, Spokes Odd, Whirliwig, Whirliwig Even, Whirliwig Odd). Fight Song carves its 6 flake styles into 24 banks (per style: Arms, Arrows, Circles, Spokes, Rings, Ribs, Bursts…).

**Takeaway for Elliott's layout:** this exactly matches the ` GRP` submodel groups already in `Christmas/xlights_rgbeffects.xml` (`GE Reel Max Arrows GRP`, `GE Starlord Plunger All GRP`, `GE Rosa Grande Hook CW GRP`, etc.) — those groups *are* the Xtreme pattern, imported. Use them as first-class instruments, several banks per prop, not the whole spinner.

---

## 2. Effect vocabulary — small, repeated relentlessly

Aggregate counts across all 18 sequences:

| Effect | Count | Role |
|---|---|---|
| Shockwave | 23,090 (37%) | THE signature. Short radial hits on every accent |
| SingleStrand (Chase) | 8,430 | Chases along linear parts and part-banks |
| On | 6,346 | Punch hits, holds, blocks of color |
| Morph | 3,267 | (mostly one sequence — Can Can's 144-layer star) |
| Galaxy / Fan / Pinwheel | 2,605 / 2,351 / 1,995 | Rotational motion on spinners & tree |
| VU Meter | 1,758 | Music-reactive layers ("On" type, level meters) |
| Spirals / Color Wash | 1,586 / 1,345 | Bases |
| Warp / Wave / Marquee / Curtain / Shimmer / Meteors | few hundred each | Texture and transitions |
| Shader | 250 | Matrices/mega-tree only, late-era |

The magic isn't exotic effects — it's ~10 effects, tightly parameterized, fired thousands of times on the right body parts at the right instant.

### 2a. The Shockwave recipe (extracted from Imperial HD, the heaviest user)

Nearly all Shockwaves share one skeleton, varying only end radius/width by prop size:

```
B_CHOICE_BufferStyle=Per Model Per Preview   (or Overlay - Centered / Per Model Single Line)
E_CHECKBOX_Shockwave_Blend_Edges=1
E_SLIDER_Shockwave_Start_Radius=1, Start_Width=5
E_SLIDER_Shockwave_End_Radius=13–42, End_Width=25–77
E_SLIDER_Shockwave_Accel=0, Center 50/50
```

- **`Per Model Per Preview`** on a part-bank GRP = the shockwave re-renders *inside each part* (each spoke/arm pulses individually) — this is the sparkling multi-fixture look.
- **`Overlay - Centered`** = one wave across the whole group (the group ripples as one).
- Typical duration: **375–825 ms**, median ~725 ms; on downbeats they stack the same hit on 5–10 banks at once with staggered starts 200–600 ms apart (measured: a chorus bar in Imperial HD fires `All Pixels`, `Priem Cube`, `SpinReel Max`, then six banks together 575 ms later).

### 2b. The SingleStrand recipe

Median duration **375 ms**. Chase type `Left-Right` / `Bounce from Left` / `Dual Bounce`, `Chase_Rotations=0.4–1.0`, 1–4 chases, palette colors. Buffer style is the trick:

- `Vertical Per Model/Strand` on `Arches GRP` / `Windows GRP` / part-bank GRPs → simultaneous identical drips/chases down every member (Home Alone Carol does this 1,863 times — arch cascades, window sweeps, feather runs).
- `Horizontal Per Model/Strand` with `Chase_Group_All=1` → one chase traveling across the members in sequence.

---

## 3. Buffer styles — the real submodel superpower

Aggregate usage:

| Buffer style | Count | What they use it for |
|---|---|---|
| Overlay - Centered | 14,901 | Radial hits centered on group (shockwaves, galaxies) |
| Vertical Per Model/Strand | 5,247 | Per-member vertical chases (icicle drips, arch fills) |
| Per Model Per Preview | 3,659 | Effect re-rendered per member using its preview location — the HD signature |
| Default / Per Preview | 2,587 / 2,316 | Whole-group canvas; Per Preview keeps geographic layout |
| Horizontal Per Model/Strand | 1,364 | Chase across members in order |
| Per Model Single Line | 517 | Treat each member as one line (uniform motion on messy wiring) |
| Layer Star / Overlaid X / Stacks | ~500 | Specialty tree/star buffers |

Rule of thumb from their work: **choose the buffer style per musical job, not per prop** — the same GRP will get `Overlay - Centered` for a boom, `Per Model Per Preview` for a shimmer-hit, and `Horizontal Per Model/Strand` for a traveling run, on different layers simultaneously.

---

## 4. Layering — deep stacks with mask/reveal choreography

- Hero elements go deep: **Mega Tree in We Will Rock You = 18 layers / 565 effects**; Matrix 1 in Fight Song = 9 layers; `GE Priem Cube GRP` in Snoop HD = 13 layers. Skrillex Medley runs *every* element at 6+ layers (32 elements at exactly 6).
- Anatomy of the We Will Rock You mega tree stack: top 1–2 layers = long (3–24 s) bases (Fan, Shader, Meteors, Spirals); middle layers = dense 700–750 ms Shockwave/Pinwheel/Warp/Shape hits (5–7 parallel hit layers so overlapping accents never collide); bottom layers = special moments (Text, one-off 375 ms shockwave runs).
- Layer methods aggregate: `2 reveals 1` (5,768), `Average` (4,325), `1 reveals 2` (2,339), `Effect 1` (1,305), `True Unmask` variants (~2,000), `Unmask` (~1,600), plus Shadow/Subtractive/Mask accents.
  - **Reveal** pairs are their bread and butter: a moving effect (chase/shockwave/wipe) on one layer *reveals* a color field or texture on the neighbor — motion defines the shape, the partner defines the color.
  - **Unmask/True Unmask**: a high-contrast effect stamps a moving window into a rich base (e.g. VU Meter unmasking a Color Wash = music-reactive color).
  - `Average` blends dual textures into one softer composite (Can Can uses it 3,962× under its Morph star).
- Transitions are mostly bare `T_TEXTCTRL_Fadeout=.10–.5` / `Fadein` (thousands of uses) — almost never fancy wipe transitions (Wipe appears only 101× corpus-wide). Fades keep the dense hits from strobing harshly.
- `T_CHECKBOX_Canvas=1` shows up ~950× (Warp/Shader-era) — Warp-on-canvas over the composed layers below, exactly the Christmas Dubstep trick already noted in AGENTS.md.

---

## 5. Timing — note-onset locked, not just beat-locked

Every package carries **`Beats` + `Note Onsets`** timing tracks (16 of 18), some add `Drums`, `Bass Drum`, `Intro High Bells`, `Lyrics`, or hand tracks (`By Ron`, `By Feel`, `Custom`).

Measured on Fight Song V2: **633 of 633 model-effect starts land within one frame (25 ms) of a Beats/Note Onsets/Drums mark — 100% quantization.** Nothing free-floats. The hit *density* follows the onsets (more marks → more shockwaves), which is why their sequences feel like they're playing the music rather than pulsing on a grid.

This matches the instrument-track approach already proven here (Feliz Navidad horn/string tracks, Holy Forever drum timings): **generate/import a note-onset-level track per instrument and snap every effect to it.**

---

## 6. Per-sequence highlights (what to steal from each)

- **Fight Song V2 (2020)** — purest HD example: 107 elements, only 633 effects, but 64 are submodel-group banks each doing one clean job. Sparse-but-surgical; every hit is a different bank. 100% onset-locked. Shaders on Matrix.
- **Imperial March HD Add-On (2020)** — the shockwave bible: 1,822 shockwaves in 3,547 effects, `2 reveals 1` × 668. Study its downbeat bank-rotation (multiple part-banks of *different props* fired together per accent, rotating each bar).
- **We Will Rock You (2020)** — hero-element depth: 18-layer mega tree, 8-layer topper/eaves/verts/poles; `Fadein/Fadeout` on nearly every effect (1,347 combined); Text effects for lyric moments.
- **Home Alone Carol (2019)** — linear-prop choreography: 1,863 SingleStrand at `Vertical Per Model/Strand` (arch/window/feather cascades), plus early Shader + `Canvas=1` Warp use, and heavy `Subtractive`/`Layered` blending experiments.
- **Snoop Winter Wonderland HD (2020)** — gentler dynamic: Shimmer/Fill/Pinwheel-forward, unmask-heavy (`1/2 is Unmask` × 527), good model for laid-back grooves.
- **TSO Christmas Medley (2018)** — mega-tree-centric: Tree effect × 651, `1 reveals 2` × 1,692, 5–6 layers on most groups. Good orchestral-build reference.
- **It's Christmas Medley Live (2018)** — brute-force shockwave era: 6,618 shockwaves, `2 reveals 1` × 4,139 (shockwave revealing color layer = their classic "colored ring" hit).
- **Christmas Can Can (2018)** — one-off spectacle: a 144-layer element of Morphs (3,048) + Butterfly/Pictures under `Average` blending. Also 816 Pictures effects — prop-art era.
- **Skrillex Medley (2019)** — dubstep template (the style Elliott's `Christmas Dubstep` gold standard follows): uniform 6-layer stacks everywhere, Galaxy × 1,745, VU Meter × 529, `Effect 1`/unmask layer tricks, 1,352 value-curve-driven params.
- **Childrens Xmas Mix / Ghost Busters / Selfish Elf / Classic Medley / Monster Mash (2017)** — pre-submodel era: mostly whole models, On/Color Wash-heavy, SubBuffers used instead of submodels (Monster Mash: 200 subbuffer effects). Useful mainly to see how much the HD approach improved things.

---

## 7. Cheat sheet — reproducing the Xtreme look on this layout

1. **Pick 3–6 part-banks per hero prop** (`* GRP` submodel groups in the layout: Spokes, Rings, Arrows, Plungers, Hooks, Feathers Even/Odd…) and treat each as an instrument. Never light the whole spinner.
2. **One long base + short hits.** Top layer(s): slow Spirals/Fan/Pinwheel/Shader 3–20 s. Below: 300–825 ms Shockwave/SingleStrand/On hits, several parallel layers so overlaps never collide.
3. **Shockwave skeleton:** Blend_Edges=1, start 1/5, end radius 13–42, end width 25–77, accel 0, centered; `Overlay - Centered` for one wave over the group, `Per Model Per Preview` to pulse every part individually. Fadeout .25.
4. **SingleStrand skeleton:** Chase, 0.4–1.0 rotations, 1–4 chases, `Vertical Per Model/Strand` for simultaneous per-member drips or `Horizontal Per Model/Strand` + Group All for a traveling run. ~375 ms.
5. **Reveal/unmask pairs:** moving effect on one layer + color field on the other with `2 reveals 1` / `Unmask` — motion draws, partner colors. VU Meter as an unmask source = music-reactive color.
6. **Quantize 100% of starts** to Beats/Note Onsets/instrument marks. Rotate which banks take the hit each bar; stack 5–10 banks on downbeats; go dark between phrases.
7. **Reserve whole-scene groups** (`All Pixels GRP` equivalent = `Whole Scene`) for sub-second slams — same as the user preference already recorded in AGENTS.md.
8. **Odd/Even splits** of any radial bank are the cheapest way to double motion (alternate colors, counter-rotate, ping-pong hits).

---

## Appendix: corpus inventory

| Package | Seq file | xLights ver | Elements | Effects | Submodel-GRP elements |
|---|---|---|---|---|---|
| xS_Childrens Xmas Mix | Childrens Xmas Mix.xml | 2019.54 | 161 | 3,885 | 5 |
| xS_Christmas Can Can | Christmas Can Can.xml | 2018.33 | 77 | 5,406 | 4 |
| xS_Christmas Every Day | Christmas Every Day.xsq | 2020.47 | 91 | 2,724 | 25 |
| xS_Classic Chrismas Medley | Clasic Chrismas Medley 2017.xml | 2017.29 | 95 | 1,230 | 0 |
| xS_Fight Song V2 | Fight Song.xsq | 2020.31 | 107 | 633 | 64 |
| xS_Ghost Busters | Ghost Busters.xml | 2017.17 | 96 | 2,099 | 8 |
| xS_Home Alone Carol | Home Alone Carol.xml | 2019.30 | 61 | 5,004 | 20 |
| xS_Imperial March | Imperial March.xml | 2019.6 | 44 | 2,913 | 12 |
| xS_Imperial March 2020 HD Add-On | Imperial March HD Add-On Pack.xsq | 2020.24 | 82 | 3,547 | 54 |
| xS_It's Christmas Medley Live | It's Christmas.xml | 2018.15 | 86 | 8,196 | 4 |
| xS_Monster Mash | Monster Mash.xml | 2017.19 | 61 | 266 | 6 |
| xS_Selfish Elf | Selfish Elf.xml | 2017.33 | 75 | 1,195 | 2 |
| xS_Skrillex Medley | Skrillex Medley.xml | 2019.46 | 36 | 9,955 | 12 |
| xS_Snoop Winter Wonderland | Snoop Winter Wonderland 2017.xsq | 2020.49 | 46 | 837 | 2 |
| xS_Snoop Winter Wonderland HD Add-On | …HD Add-On Pack.xsq | 2020.47 | 77 | 1,866 | 58 |
| xS_TSO Christmas Medley | TSO Christmas Medley.xml | 2018.52 | 49 | 5,008 | 4 |
| xS_Twas The Night Before Christmas | …Family Force V2.xsq | 2020.47 | 39 | 2,600 | 12 |
| xS_We Will Rock You | We Will Rock You.xml | 2020.4 | 84 | 4,793 | 35 |

Vendor layouts referenced: each package's own `xlights_rgbeffects.xml` (Fight Song layout: 153 models / 2,115 submodels / 164 groups; Imperial HD: 173 / 2,378 / 187). Legacy `.xml` sequence files are old-format `<xsequence>` — same EffectDB/ElementEffects structure as `.xsq`.
