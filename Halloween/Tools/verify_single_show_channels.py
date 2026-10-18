"""Inspect rendered pixels at the final physical addresses, across all songs."""
from pathlib import Path
from compression import zstd
import ast, bisect, json, struct

SHOW = Path(__file__).resolve().parents[1]
record = json.loads((SHOW / 'single-show-consolidation-latest.json').read_text())
assert record['all_local_renders_complete']
backup = Path(record['backup'])
reference = json.loads((backup / 'physical output reference.json').read_text())
module = ast.parse((SHOW / 'Sequences/I Knew It I Knew You/Tools/verify_mapping.py').read_text())
exec(compile(ast.Module(body=[next(n for n in module.body if isinstance(n, ast.ClassDef) and n.name == 'FSEQ')], type_ignores=[]), '<FSEQ>', 'exec'))
models = {m['name']: m for c in reference['portmaps'].values() for ports in c.values() for p in ports for m in p.get('models', [])}
sign = next(c for c in reference['controllers'] if c['name'] == 'FPP-TUNETO')
models['Tune To'] = {'startchannel': sign['startchannel'], 'channels': sign['channels']}
targets = {n: models[n] for n in ['Window - Bottom Left', 'House Left', 'Lantana 01', 'Lantana 08', 'Lantana 09', 'Lantana 11', 'Column Left', 'Tune To']}
results = {}
for name, song in record['songs'].items():
    reader = FSEQ(Path(song['xsq']).with_suffix('.fseq'))
    counts = {n: 0 for n in targets}
    for ms in range(0, reader.frames * reader.step, 1000):
        for n, m in targets.items():
            counts[n] += any(reader.model(ms, m['startchannel'], m['channels']))
    reader.f.close()
    assert counts['Tune To'] > 0, (name, 'sign is black')
    results[name] = counts
    print('PHYSICAL CHANNEL SAMPLES', name, counts, flush=True)
assert any(v['Lantana 11'] for v in results.values())
assert any(v['House Left'] for v in results.values())
(backup / 'final physical channel samples.json').write_text(json.dumps({'addresses': targets, 'lit_samples_by_song': results, 'sample_interval_ms': 1000}, indent=2))
print('FINAL PHYSICAL ADDRESS SAMPLING COMPLETE', flush=True)
