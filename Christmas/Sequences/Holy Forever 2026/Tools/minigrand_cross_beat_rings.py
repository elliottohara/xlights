"""Mini Grand cross — user's per-bar gold shockwave ring, whole groove span.

2026-08-01: the user hand-placed two Shockwaves on `GE Mini Grand Illusion` L0
(98025-99150 and 101400-102525, 1125 ms, Scale=1, amber/gold, radius 1->42)
and asked to "repeat what I did for the rest of the sequence", clarifying:
one hit per bar on that same felt beat ("beat 4" to their ear = the Beat
Count track's labeled "2", +~825 ms after each bar downbeat), through the
whole rest of the song.

This script clones their exact effect onto every Beat Count mark labeled "2"
AFTER their last hand hit, ending when the band falls away (Mood Afterglow
287275; last groove bar's mark ~286425). The two hand-placed originals are
never touched. Hits start exactly ON the labeled mark (the hand ones are
25-75 ms early — hand-drag imprecision, kept as-is).

Run in Slot B (XLIGHTS_API_PORT=49914), sequence open:
    python3 minigrand_cross_beat_rings.py [--dry-run] [--clear-only]
--clear-only removes script-added rings (L0 Shockwaves at labeled-"2" marks
in the span, exact 1125 ms duration) via direct .xsq edit; hand hits stay.
"""
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, '/Users/elliott.ohara/xlights-worktrees/slot-b/Tools')
import xlights_api as x

XSQ = ('/Users/elliott.ohara/xlights-worktrees/slot-b/Christmas/Sequences/'
       'Holy Forever 2026/Holy Forever 2026.xsq')
SEQ_LEN = 308314
MG = 'GE Mini Grand Illusion'

# 2026-08-01 v2: user re-timed/re-shaped in the GUI — 350 ms, Fadeout 0.20,
# starting ~2 frames before the beat (bloom peaks ON the beat). Their four
# hand hits below are canonical; script rings start LEAD ms before each mark.
HAND_HITS = [(98025, 98375), (101400, 101750),
             (104700, 105050), (108075, 108425)]   # user's — do not touch
AFTER = 108425          # only add after the last hand hit ends
GROOVE_END = 287275     # Mood Afterglow downbeat — band falls away
DUR = 350
LEAD = 50               # start this many ms before the labeled mark

SETTINGS = (
    'B_CHOICE_BufferStyle=Per Preview,'
    'E_CHECKBOX_Shockwave_Blend_Edges=1,'
    'E_CHECKBOX_Shockwave_Scale=1,'
    'E_NOTEBOOK_Shockwave=Position,'
    'E_SLIDER_Shockwave_Accel=0,'
    'E_SLIDER_Shockwave_CenterX=50,'
    'E_SLIDER_Shockwave_CenterY=50,'
    'E_SLIDER_Shockwave_Cycles=1,'
    'E_SLIDER_Shockwave_End_Radius=42,'
    'E_SLIDER_Shockwave_End_Width=77,'
    'E_SLIDER_Shockwave_Start_Radius=1,'
    'E_SLIDER_Shockwave_Start_Width=10,'
    'T_TEXTCTRL_Fadeout=0.20')
PALETTE = ('C_BUTTON_Palette1=#ffc800,C_CHECKBOX_Palette1=1,'
           'C_BUTTON_Palette2=#ffd89a,C_CHECKBOX_Palette2=1')


def beat2_marks():
    root = ET.parse(XSQ).getroot()
    for el in root.find('ElementEffects').findall('Element'):
        if el.get('name') == 'Beat Count' and el.get('type') == 'timing':
            layer = el.find('EffectLayer')
            return [int(e.get('startTime')) for e in layer.findall('Effect')
                    if (e.get('label') or '').strip() == '2']
    raise SystemExit('Beat Count track not found')


def targets():
    return [t for t in beat2_marks() if AFTER < t < GROOVE_END]


def l0_effects():
    ids = x.xl('getEffectIDs', model=MG)['effects'][0]
    out = []
    for eid in ids:
        s = x.xl('getEffectSettings', model=MG, layer='0', id=str(eid))
        out.append((int(s['startTime']), int(s['endTime']), s['name']))
    return out


def main():
    dry = '--dry-run' in sys.argv
    clear_only = '--clear-only' in sys.argv

    marks = targets()
    print(f'{len(marks)} per-bar marks in ({AFTER}, {GROOVE_END}): '
          f'{marks[0]}..{marks[-1]}')

    info = x.xl('getOpenSequence')
    assert 'Holy Forever 2026' in info.get('seq', ''), info
    assert int(info.get('len', 0)) == SEQ_LEN, info

    existing = l0_effects()
    for hs, he in HAND_HITS:
        assert any(s == hs and e == he for s, e, _ in existing), \
            f'hand hit {hs}-{he} missing — aborting'

    if clear_only:
        if dry:
            print('dry-run: would clear script rings')
            return
        x.save(XSQ)
        x.xl('closeSequence', force='true', quiet='true')
        tree = ET.parse(XSQ)
        removed = 0
        mark_set = set(marks)
        for el in tree.getroot().find('ElementEffects').findall('Element'):
            if el.get('name') != MG:
                continue
            layer = el.findall('EffectLayer')[0]
            for e in list(layer.findall('Effect')):
                s, en = int(e.get('startTime')), int(e.get('endTime'))
                if (e.get('name') == 'Shockwave' and s + LEAD in mark_set
                        and en - s == DUR):
                    layer.remove(e)
                    removed += 1
        tree.write(XSQ, encoding='UTF-8', xml_declaration=True)
        x.xl('openSequence', seq=XSQ, timeout=300)
        x.save(XSQ)
        print(f'cleared {removed} script rings; saved')
        return

    # collision check: nothing else on L0 in the add span
    stray = [e for e in existing
             if e[1] > AFTER and (e[0], e[1]) not in HAND_HITS]
    assert not stray, f'unexpected L0 effects in span: {stray}'

    if dry:
        print(f'dry-run: would add {len(marks)} rings ({DUR} ms each)')
        return

    for t in marks:
        x.add_effect(MG, 0, 'Shockwave', SETTINGS, PALETTE, t - LEAD, t - LEAD + DUR)

    got = l0_effects()
    assert len(got) == len(existing) + len(marks), (len(got), len(existing))
    x.save(XSQ)
    print(f'added {len(marks)} rings; saved')


if __name__ == '__main__':
    main()
