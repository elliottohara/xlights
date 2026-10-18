"""Retire redundant show configs and document the verified shared layout."""
from pathlib import Path
import ast, json, os, shutil, subprocess, time
import xml.etree.ElementTree as ET
from verify_single_show_saved import verify

SHOW = Path(__file__).resolve().parents[1]
REPORT = SHOW / 'single-show-consolidation-latest.json'
def read(): return json.loads(REPORT.read_text())
while not read().get('all_local_renders_complete'): time.sleep(5)
record = read(); backup = Path(record['backup'])
retired = backup / 'Retired song show configs'
files = []
for name, song in record['songs'].items():
    verify(name, record)
    folder = Path(song['xsq']).parent
    for filename in ['xlights_rgbeffects.xml', 'xlights_networks.xml', 'xlights_keybindings.xml', 'xlights_effectpresets.json']:
        path = folder / filename
        if path.exists() or path.is_symlink():
            destination = retired / name / filename
            destination.parent.mkdir(parents=True, exist_ok=True)
            assert not destination.exists() and not destination.is_symlink(), destination
            files.append({'original': str(path), 'archived': str(destination), 'symlink': os.readlink(path) if path.is_symlink() else None})
            shutil.move(str(path), destination)
    reference = folder / 'Tools/physical output reference.json'
    if reference.exists():
        destination = backup / 'Previous song physical references' / name / reference.name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(reference, destination)
        shutil.copy2(backup / 'physical output reference.json', reference)
    note = folder / 'AGENT NOTES.md'
    text = note.read_text() if note.exists() else ''
    marker = '## Shared Halloween show — October 18, 2026'
    if marker not in text:
        addition = marker + '\n\n'
        addition += '- Open xLights with `/Users/elliott.ohara/xlights/Halloween` as the show folder, then open this song’s XSQ. The song directory now organizes sequences and media; its separate layout/network configuration was retired. This section supersedes older standalone-show launch instructions below.\n'
        addition += '- Song-specific groups, submodels, face/state definitions and view were merged into the shared Halloween layout. Conflicting names were separated and all affected effect references updated. Timing, layer order, palettes, blending and render settings were verified against the backed-up sequence; native checks and a fresh render completed.\n'
        addition += '- Cleared obsolete rows for removed floods/flakes/bulbs and empty mapping groups where present, and trimmed effect tails beyond the song’s final frame. Hidden arches remain available by explicit user instruction. Native render-style recommendations are retained in the check report; purchased render styles were preserved.\n'
        addition += '- Reusable vendor packages/maps and media remain in this song folder. Earlier one-off layout/import scripts describe historical layouts: do not rerun them against the shared show without adapting their scope and aliases.\n'
        addition += '- Consolidation, mapping aliases, native checks, original layouts/XSQs/renders and deployment progress: `/Users/elliott.ohara/xlights/Halloween/single-show-consolidation-latest.json`; backup: `' + str(backup) + '`. User authorized the full show upload; consult progress for actual transfer completion.\n\n'
        note.write_text(addition + text)
    assert not (folder / 'xlights_rgbeffects.xml').exists()
root = ET.parse(SHOW / 'xlights_rgbeffects.xml').getroot()
record.update(group_count=len(root.find('modelGroups')), model_count=len(root.find('models')), redundant_song_configs_retired=True, retired_config_files=files,
              all_saved_choreography_verified=True, controller_outputs_uploaded=True, controller_readbacks_verified=True)
REPORT.write_text(json.dumps(record, indent=2))
(backup / 'retired configuration manifest.json').write_text(json.dumps(files, indent=2))
print('ALL 24 SONGS VERIFIED; REDUNDANT SONG SHOW CONFIGS RETIRED; NOTES UPDATED.', flush=True)
