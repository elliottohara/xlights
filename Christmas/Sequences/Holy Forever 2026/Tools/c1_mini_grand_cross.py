"""Chorus 1 — glowing cross on GE Mini Grand Illusion.

Same Pictures image as the intro Mega Tree cross (Glowing Cross.png,
Scale To Fit, white), but render style is **Per Preview** — hand-tuned
2026-07-21 (default / Scale-To-Fit alone did not paint correctly on the
Mini Grand). No intro Holy swell curve.

Window: Song Sections "Chorus 1" 67575–95100.

Run (Slot A):
    python3 c1_mini_grand_cross.py [--dry-run] [--clear-only] [--rework]
"""
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, '/Users/elliott.ohara/xlights-worktrees/slot-a/Tools')
import xlights_api as x

XSQ = ('/Users/elliott.ohara/xlights-worktrees/slot-a/Christmas/Sequences/'
       'Holy Forever 2026/Holy Forever 2026.xsq')
SEQ_LEN = 308314

WIN_START = 67575   # Song Sections: Chorus 1
WIN_END = 95100

TARGET = 'GE Mini Grand Illusion'
LAYER = 0

CROSS = ('/Users/elliott.ohara/xlights-worktrees/slot-a/Christmas/Sequences/'
         'Holy Forever 2026/Media/Images/Glowing Cross.png')

# Hand-tuned: Per Preview (required on Mini Grand; default failed).
SETTINGS = (
    'B_CHOICE_BufferStyle=Per Preview,'
    'E_CHECKBOX_Pictures_PixelOffsets=0,'
    'E_CHECKBOX_Pictures_Shimmer=0,'
    'E_CHECKBOX_Pictures_TransparentBlack=0,'
    'E_CHECKBOX_Pictures_WrapX=0,'
    'E_CHOICE_Pictures_Direction=none,'
    'E_CHOICE_Scaling=Scale To Fit,'
    'E_SLIDER_PicturesXC=0,'
    'E_SLIDER_PicturesYC=0,'
    'E_SLIDER_Pictures_EndScale=100,'
    'E_SLIDER_Pictures_StartScale=100,'
    f'E_TEXTCTRL_Pictures_Filename={CROSS},'
    'E_TEXTCTRL_Pictures_FrameRateAdj=1.0,'
    'E_TEXTCTRL_Pictures_Speed=1.0,'
    'E_TEXTCTRL_Pictures_TransparentBlack=0,'
    'T_TEXTCTRL_Fadein=2,'
    'T_TEXTCTRL_Fadeout=2'
)

PALETTE = (
    'C_BUTTON_Palette1=#FFFFFF,'
    'C_CHECKBOX_Palette1=1'
)


def window_effects():
    layers = x.xl('getEffectIDs', model=TARGET)['effects']
    hits = []
    for li, ids in enumerate(layers):
        if li != LAYER:
            continue
        for eid in ids:
            s = x.xl('getEffectSettings', model=TARGET, layer=str(li), id=str(eid))
            if int(s['endTime']) > WIN_START and int(s['startTime']) < WIN_END:
                hits.append((li, eid, s.get('name')))
    return hits


def clear_window_via_xsq():
    tree = ET.parse(XSQ)
    ee = tree.getroot().find('ElementEffects')
    removed = 0
    for el in ee.findall('Element'):
        if el.get('name') != TARGET:
            continue
        for li, layer in enumerate(el.findall('EffectLayer')):
            if li != LAYER:
                continue
            for eff in list(layer.findall('Effect')):
                s, e = int(eff.get('startTime')), int(eff.get('endTime'))
                if e > WIN_START and s < WIN_END:
                    layer.remove(eff)
                    removed += 1
    tree.write(XSQ, encoding='UTF-8', xml_declaration=True)
    return removed


def main():
    dry = '--dry-run' in sys.argv
    clear_only = '--clear-only' in sys.argv
    rework = '--rework' in sys.argv

    info = x.xl('getOpenSequence')
    assert 'Holy Forever 2026' in info.get('seq', ''), info
    assert int(info.get('len', 0)) == SEQ_LEN, info

    dirty = window_effects()
    print(f'plan: Pictures Glowing Cross on {TARGET} L{LAYER} '
          f'{WIN_START}-{WIN_END}')

    if dry:
        if dirty:
            print(f'window dirty: {dirty} (use --rework)')
        print('dry-run: no writes')
        return

    if dirty:
        if not rework:
            raise SystemExit('C1 window not empty — rerun with --rework.')
        x.save(XSQ)
        x.xl('closeSequence', force='true', quiet='true')
        removed = clear_window_via_xsq()
        print(f'cleared {removed} via .xsq')
        x.xl('openSequence', seq=XSQ, timeout=120)
        assert int(x.xl('getOpenSequence').get('len', 0)) == SEQ_LEN

    if not clear_only:
        x.add_effect(TARGET, LAYER, 'Pictures', SETTINGS, PALETTE,
                     WIN_START, WIN_END)
        print(f'  + {TARGET} L{LAYER} Pictures')

    got = window_effects()
    expected = 0 if clear_only else 1
    assert len(got) == expected, got
    if not clear_only:
        s = x.xl('getEffectSettings', model=TARGET, layer=str(LAYER),
                 id=str(got[0][1]))
        assert s['name'] == 'Pictures', s
        sett = s.get('settings') or {}
        fn = sett.get('E_TEXTCTRL_Pictures_Filename', '')
        assert 'Glowing Cross' in fn, fn
        assert sett.get('B_CHOICE_BufferStyle') == 'Per Preview', sett

    x.save(XSQ)
    print(f'saved {XSQ}')


if __name__ == '__main__':
    main()
