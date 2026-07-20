"""Add the PiXeL Paradise tree's seven faces to the Holy Forever choir.

The 1,300-pixel prop has built-in faces for its star, present, and five
ornaments. All seven sing from Lyrics Choir on the same three blocks as the
Penguins. A subdued evergreen tree outline and ivory/burgundy candy canes keep
the prop tied to Holy Forever's white/gold treatment while the face definitions
retain their designed ornament colors.

Run:
  python3 ".../Tools/pixel_paradise_tree_choir.py" --dry-run
  python3 ".../Tools/pixel_paradise_tree_choir.py"
"""

import argparse
import sys
from pathlib import Path


TOOLS_DIR = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[4]
SEQUENCE = TOOLS_DIR.parent / 'Holy Forever 2026.xsq'
sys.path.insert(0, str(REPO_ROOT / 'Tools'))

import xlights_api as x

import fix_faces as faces


MODEL = 'PiXeL Paradise Xmas Tree Choir'
TRACK = 'Lyrics Choir'
EMPTY_SOURCE = 'House'
EXPECTED_DURATION = 308314

FACE_DEFINITIONS = (
    'Star',
    'Blue Ornamnet',  # spelling is canonical in xlights_rgbeffects.xml
    'Green Ornament',
    'Red Ornament',
    'Yellow Ornament',
    'Purple Ornament',
    'Present',
)
FACE_PALETTE = (
    'C_BUTTON_Palette1=#FFFFFF,'
    'C_CHECKBOX_Palette1=1,'
    'C_SLIDER_Brightness=82'
)
SUBMODELS = {
    'Tree Outline': ('#0B6B3A', 38),
    'Candy Canes White Stripes': ('#EEEAE2', 52),
    'Candy Canes Red Stripes': ('#9D1D25', 48),
}


def choir_blocks():
    c1_start, c1_end = faces.sec('C1')
    c2_start, _ = faces.sec('C2a')
    _, c2_end = faces.sec('C2c')
    pc2b_start, _ = faces.sec('PC2b')
    _, c3_end = faces.sec('C3c')
    return [
        (c1_start, c1_end + 300, '.30'),
        (c2_start, c2_end + 300, '.30'),
        (pc2b_start, c3_end + 1500, '1.5'),
    ]


def face_settings(definition, fadeout):
    return (
        'E_CHECKBOX_Faces_Outline=1,'
        'E_CHOICE_Faces_EyeBlinkDuration=Normal,'
        'E_CHOICE_Faces_EyeBlinkFrequency=Normal,'
        'E_CHOICE_Faces_Eyes=Auto,'
        f'E_CHOICE_Faces_FaceDefinition={definition},'
        f'E_CHOICE_Faces_TimingTrack={TRACK},'
        f'T_TEXTCTRL_Fadeout={fadeout}'
    )


def on_settings(fadeout):
    return (
        'E_TEXTCTRL_On_Cycles=1.0,'
        'T_TEXTCTRL_Fadein=.25,'
        f'T_TEXTCTRL_Fadeout={fadeout}'
    )


def on_palette(color, brightness):
    return (
        f'C_BUTTON_Palette1={color},'
        'C_CHECKBOX_Palette1=1,'
        f'C_SLIDER_Brightness={brightness}'
    )


def effect_rows(model):
    layers = x.xl('getEffectIDs', model=model)['effects']
    rows = []
    for layer, effect_ids in enumerate(layers):
        for effect_id in effect_ids:
            effect = x.xl(
                'getEffectSettings',
                model=model,
                layer=str(layer),
                id=str(effect_id),
            )
            rows.append((layer, str(effect_id), effect))
    return rows


def assert_open_sequence():
    info = x.xl('getOpenSequence')
    assert info.get('seq') == 'Holy Forever 2026', f'wrong sequence: {info}'
    assert int(info.get('len', 0)) == EXPECTED_DURATION, f'wrong duration: {info}'
    assert Path(info.get('fullseq', '')).resolve() == SEQUENCE.resolve(), (
        f'xLights owns {info.get("fullseq")}; expected {SEQUENCE}')
    source = x.xl('getEffectIDs', model=EMPTY_SOURCE)['effects']
    assert all(not layer for layer in source), (
        f'{EMPTY_SOURCE} is not effect-free: {source}')


def inspect_owned():
    rows = effect_rows(MODEL)
    unexpected = []
    for layer, effect_id, effect in rows:
        if effect.get('name') == 'Off':
            continue
        settings = effect.get('settings', {})
        owned = (
            1 <= layer <= len(FACE_DEFINITIONS)
            and effect.get('name') == 'Faces'
            and settings.get('E_CHOICE_Faces_TimingTrack') == TRACK
            and settings.get('E_CHOICE_Faces_FaceDefinition')
            == FACE_DEFINITIONS[layer - 1]
        )
        if not owned:
            unexpected.append((layer, effect_id, effect))
    assert not unexpected, f'unowned effects on {MODEL}: {unexpected}'

    for submodel in SUBMODELS:
        target = f'{MODEL}/{submodel}'
        subrows = effect_rows(target)
        bad = [
            row for row in subrows
            if row[2].get('name') != 'On' or row[0] != 0
        ]
        assert not bad, f'unowned effects on {target}: {bad}'

    return rows


def next_park_slot(layer, occupied_by_layer):
    occupied = occupied_by_layer.setdefault(layer, set())
    for start in range(25, 3000, 25):
        if start not in occupied:
            occupied.add(start)
            return start
    raise RuntimeError(f'no dark Off-park slot left on {MODEL} layer {layer}')


def clear_owned(rows):
    occupied_by_layer = {}
    for layer, _, effect in rows:
        if effect.get('name') == 'Off':
            occupied_by_layer.setdefault(layer, set()).add(
                int(effect['startTime']))

    for layer, effect_id, effect in rows:
        if effect.get('name') == 'Off':
            continue
        park = next_park_slot(layer, occupied_by_layer)
        x.xl(
            'setEffectSettings',
            model=MODEL,
            layer=layer,
            id=effect_id,
            name='Off',
            startTime=park,
            endTime=park + 25,
            settings='',
            palette='',
        )

    for submodel in SUBMODELS:
        target = f'{MODEL}/{submodel}'
        x.xl(
            'cloneModelEffects',
            target=target,
            source=EMPTY_SOURCE,
            eraseModel='true',
        )
        remaining = x.xl('getEffectIDs', model=target)['effects']
        assert all(not layer for layer in remaining), (
            f'{target} did not clear: {remaining}')


def add_tree_choir():
    blocks = choir_blocks()
    for layer, definition in enumerate(FACE_DEFINITIONS, 1):
        for start, end, fadeout in blocks:
            x.add_effect(
                MODEL,
                layer,
                'Faces',
                face_settings(definition, fadeout),
                FACE_PALETTE,
                start,
                end,
            )

    for submodel, (color, brightness) in SUBMODELS.items():
        target = f'{MODEL}/{submodel}'
        palette = on_palette(color, brightness)
        for start, end, fadeout in blocks:
            x.add_effect(
                target,
                0,
                'On',
                on_settings(fadeout),
                palette,
                start,
                end,
            )


def verify():
    expected_blocks = [(start, end) for start, end, _ in choir_blocks()]
    rows = effect_rows(MODEL)
    for layer, definition in enumerate(FACE_DEFINITIONS, 1):
        live = sorted(
            (
                int(effect['startTime']),
                int(effect['endTime']),
                effect,
            )
            for row_layer, _, effect in rows
            if row_layer == layer and effect.get('name') != 'Off'
        )
        assert [(start, end) for start, end, _ in live] == expected_blocks, (
            f'{definition} spans mismatch: {live}')
        for _, _, effect in live:
            settings = effect['settings']
            palette = effect['palette']
            assert effect.get('name') == 'Faces'
            assert settings.get('E_CHOICE_Faces_TimingTrack') == TRACK
            assert settings.get('E_CHOICE_Faces_FaceDefinition') == definition
            assert settings.get('E_CHECKBOX_Faces_Outline') == '1'
            assert palette.get('C_SLIDER_Brightness') == '82'

    for submodel, (color, brightness) in SUBMODELS.items():
        target = f'{MODEL}/{submodel}'
        live = sorted(
            (
                int(effect['startTime']),
                int(effect['endTime']),
                effect,
            )
            for _, _, effect in effect_rows(target)
            if effect.get('name') != 'Off'
        )
        assert [(start, end) for start, end, _ in live] == expected_blocks, (
            f'{target} spans mismatch: {live}')
        for _, _, effect in live:
            palette = effect['palette']
            assert effect.get('name') == 'On'
            assert palette.get('C_BUTTON_Palette1', '').upper() == color
            assert palette.get('C_SLIDER_Brightness') == str(brightness)

    print(
        f'OK {MODEL}: {len(FACE_DEFINITIONS)} faces + '
        f'{len(SUBMODELS)} supporting submodels')


def print_plan():
    print(f'{MODEL}:')
    print(f'  faces: {", ".join(FACE_DEFINITIONS)}')
    print(f'  track: {TRACK}')
    for start, end, fadeout in choir_blocks():
        print(f'  block {start}-{end}, fadeout={fadeout}')
    for submodel, (color, brightness) in SUBMODELS.items():
        print(f'  {submodel}: {color} at brightness {brightness}')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--clear-only', action='store_true')
    args = parser.parse_args()

    assert_open_sequence()
    rows = inspect_owned()
    print_plan()
    if args.dry_run:
        print('dry-run: no changes')
        return

    clear_owned(rows)
    if not args.clear_only:
        add_tree_choir()
        verify()
    x.save(str(SEQUENCE))
    print(f'saved {SEQUENCE}')


if __name__ == '__main__':
    main()
