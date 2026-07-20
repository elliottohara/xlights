"""Rebuild the Holy Forever bulb/penguin chorus choir.

This targeted builder preserves each bulb's dim Lyrics Intro Choir block, then
rebuilds the three Singing Bulbs and both Toni penguins on Lyrics Choir for C1,
C2a-C2c, and PC2b-C3c. It does not touch the other singing props.

Penguin palette slots (Penguin v.1.1 - No Tongue, CustomColors=0):
  mouth, eyes/wings, body/feet, belly
  Toni 1: white, white, white, burgundy
  Toni 2: white, white, white, sapphire

The xLights API cannot safely edit Faces settings in place, so this script
wipes layer 0 from an effect-free source and re-adds every owned effect.

Run:
  python3 ".../Tools/chorus_choir_faces.py" --dry-run
  python3 ".../Tools/chorus_choir_faces.py"
"""

import argparse
from pathlib import Path

import fix_faces as faces
import xlights_api as x


SEQUENCE = faces.TOOLS_DIR.parent / 'Holy Forever 2026.xsq'
EXPECTED_DURATION = 308314
INTRO_TRACK = 'Lyrics Intro Choir'
CHOIR_TRACK = 'Lyrics Choir'
INTRO_START = 3900
INTRO_END = 41850

BULBS = tuple(faces.BULB_GLASS)
PENGUINS = tuple(faces.PENGUIN_BELLY)
TARGETS = BULBS + PENGUINS


def encode(values):
    """Serialize API dictionaries for addEffect's key=value parser."""
    return ','.join(
        f'{key}={value}'
        for key, value in values.items()
        if value is not None and value != ''
    )


def capture(model):
    layers = x.xl('getEffectIDs', model=model)['effects']
    assert layers, f'{model} has no effect layer'
    assert all(not layer for layer in layers[1:]), (
        f'{model} has effects below layer 0; refusing a partial wipe: {layers}')
    return [
        x.xl('getEffectSettings', model=model, layer='0', id=str(effect_id))
        for effect_id in layers[0]
    ]


def choir_blocks():
    c1_start, c1_end = faces.sec('C1')
    c2_start, _ = faces.sec('C2a')
    _, c2_end = faces.sec('C2c')
    pc2b_start, _ = faces.sec('PC2b')
    _, c3_end = faces.sec('C3c')
    return [
        (c1_start, c1_end + 300, None),
        (c2_start, c2_end + 300, None),
        (pc2b_start, c3_end + 1500, '1.5'),
    ]


def assert_open_sequence():
    info = x.xl('getOpenSequence')
    assert info.get('seq') == 'Holy Forever 2026', f'wrong sequence: {info}'
    assert int(info.get('len', 0)) == EXPECTED_DURATION, f'wrong duration: {info}'
    assert Path(info.get('fullseq', '')).resolve() == SEQUENCE.resolve(), (
        f'xLights owns a different checkout: {info.get("fullseq")}; '
        f'expected {SEQUENCE}')
    assert Path(info.get('media', '')).name == (
        'Chris Tomlin - Holy Forever (Lyric Video).mp4'
    ), f'wrong media: {info}'


def assert_prerequisites():
    source = x.xl('getEffectIDs', model=faces.EMPTY_SOURCE)['effects']
    assert all(not layer for layer in source), (
        f'{faces.EMPTY_SOURCE} is not effect-free: {source}')

    timing = x.xl('getEffectIDs', model=CHOIR_TRACK)['effects']
    assert timing and any(timing), f'{CHOIR_TRACK} timing marks are missing'

    for submodel in faces.BULB_SUBMODELS:
        effects = x.xl('getEffectIDs', model=submodel)['effects']
        assert all(not layer for layer in effects), (
            f'legacy bulb submodel effects found on {submodel}: {effects}')


def inspect_existing():
    """Validate owned rows and return each bulb's intro Faces snapshot."""
    intros = {}
    for model in TARGETS:
        effects = capture(model)
        allowed_tracks = {CHOIR_TRACK}
        if model in BULBS:
            allowed_tracks.add(INTRO_TRACK)

        unexpected = [
            effect for effect in effects
            if effect.get('name') != 'Faces'
            or effect.get('settings', {}).get(
                'E_CHOICE_Faces_TimingTrack') not in allowed_tracks
        ]
        assert not unexpected, f'unowned effects on {model}: {unexpected}'

        intro = [
            effect for effect in effects
            if effect['settings'].get('E_CHOICE_Faces_TimingTrack') == INTRO_TRACK
        ]
        if model in BULBS:
            assert len(intro) == 1, f'{model} needs exactly one intro block: {intro}'
            block = intro[0]
            assert (int(block['startTime']), int(block['endTime'])) == (
                INTRO_START, INTRO_END
            ), f'unexpected intro span on {model}: {block}'
            assert block['settings'].get(
                'E_CHOICE_Faces_FaceDefinition') == 'Boscoyo ChromaBulb Face'
            assert block['palette'].get('C_SLIDER_Brightness') == '40'
            intros[model] = block
        else:
            assert not intro, f'unexpected intro block on {model}: {intro}'

        print(f'{model}: {len(effects)} existing block(s)')
        for effect in sorted(effects, key=lambda item: int(item['startTime'])):
            track = effect['settings'].get('E_CHOICE_Faces_TimingTrack')
            print(f'  {effect["startTime"]}-{effect["endTime"]} {track}')

    return intros


def print_plan():
    print('planned Lyrics Choir blocks:')
    for start, end, fadeout in choir_blocks():
        suffix = f', fadeout={fadeout}' if fadeout else ''
        print(f'  {start}-{end}{suffix}')
    print(
        '  Toni - Penguin 1: outside #FFFFFF, '
        f'belly {faces.PENGUIN_BELLY["Toni - Penguin 1"]}')
    print(
        '  Toni - Penguin 2: outside #FFFFFF, '
        f'belly {faces.PENGUIN_BELLY["Toni - Penguin 2"]}')


def rebuild(intros):
    for model in TARGETS:
        x.xl(
            'cloneModelEffects',
            target=model,
            source=faces.EMPTY_SOURCE,
            eraseModel='true',
        )
        remaining = x.xl('getEffectIDs', model=model)['effects']
        assert remaining and not remaining[0], (
            f'{model} layer 0 did not clear: {remaining}')

    for model in BULBS:
        intro = intros[model]
        x.add_effect(
            model,
            0,
            'Faces',
            encode(intro['settings']),
            encode(intro['palette']),
            int(intro['startTime']),
            int(intro['endTime']),
        )

    for model in TARGETS:
        definition, state, _ = faces.SINGERS[model]
        palette = faces.palette_for(model)
        for start, end, fadeout in choir_blocks():
            x.add_effect(
                model,
                0,
                'Faces',
                faces.face_settings(
                    definition, state, CHOIR_TRACK, fadeout=fadeout),
                palette,
                start,
                end,
            )


def assert_palette(effect, colors):
    palette = effect['palette']
    for index, color in enumerate(colors, 1):
        assert palette.get(f'C_BUTTON_Palette{index}', '').upper() == color, (
            f'palette {index} expected {color}, got {palette}')
        assert palette.get(f'C_CHECKBOX_Palette{index}') == '1', (
            f'palette {index} is disabled: {palette}')


def verify(intros):
    planned = choir_blocks()
    for model in TARGETS:
        effects = sorted(capture(model), key=lambda item: int(item['startTime']))
        expected_count = 4 if model in BULBS else 3
        assert len(effects) == expected_count, (
            f'{model} expected {expected_count} blocks, got {len(effects)}')

        offset = 0
        if model in BULBS:
            intro = effects[0]
            assert (int(intro['startTime']), int(intro['endTime'])) == (
                INTRO_START, INTRO_END)
            assert intro['settings'].get(
                'E_CHOICE_Faces_TimingTrack') == INTRO_TRACK
            assert intro['palette'].get('C_SLIDER_Brightness') == '40'
            for key in (
                'C_BUTTON_Palette1',
                'C_BUTTON_Palette2',
                'C_BUTTON_Palette3',
                'C_BUTTON_Palette4',
            ):
                assert intro['palette'].get(key, '').upper() == (
                    intros[model]['palette'].get(key, '').upper()
                ), f'{model} intro palette changed at {key}'
            offset = 1

        definition = faces.SINGERS[model][0]
        colors = faces.palette_colors_for(model)
        for effect, (start, end, fadeout) in zip(effects[offset:], planned):
            settings = effect['settings']
            assert effect.get('name') == 'Faces'
            assert (int(effect['startTime']), int(effect['endTime'])) == (
                start, end)
            assert settings.get('E_CHOICE_Faces_TimingTrack') == CHOIR_TRACK
            assert settings.get('E_CHOICE_Faces_FaceDefinition') == definition
            assert settings.get('E_CHECKBOX_Faces_Outline') == '1'
            if fadeout:
                assert settings.get('T_TEXTCTRL_Fadeout') == fadeout
            else:
                assert settings.get('T_TEXTCTRL_Fadeout', '0') in {
                    '0', '0.0', '0.00'}
            assert_palette(effect, colors)

        print(f'OK {model}: {len(effects)} verified block(s)')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='validate and print the rebuild without changing xLights',
    )
    args = parser.parse_args()

    assert_open_sequence()
    assert_prerequisites()
    intros = inspect_existing()
    print_plan()

    if args.dry_run:
        print('dry-run: no changes')
        return

    rebuild(intros)
    verify(intros)
    x.save(str(SEQUENCE))
    print(f'saved {SEQUENCE}')


if __name__ == '__main__':
    main()
