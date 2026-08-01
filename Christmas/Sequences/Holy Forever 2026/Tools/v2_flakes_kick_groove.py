"""REJECTED 2026-08-01 — user removed this treatment; build mode refuses.

C1-end kick build + Verse 2 groove — Xtreme part-bank pass on the house-face
snowflakes (Flakes Outline / Spokes / Arms banks). Kept as reference for what
was tried; only --dry-run / --clear-only still run.

User ask (2026-07-31): "The end of the first chorus, where the kick drum starts
and the intensity starts up. Let's add some really nice xtreme style effects on
the snowflakes on the face of the house. Run this all the way through verse 2."

Musical anchors (live timing tracks):
  - Kick pickup pairs 88925+89750 and 92250+93075 close out C1.
  - Mood `Groove` downbeat 93925 (kit settles); snare backbeat 2&4 from 94750.
  - V2 ends at the Soaring/Chorus-2 downbeat 127275.

Design (XTREME SEQUENCES STYLE REPORT flake pattern: outline = glow base,
spokes = hit target, arms = chase-out; every start on a timing mark; blue/amber
palette continues the approved C1 look):
  - `Flakes Spokes All GRP` L0/L1: amber Shockwave per labeled Kick mark
    (Per Model Per Preview + 2D — the HD per-part pulse), 500 ms, from 88925.
    Tight kick pairs alternate onto L1 so decays never collide.
  - `Flakes GRP` L0: one large amber Overlay-Centered Shockwave slam on the
    Groove downbeat 93925 (the moment the kit lands).
  - `Flakes Outline All GRP` L0: navy->sapphire breathing Color Wash bed,
    93925-127275 (starts as the Whole Scene C1 aurora bows out), b40, 2 s fades.
  - `Flakes Arms GRP` L0: sapphire SingleStrand chase-out per labeled Snare
    mark (Vertical Per Model/Strand — every arm chases root->tip together),
    375 ms, backbeat 94750-126450.

Run in Slot B (XLIGHTS_API_PORT=49914):
    python3 v2_flakes_kick_groove.py [--dry-run] [--clear-only] [--rework]
"""
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, '/Users/elliott.ohara/xlights-worktrees/slot-b/Tools')
import xlights_api as x

XSQ = ('/Users/elliott.ohara/xlights-worktrees/slot-b/Christmas/Sequences/'
       'Holy Forever 2026/Holy Forever 2026.xsq')
SEQ_LEN = 308314

HIT_START = 88925      # first kick of the C1-end pickup
BASE_START = 93925     # Groove downbeat — kit settles, aurora bed ends
WIN_END = 127275       # Soaring/C2 downbeat — end of V2

OUTLINE = 'Flakes Outline All GRP'
SPOKES = 'Flakes Spokes All GRP'
ARMS = 'Flakes Arms GRP'
FLAKES = 'Flakes GRP'

OWNED = {OUTLINE: {0}, SPOKES: {0, 1}, ARMS: {0}, FLAKES: {0}}

AMBER = '#FFC800'
GOLD = '#FFD89A'
SAPPHIRE = '#2864FF'
NAVY = '#0A1E50'

KICK_MS = 500
SNARE_MS = 375
SLAM_MS = 825

SHOCK_COMMON = (
    'E_CHECKBOX_Shockwave_Blend_Edges=1,'
    'E_NOTEBOOK_Shockwave=Position,'
    'E_SLIDER_Shockwave_Accel=0,'
    'E_SLIDER_Shockwave_CenterX=50,'
    'E_SLIDER_Shockwave_CenterY=50,'
    'E_SLIDER_Shockwave_Start_Radius=1,'
    'E_SLIDER_Shockwave_Start_Width=5,'
)

KICK_SETTINGS = (
    'B_CHOICE_BufferStyle=Per Model Per Preview,'
    'B_CHOICE_PerPreviewCamera=2D,'
    + SHOCK_COMMON +
    'E_SLIDER_Shockwave_End_Radius=35,'
    'E_SLIDER_Shockwave_End_Width=100,'
    'T_TEXTCTRL_Fadeout=.25'
)
KICK_PALETTE = (
    f'C_BUTTON_Palette1={AMBER},C_CHECKBOX_Palette1=1,'
    f'C_BUTTON_Palette2={GOLD},C_CHECKBOX_Palette2=1,'
    'C_SLIDER_Brightness=100'
)

SLAM_SETTINGS = (
    'B_CHOICE_BufferStyle=Overlay - Centered,'
    + SHOCK_COMMON +
    'E_SLIDER_Shockwave_End_Radius=42,'
    'E_SLIDER_Shockwave_End_Width=77,'
    'T_TEXTCTRL_Fadeout=.25'
)
SLAM_PALETTE = (
    f'C_BUTTON_Palette1={AMBER},C_CHECKBOX_Palette1=1,'
    f'C_BUTTON_Palette2={GOLD},C_CHECKBOX_Palette2=1,'
    'C_SLIDER_Brightness=100'
)

BASE_SETTINGS = (
    'B_CHOICE_BufferStyle=Default,'
    'E_TEXTCTRL_ColorWash_Cycles=4.0,'
    'E_CHECKBOX_ColorWash_HFade=0,'
    'E_CHECKBOX_ColorWash_VFade=0,'
    'T_TEXTCTRL_Fadein=2,'
    'T_TEXTCTRL_Fadeout=2'
)
BASE_PALETTE = (
    f'C_BUTTON_Palette1={NAVY},C_CHECKBOX_Palette1=1,'
    f'C_BUTTON_Palette2={SAPPHIRE},C_CHECKBOX_Palette2=1,'
    'C_SLIDER_Brightness=40'
)

SNARE_SETTINGS = (
    'B_CHOICE_BufferStyle=Vertical Per Model/Strand,'
    'E_NOTEBOOK_SSEFFECT_TYPE=Chase,'
    'E_CHOICE_SingleStrand_Colors=Palette,'
    'E_CHOICE_Chase_Type1=Left-Right,'
    'E_CHOICE_Fade_Type=From Head,'
    'E_CHECKBOX_Chase_Group_All=0,'
    'E_TEXTCTRL_Chase_Rotations=1.0,'
    'E_SLIDER_Number_Chases=1,'
    'E_SLIDER_Color_Mix1=35,'
    'T_TEXTCTRL_Fadeout=.25'
)
SNARE_PALETTE = (
    f'C_BUTTON_Palette1={SAPPHIRE},C_CHECKBOX_Palette1=1,'
    'C_SLIDER_Brightness=100'
)


def timing_marks(track, label):
    """Labeled mark start times from the .xsq inside [HIT_START, WIN_END)."""
    root = ET.parse(XSQ).getroot()
    for el in root.find('ElementEffects').findall('Element'):
        if el.get('name') == track and el.get('type') == 'timing':
            layer = el.find('EffectLayer')
            return [int(e.get('startTime')) for e in layer.findall('Effect')
                    if (e.get('label') or '').strip() == label
                    and HIT_START <= int(e.get('startTime')) < WIN_END]
    raise SystemExit(f'timing track {track!r} not found')


def plan():
    kicks = timing_marks('Kick', 'K')
    snares = timing_marks('Snare', 'S')
    effects = []  # (model, layer, effect, settings, palette, start, end)

    prev_end = {0: -1, 1: -1}
    for k in kicks:
        layer = 0 if k >= prev_end[0] else 1
        assert k >= prev_end[layer], f'kick {k} overlaps on both layers'
        end = min(k + KICK_MS, WIN_END)
        prev_end[layer] = end
        effects.append((SPOKES, layer, 'Shockwave',
                        KICK_SETTINGS, KICK_PALETTE, k, end))

    effects.append((FLAKES, 0, 'Shockwave', SLAM_SETTINGS, SLAM_PALETTE,
                    BASE_START, BASE_START + SLAM_MS))

    effects.append((OUTLINE, 0, 'Color Wash', BASE_SETTINGS, BASE_PALETTE,
                    BASE_START, WIN_END))

    for s in snares:
        if s < BASE_START:
            continue
        effects.append((ARMS, 0, 'SingleStrand',
                        SNARE_SETTINGS, SNARE_PALETTE, s, min(s + SNARE_MS, WIN_END)))

    return kicks, snares, effects


def window_effects(model, layers):
    layer_list = x.xl('getEffectIDs', model=model)['effects']
    hits = []
    for li, ids in enumerate(layer_list):
        if li not in layers:
            continue
        for eid in ids:
            s = x.xl('getEffectSettings', model=model, layer=str(li), id=str(eid))
            if int(s['endTime']) > HIT_START and int(s['startTime']) < WIN_END:
                hits.append((li, eid, s.get('name')))
    return hits


def clear_window_via_xsq():
    tree = ET.parse(XSQ)
    ee = tree.getroot().find('ElementEffects')
    removed = 0
    for el in ee.findall('Element'):
        name = el.get('name')
        if name not in OWNED:
            continue
        for li, layer in enumerate(el.findall('EffectLayer')):
            if li not in OWNED[name]:
                continue
            for eff in list(layer.findall('Effect')):
                s, e = int(eff.get('startTime')), int(eff.get('endTime'))
                if e > HIT_START and s < WIN_END:
                    layer.remove(eff)
                    removed += 1
    tree.write(XSQ, encoding='UTF-8', xml_declaration=True)
    return removed


def main():
    dry = '--dry-run' in sys.argv
    clear_only = '--clear-only' in sys.argv
    rework = '--rework' in sys.argv

    if not (dry or clear_only):
        raise SystemExit(
            'REFUSED: the user rejected this flake treatment on 2026-08-01 '
            '("I don\'t like the effects on the flakes like that") and it was '
            'removed. Rebuilding would undo that decision — see AGENT NOTES.md. '
            'Only --dry-run and --clear-only are allowed.')

    kicks, snares, effects = plan()
    by_model = {}
    for m, li, name, *_ in effects:
        by_model.setdefault(f'{m} L{li}', []).append(name)
    print(f'{len(kicks)} kicks, {len(snares)} snares in window '
          f'{HIT_START}-{WIN_END}; {len(effects)} effects planned:')
    for k, v in by_model.items():
        print(f'  {k}: {len(v)}x {v[0]}')

    if dry:
        print('dry-run: no writes')
        return

    info = x.xl('getOpenSequence')
    assert 'Holy Forever 2026' in info.get('seq', ''), info
    assert int(info.get('len', 0)) == SEQ_LEN, info

    dirty = {m: hits for m in OWNED if (hits := window_effects(m, OWNED[m]))}
    if dirty:
        if not rework and not clear_only:
            raise SystemExit(f'window not empty on {list(dirty)} — '
                             'rerun with --rework.')
        x.save(XSQ)
        x.xl('closeSequence', force='true', quiet='true')
        removed = clear_window_via_xsq()
        print(f'cleared {removed} window effects via .xsq')
        x.xl('openSequence', seq=XSQ, timeout=120)
        info = x.xl('getOpenSequence')
        assert int(info.get('len', 0)) == SEQ_LEN, info

    if not clear_only:
        for m, li, name, settings, palette, s, e in effects:
            x.add_effect(m, li, name, settings, palette, s, e)
        print(f'added {len(effects)} effects')

    # verify counts landed
    expect = {}
    for m, li, *_ in effects:
        expect.setdefault(m, set()).add(li)
    for m in OWNED:
        got = window_effects(m, OWNED[m])
        want = 0 if clear_only else sum(
            1 for e in effects if e[0] == m)
        assert len(got) == want, f'{m}: expected {want} in window, got {got}'

    # V1 chord Shockwave @32200 must survive on Outline L0
    outline_l0 = x.xl('getEffectIDs', model=OUTLINE)['effects'][0]
    starts = []
    for eid in outline_l0:
        s = x.xl('getEffectSettings', model=OUTLINE, layer='0', id=str(eid))
        starts.append(int(s['startTime']))
    assert 32200 in starts, f'V1 Shockwave missing from Outline L0: {starts}'

    x.save(XSQ)
    print(f'saved {XSQ}')


if __name__ == '__main__':
    main()
