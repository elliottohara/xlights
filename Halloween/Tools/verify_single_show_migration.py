"""Prove that consolidation changed references, not authored choreography."""
from pathlib import Path
import html
import json
import xml.etree.ElementTree as ET

SHOW = Path(__file__).resolve().parents[1]
REPORT = SHOW / 'single-show-consolidation-latest.json'
record = json.loads(REPORT.read_text())
backup = Path(record['backup'])

def canon(e):
    return (e.tag, tuple(sorted(e.attrib.items())), (e.text or '').strip(), tuple(canon(c) for c in e))

def asset(value, folder):
    value = value.replace('&comma;', ',')
    candidates = []
    for text in [value, html.unescape(html.unescape(value))]:
        p = Path(text)
        candidates.extend([p] if p.is_absolute() else [folder / p, SHOW / p])
    found = next((p for p in candidates if p.exists()), candidates[0])
    assert found.exists(), found
    return str(found.resolve()).replace(',', '&comma;')

results = {}
for name, song in record['songs'].items():
    path = Path(song['xsq'])
    old = ET.parse(backup / 'Before' / path.relative_to(SHOW)).getroot()
    new = ET.parse(path).getroot()
    assert canon(old.find('ColorPalettes')) == canon(new.find('ColorPalettes')), name
    for tag in ['DisplayElements', 'ElementEffects']:
        a, z = old.find(tag), new.find(tag)
        assert len(a) == len(z), (name, tag)
        for x, y in zip(a, z):
            expected = dict(x.attrib)
            if x.get('type') == 'model':
                expected['name'] = song['aliases'].get(x.get('name'), x.get('name'))
            assert expected == y.attrib, (name, tag, x.attrib, y.attrib)
            if tag == 'ElementEffects' and x.get('type') == 'timing':
                assert canon(x) == canon(y), (name, 'timing')
    old_db, new_db = list(old.find('EffectDB')), list(new.find('EffectDB'))
    count = 0
    for a, z in zip(old.findall('./ElementEffects/Element'), new.findall('./ElementEffects/Element')):
        if a.get('type') != 'model':
            continue
        # Layer architecture and all attributes except the deduplicated settings
        # reference must be identical, including ids, timing and palette index.
        x, y = list(a.iter()), list(z.iter())
        assert len(x) == len(y), (name, a.get('name'))
        for before, after in zip(x[1:], y[1:]):
            assert before.tag == after.tag
            ba, aa = dict(before.attrib), dict(after.attrib)
            ba.pop('ref', None)
            aa.pop('ref', None)
            assert ba == aa, (name, a.get('name'), before.attrib, after.attrib)
            if before.tag != 'Effect' or before.get('ref') is None:
                continue
            expected = []
            saw_definition = False
            for token in (old_db[int(before.get('ref'))].text or '').split(','):
                if '=' not in token:
                    expected.append(token)
                    continue
                key, value = token.split('=', 1)
                if value and ('FILEPICKER' in key or 'filename' in key.lower()):
                    value = asset(value, path.parent)
                if key == 'E_CHOICE_Faces_FaceDefinition':
                    value = song['definitions']['faceInfo'].get(value, value)
                elif key in ['E_CHOICE_Faces_UseState', 'E_CHOICE_State_StateDefinition']:
                    saw_definition |= key == 'E_CHOICE_State_StateDefinition'
                    value = song['definitions']['stateInfo'].get(value, value)
                elif ('Model' in key or 'Group' in key) and value in song['aliases']:
                    value = song['aliases'][value]
                expected.append(key + '=' + value)
            if before.get('name') == 'State' and '' in song['definitions']['stateInfo'] and not saw_definition:
                expected.append('E_CHOICE_State_StateDefinition=' + song['definitions']['stateInfo'][''])
            assert ','.join(expected) == (new_db[int(after.get('ref'))].text or ''), (name, a.get('name'), 'settings')
            count += 1
    assert count == song['effect_count'], (name, count, song['effect_count'])
    results[name] = {'effects_verified': count, 'timing_palettes_layers_blending_and_render_settings_preserved': True}
    print('VERIFIED CHOREOGRAPHY', name, count, flush=True)
(backup / 'migration verification.json').write_text(json.dumps(results, indent=2))
record['migration_semantics_verified'] = True
REPORT.write_text(json.dumps(record, indent=2))
print('ALL 24 MIGRATIONS VERIFIED', flush=True)
