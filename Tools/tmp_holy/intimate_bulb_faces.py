"""Dim Singing Bulb Faces through intro + intimate acoustic V1.

Extends the existing muted intro Faces (Lyrics Intro Choir, brightness ~40,
warm ivory/gold C9) from their current end (13850) through PC1 (41850) so
the choir bulbs stay present — fairly dim — under the Snowman lead through
the acoustic verse. Later choir blocks (C1+) are preserved unchanged.

Must wipe+re-add (setEffectSettings corrupts Faces). House-wipe only touches L0.

Run: python3 Tools/tmp_holy/intimate_bulb_faces.py [--dry-run]
"""
import sys

sys.path.insert(0, '/Users/elliott.ohara/xlights/Tools')
import xlights_api as x


EMPTY_SOURCE = 'House'
BULBS = [
    'Singing Bulb - Left',
    'Singing Bulb - Center',
    'Singing Bulb - Right',
]

INTIMATE_END = 41850   # PC1 section boundary (matches cross/snow)
INTIMATE_BRIGHTNESS = 40  # fairly dim (intro was 45)
INTIMATE_FADEOUT = '2.00'


def capture(model):
    ids = x.xl('getEffectIDs', model=model)['effects'][0]
    out = []
    for eid in ids:
        s = x.xl('getEffectSettings', model=model, layer=0, id=eid)
        out.append(s)
    return out


def settings_str(sett):
    # addEffect wants key=value,... ; omit empty values
    parts = []
    for k, v in sett.items():
        if v is None or v == '':
            continue
        parts.append(f'{k}={v}')
    return ','.join(parts)


def palette_str(pal):
    parts = []
    for k, v in pal.items():
        if v is None or v == '':
            continue
        parts.append(f'{k}={v}')
    return ','.join(parts)


def main():
    dry = '--dry-run' in sys.argv
    info = x.xl('getOpenSequence')
    assert 'Holy Forever 2026' in info.get('seq', ''), f'wrong sequence: {info}'

    for el in BULBS:
        effects = capture(el)
        print(f'\n{el}: {len(effects)} Faces blocks')
        for e in effects:
            print(f'  {e["startTime"]}-{e["endTime"]} '
                  f'track={e["settings"].get("E_CHOICE_Faces_TimingTrack")} '
                  f'br={e["palette"].get("C_SLIDER_Brightness", "—")}')

        assert effects, f'{el} has no Faces to extend'
        first = effects[0]
        assert first['settings'].get('E_CHOICE_Faces_TimingTrack') == 'Lyrics Intro Choir', (
            f'{el} first block is not intro choir — abort')
        assert first['endTime'] < INTIMATE_END, (
            f'{el} first block already ends at {first["endTime"]}')

        # rebuild list: extend first through intimate V1; keep the rest
        rebuilt = []
        for i, e in enumerate(effects):
            sett = dict(e['settings'])
            pal = dict(e['palette'])
            start, end = int(e['startTime']), int(e['endTime'])
            if i == 0:
                end = INTIMATE_END
                pal['C_SLIDER_Brightness'] = str(INTIMATE_BRIGHTNESS)
                sett['T_TEXTCTRL_Fadeout'] = INTIMATE_FADEOUT
            rebuilt.append((start, end, sett, pal))
            print(f'  -> {start}-{end}'
                  + (' (extended intimate)' if i == 0 else ''))

        # no overlaps
        for a, b in zip(rebuilt, rebuilt[1:]):
            assert a[1] <= b[0], f'overlap {a[1]} vs {b[0]} on {el}'

        if dry:
            continue

        x.xl('cloneModelEffects', target=el, source=EMPTY_SOURCE, eraseModel='true')
        left = x.xl('getEffectIDs', model=el)['effects']
        assert not left[0], f'{el} L0 not empty after wipe'

        for start, end, sett, pal in rebuilt:
            x.add_effect(el, 0, 'Faces', settings_str(sett), palette_str(pal),
                         start, end)

        verify = capture(el)
        assert len(verify) == len(rebuilt), f'{el} count mismatch'
        assert verify[0]['endTime'] == INTIMATE_END
        assert verify[0]['palette'].get('C_SLIDER_Brightness') == str(INTIMATE_BRIGHTNESS)
        print(f'  OK: {len(verify)} blocks, intimate ends {INTIMATE_END}')

    if dry:
        print('\ndry-run: no writes')
        return

    out = '/Users/elliott.ohara/xlights/Christmas/Holy Forever 2026.xsq'
    x.save(out)
    print(f'\nsaved {out}')


if __name__ == '__main__':
    main()
