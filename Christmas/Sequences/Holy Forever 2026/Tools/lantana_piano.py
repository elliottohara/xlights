"""Full-song True Piano on Matrix - Lantana driven by Piano Notes track.

Requires the `Piano Notes` timing track (import
`Timing Templates/Holy Forever Piano Notes.xsq` once first).

Run:
  python3 Christmas/Sequences/Holy Forever 2026/Tools/lantana_piano.py [--dry-run]
  python3 Christmas/Sequences/Holy Forever 2026/Tools/lantana_piano.py --clear-only
"""
import sys

sys.path.insert(0, '/Users/elliott.ohara/xlights/Tools')
import xlights_api as x

EMPTY_SOURCE = 'House'
TARGET = 'Matrix - Lantana'
TRACK = 'Piano Notes'
SEQ_END = 308275  # snap inside sequence length 308314
START_MIDI = 44
END_MIDI = 88

SETTINGS = (
    'E_CHOICE_Piano_Type=True Piano,'
    'E_CHECKBOX_Piano_ShowSharps=1,'
    'E_CHECKBOX_Piano_FadeNotes=1,'
    f'E_CHOICE_Piano_MIDITrack_APPLYLAST={TRACK},'
    f'E_TEXTCTRL_Piano_StartMIDI={START_MIDI},'
    f'E_TEXTCTRL_Piano_EndMIDI={END_MIDI},'
    'E_SLIDER_Piano_Scale=100,'
    'E_SLIDER_Piano_XOffset=0'
)

PALETTE = (
    'C_BUTTON_Palette1=#F0E6D0,'
    'C_BUTTON_Palette2=#FFD89A,'
    'C_BUTTON_Palette3=#FFFFFF,'
    'C_CHECKBOX_Palette1=1,'
    'C_CHECKBOX_Palette2=1,'
    'C_CHECKBOX_Palette3=1,'
    'C_SLIDER_Brightness=55'
)


def wipe():
    x.xl('cloneModelEffects', target=TARGET, source=EMPTY_SOURCE, eraseModel='true')
    left = x.xl('getEffectIDs', model=TARGET)['effects']
    assert not left[0], f'{TARGET} not empty after wipe'


def track_ok():
    try:
        ids = x.xl('getEffectIDs', model=TRACK)['effects'][0]
    except Exception as e:
        raise SystemExit(
            f'timing track {TRACK!r} missing — import '
            f'Holy Forever Piano Notes.xsq first ({e})')
    labeled = 0
    for eid in ids:
        s = x.xl('getEffectSettings', model=TRACK, layer=0, id=eid)
        if s.get('name'):
            labeled += 1
    if labeled < 10:
        raise SystemExit(f'{TRACK} has only {labeled} labeled marks')
    return labeled


def main():
    dry = '--dry-run' in sys.argv
    clear = '--clear-only' in sys.argv
    info = x.xl('getOpenSequence')
    assert 'Holy Forever 2026' in info.get('seq', ''), info

    if clear:
        print(f'clearing {TARGET}')
        if not dry:
            wipe()
        return

    n = track_ok()
    print(f'{TRACK}: {n} labeled marks')
    print(f'plan: wipe {TARGET}; Piano 0-{SEQ_END} MIDI {START_MIDI}-{END_MIDI} '
          f'True Piano / FadeNotes / track={TRACK}')
    if dry:
        print('dry-run: no writes')
        return

    wipe()
    x.add_effect(TARGET, 0, 'Piano', SETTINGS, PALETTE, 0, SEQ_END)
    s = x.xl('getEffectSettings', model=TARGET, layer=0, id='0')
    assert s.get('name') == 'Piano', s
    assert s['settings'].get('E_CHOICE_Piano_MIDITrack_APPLYLAST') == TRACK, s
    print(f'OK: {TARGET} Piano {s["startTime"]}-{s["endTime"]} '
          f'track={s["settings"]["E_CHOICE_Piano_MIDITrack_APPLYLAST"]} '
          f'MIDI={s["settings"]["E_TEXTCTRL_Piano_StartMIDI"]}-'
          f'{s["settings"]["E_TEXTCTRL_Piano_EndMIDI"]}')


if __name__ == '__main__':
    main()
