"""Audit native-saved choreography against staged migration, before uploading."""
from pathlib import Path
import html, json, struct
import xml.etree.ElementTree as ET

SHOW = Path(__file__).resolve().parents[1]
def verify(name, record):
    backup = Path(record['backup']); song = record['songs'][name]; path = Path(song['xsq'])
    old = ET.parse(backup / 'Staged' / path.relative_to(SHOW)).getroot()
    new = ET.parse(path).getroot()
    removed = set(record['empty_groups_removed']) | {'Elliott - GE Flake N 1', 'Elliott - GE Flake N 2', 'GE Flake A 1', 'GE Flake A 2', 'Singing Bulb - Left', 'Singing Bulb - Right'}
    removed.update(record.get('inactive_targets_removed', []))
    if name == 'Thriller Xtreme Remap' and record.get('thriller_sign_repair'):
        # The previously empty sign is intentionally repaired with native
        # projector import and the standard frequency overlay. Its independent
        # importer audit verifies the cloned visuals; all other targets below
        # must still match the original choreography exactly.
        removed.add('Tune To')
    with (backup / 'Before' / path.with_suffix('.fseq').relative_to(SHOW)).open('rb') as stream: header = stream.read(32)
    end = struct.unpack_from('<I', header, 14)[0] * header[18]
    def canonical(root, original):
        db = list(root.find('EffectDB')); palettes = list(root.find('ColorPalettes'))
        def node(e):
            attrs = dict(e.attrib)
            if e.tag == 'Effect' and e.get('ref') is not None:
                if original and int(attrs.get('endTime', 0)) > end:
                    if int(attrs.get('startTime', 0)) >= end: return None
                    attrs['endTime'] = str(end)
                settings = dict(t.split('=', 1) for t in (db[int(e.get('ref'))].text or '').split(',') if '=' in t)
                for k, v in list(settings.items()):
                    if 'FILEPICKER' in k or 'filename' in k.lower():
                        v = html.unescape(v); settings[k] = v
                    if v.startswith(str(SHOW) + '/'): settings[k] = v[len(str(SHOW)) + 1:]
                if settings.get('B_CHOICE_PerPreviewCamera') == '2D': settings.pop('B_CHOICE_PerPreviewCamera')
                for key in ['ref', 'palette', 'id']: attrs.pop(key, None)
                return e.tag, tuple(sorted(attrs.items())), tuple(sorted(settings.items())), palettes[int(e.get('palette'))].text
            children = tuple(v for c in e if (v := node(c)) is not None)
            return e.tag, tuple(sorted(attrs.items())), children
        rows = {}
        for row in root.find('ElementEffects'):
            if row.get('name') == 'Tune To' and name == 'Thriller Xtreme Remap' and record.get('thriller_sign_repair'): continue
            if original and row.get('name') in removed: continue
            if row.get('type') != 'timing' and next(row.iter('Effect'), None) is None: continue
            rows[row.get('name')] = node(row)
        return rows
    a, b = canonical(old, True), canonical(new, False)
    assert a.keys() == b.keys(), (name, 'rows', a.keys() ^ b.keys())
    for key in a: assert a[key] == b[key], (name, 'authored data differs', key)
    return True

if __name__ == '__main__':
    record = json.loads((SHOW / 'single-show-consolidation-latest.json').read_text())
    for name, song in record['songs'].items():
        if song.get('rendered'):
            verify(name, record); print('SAVED CHOREOGRAPHY VERIFIED', name)
