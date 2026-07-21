"""Chorus 1 — house Rosa-red reveal (idea 1).

Cast:
  - Verts / Roof / Windows: L1 Rosa red (#B01212) Color Wash + L0 narrow
    Single Line Marquee with `1 reveals 2` and Rosa amber (#FFD89A) mask.
  - GE Merry Christmas/Christ: same marquee reveal, but full bright white
    (#FFFFFF) wash + white mask (no amber/red/blue).
  - Icicles GRP: same red wash, but L0 is the Vertical Per Model SingleStrand
    drip (liked motion) with the same reveal + amber mask.
  Christ PC1 bass blinks (L1–L3, ends ≤63875) sit outside this window.

⚠ Roof includes /Eves submodels — overlaps Icicles GRP visually; intentional
per user (roof line + icicles both active in C1). Roof L0 final-hold On at
301500 is outside this window and left alone.

Window: 67275-93925 (same Anthemic C1 window as Rosa/Starlord/Reel Max).
Long fades (2 s). Idempotent; --rework clears owned layers in-window via .xsq.
`--rework` also strips the mistaken Flakes Outline/Arms C1 pass if present.

Run (Slot A):
    python3 c1_house_icicles.py [--dry-run] [--clear-only] [--rework]
"""
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, '/Users/elliott.ohara/xlights-worktrees/slot-a/Tools')
import xlights_api as x

XSQ = ('/Users/elliott.ohara/xlights-worktrees/slot-a/Christmas/Sequences/'
       'Holy Forever 2026/Holy Forever 2026.xsq')
SEQ_LEN = 308314

WIN_START = 67275
WIN_END = 93925

VERTS = 'Verts'
ROOF = 'Roof'
WINDOWS = 'Windows'
CHRIST = 'GE Merry Christmas/Christ'
ICICLES = 'Icicles GRP'
# Cleared on --rework only — mistaken "snowflakes" pass (user meant icicles).
STALE_FLAKES = [
    ('Flakes Outline All GRP', 0), ('Flakes Outline All GRP', 1),
    ('Flakes Arms GRP', 0), ('Flakes Arms GRP', 1),
]
MARQUEE_MODELS = (VERTS, ROOF, WINDOWS, CHRIST)
OWNED = (
    [(m, 0) for m in MARQUEE_MODELS] +
    [(m, 1) for m in MARQUEE_MODELS] +
    [(ICICLES, 0), (ICICLES, 1)]
)
CLEAR_TARGETS = OWNED + STALE_FLAKES

ROSA_RED = '#B01212'   # same as rosa_c1_constant_motion.py
ROSA_GOLD = '#FFD89A'  # warm amber mask (Rosa palette)
WHITE = '#FFFFFF'      # Christ — full bright white

VERTS_MARQUEE = (
    'B_CHOICE_BufferStyle=Single Line,'
    'E_CHECKBOX_Marquee_PixelOffsets=0,'
    'E_CHECKBOX_Marquee_Reverse=0,'
    'E_CHECKBOX_Marquee_WrapX=0,'
    'E_NOTEBOOK_Marquee=Settings,'
    'E_SLIDER_MarqueeXC=0,'
    'E_SLIDER_MarqueeYC=0,'
    'E_SLIDER_Marquee_Band_Size=4,'
    'E_SLIDER_Marquee_ScaleX=100,'
    'E_SLIDER_Marquee_ScaleY=100,'
    'E_SLIDER_Marquee_Skip_Size=9,'
    'E_SLIDER_Marquee_Speed=2,'
    'E_SLIDER_Marquee_Stagger=0,'
    'E_SLIDER_Marquee_Start=0,'
    'E_SLIDER_Marquee_Thickness=2,'
    'T_CHOICE_LayerMethod=1 reveals 2,'
    'T_TEXTCTRL_Fadein=2,'
    'T_TEXTCTRL_Fadeout=2'
)

VERTS_WASH = (
    'E_CHECKBOX_ColorWash_HFade=0,'
    'E_CHECKBOX_ColorWash_VFade=0,'
    'E_TEXTCTRL_ColorWash_Cycles=1.0,'
    'T_TEXTCTRL_Fadein=2,'
    'T_TEXTCTRL_Fadeout=2'
)

# Icicles motion — liked drip, now reveals Rosa red (same method as Verts).
ICICLES_DRIP = (
    'B_CHOICE_BufferStyle=Vertical Per Model/Strand,'
    'E_CHECKBOX_Chase_Group_All=0,'
    'E_CHOICE_Chase_Type1=Left-Right,'
    'E_CHOICE_Fade_Type=From Head,'
    'E_CHOICE_SingleStrand_Colors=Palette,'
    'E_NOTEBOOK_SSEFFECT_TYPE=Chase,'
    'E_SLIDER_Color_Mix1=28,'
    'E_SLIDER_Number_Chases=1,'
    'E_TEXTCTRL_Chase_Rotations=3,'
    'T_CHOICE_LayerMethod=1 reveals 2,'
    'T_TEXTCTRL_Fadein=2,'
    'T_TEXTCTRL_Fadeout=2'
)


def flat_pal(*colors, brightness=None):
    parts = []
    for i, c in enumerate(colors, 1):
        parts.append(f'C_BUTTON_Palette{i}={c},C_CHECKBOX_Palette{i}=1')
    if brightness is not None:
        parts.append(f'C_SLIDER_Brightness={brightness}')
    return ','.join(parts)


def reveal_marquee(model, wash=ROSA_RED, mask=ROSA_GOLD, wash_brightness=80):
    return [
        (model, 1, 'Color Wash', VERTS_WASH, flat_pal(wash, brightness=wash_brightness)),
        (model, 0, 'Marquee', VERTS_MARQUEE, flat_pal(mask, brightness=100)),
    ]


PLAN = (
    reveal_marquee(VERTS) +
    reveal_marquee(ROOF) +
    reveal_marquee(WINDOWS) +
    reveal_marquee(CHRIST, wash=WHITE, mask=WHITE, wash_brightness=100) +
    [
        (ICICLES, 1, 'Color Wash', VERTS_WASH, flat_pal(ROSA_RED, brightness=80)),
        (ICICLES, 0, 'SingleStrand', ICICLES_DRIP, flat_pal(ROSA_GOLD, brightness=100)),
    ]
)

WASH_COLOR = {
    VERTS: ROSA_RED, ROOF: ROSA_RED, WINDOWS: ROSA_RED,
    CHRIST: WHITE, ICICLES: ROSA_RED,
}
MASK_COLOR = {
    VERTS: ROSA_GOLD, ROOF: ROSA_GOLD, WINDOWS: ROSA_GOLD,
    CHRIST: WHITE, ICICLES: ROSA_GOLD,
}


def window_effects(model, layer=None):
    layers = x.xl('getEffectIDs', model=model)['effects']
    hits = []
    for li, ids in enumerate(layers):
        if layer is not None and li != layer:
            continue
        for eid in ids:
            s = x.xl('getEffectSettings', model=model, layer=str(li), id=str(eid))
            if int(s['endTime']) > WIN_START and int(s['startTime']) < WIN_END:
                hits.append((li, eid, s))
    return hits


def expected_present():
    for model, layer, name, settings, palette in PLAN:
        hits = window_effects(model, layer)
        if len(hits) != 1:
            return False
        _, _, s = hits[0]
        if (s.get('name') != name
                or int(s['startTime']) != WIN_START
                or int(s['endTime']) != WIN_END):
            return False
        method = (s.get('settings') or {}).get('T_CHOICE_LayerMethod')
        if name == 'Marquee':
            if method != '1 reveals 2':
                return False
            want = MASK_COLOR.get(model, ROSA_GOLD)
            if s.get('palette', {}).get('C_BUTTON_Palette1') != want:
                return False
        if name == 'SingleStrand':
            if method != '1 reveals 2':
                return False
            if s.get('palette', {}).get('C_BUTTON_Palette1') != ROSA_GOLD:
                return False
        if name == 'Color Wash' and model in WASH_COLOR:
            if s.get('palette', {}).get('C_BUTTON_Palette1') != WASH_COLOR[model]:
                return False
    return True


def _strip_in_window(layer_el):
    removed = 0
    for eff in list(layer_el.findall('Effect')):
        st = int(eff.get('startTime', 0))
        en = int(eff.get('endTime', 0))
        if en > WIN_START and st < WIN_END:
            layer_el.remove(eff)
            removed += 1
    return removed


def clear_xsq_window():
    """Strip owned (+ stale flake) in-window effects from the closed .xsq.

    Whole models use `<EffectLayer>`; submodels (e.g. Christ) live under the
    parent as `<SubModelEffectLayer name="…" layer="…">`.
    """
    tree = ET.parse(XSQ)
    root = tree.getroot()
    ee = root.find('ElementEffects')
    if ee is None:
        raise RuntimeError('no ElementEffects')

    whole = {}  # model -> set(layers)
    subs = {}   # (parent, sub) -> set(layers)
    for model, li in CLEAR_TARGETS:
        if '/' in model:
            parent, sub = model.split('/', 1)
            subs.setdefault((parent, sub), set()).add(li)
        else:
            whole.setdefault(model, set()).add(li)

    removed = 0
    for el in ee.findall('Element'):
        name = el.get('name')
        if name in whole:
            for li, layer in enumerate(el.findall('EffectLayer')):
                if li in whole[name]:
                    removed += _strip_in_window(layer)
        for (parent, sub), want in subs.items():
            if name != parent:
                continue
            for sm in el.findall('SubModelEffectLayer'):
                if sm.get('name') != sub:
                    continue
                li = int(sm.get('layer', 0))
                if li in want:
                    removed += _strip_in_window(sm)

    tree.write(XSQ, encoding='UTF-8', xml_declaration=True)
    return removed


def main():
    dry = '--dry-run' in sys.argv
    clear_only = '--clear-only' in sys.argv
    rework = '--rework' in sys.argv

    info = x.xl('getOpenSequence')
    assert 'Holy Forever 2026' in info.get('seq', ''), info
    assert int(info.get('len', 0)) == SEQ_LEN, info

    print(f'plan: Verts/Roof/Windows/Christ Marquee + Icicles drip, '
          f'Rosa-red reveal {WIN_START}-{WIN_END}')

    if expected_present() and not rework and not clear_only:
        print('done: exact effects already present.')
        return

    # Refuse unexpected occupants unless rework/clear
    blockers = []
    for model, layer in OWNED:
        for li, eid, s in window_effects(model, layer):
            blockers.append((model, li, s.get('name'), s['startTime'], s['endTime']))
    if blockers and not (rework or clear_only):
        if expected_present():
            print('done: exact effects already present.')
            return
        raise SystemExit(f'REFUSING: unexpected in-window effects: {blockers}')

    if dry:
        print(f'dry run: would {"clear" if clear_only or rework else "add"} '
              f'{len(PLAN)} effects; blockers={blockers}')
        return

    if rework or clear_only or blockers:
        x.save(XSQ)
        x.xl('closeSequence', force='true', quiet='true')
        n = clear_xsq_window()
        print(f'cleared {n} in-window effect(s) from .xsq')
        x.xl('openSequence', seq=XSQ, timeout=120)
        info = x.xl('getOpenSequence')
        assert int(info.get('len', 0)) == SEQ_LEN, info
        if clear_only:
            x.save(XSQ)
            print('clear-only done')
            return

    for model, layer, name, settings, palette in PLAN:
        remaining = window_effects(model, layer)
        if remaining:
            raise SystemExit(f'{model} L{layer} still occupied: {remaining}')
        x.add_effect(model, layer, name, settings, palette, WIN_START, WIN_END)
        print(f'  + {model} L{layer} {name}')

    assert expected_present(), 'verification failed'
    x.save(XSQ)
    print(f'saved: {XSQ}')


if __name__ == '__main__':
    main()
