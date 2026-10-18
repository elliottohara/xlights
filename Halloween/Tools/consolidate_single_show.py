"""Consolidate song layout metadata into the one canonical Halloween show.

Preserves effect order/timing/palettes/settings; only names and media paths are
retargeted. Original layouts, sequences and renders are retained in the backup.
"""
from pathlib import Path
from collections import defaultdict
import copy
import hashlib
import html
import json
import re
import shutil
import socket
import subprocess
import time
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

SHOW = Path(__file__).resolve().parents[1]
REPORT = SHOW / 'single-show-consolidation-latest.json'
record = json.loads(REPORT.read_text())
assert not record.get('consolidated'), 'Consolidation has already been applied.'
backup = Path(record['backup'])
staged = backup / 'Staged'
staged.mkdir(exist_ok=True)

def canon(e, omit=()):
    return (e.tag, tuple(sorted((k, v) for k, v in e.attrib.items() if k not in omit)),
            (e.text or '').strip(), tuple(canon(c) for c in e))

def xl(cmd, **kwargs):
    req = Request('http://127.0.0.1:49913/xlDoAutomation', json.dumps({'cmd': cmd, **kwargs}).encode(), {'Content-Type': 'application/json'})
    with urlopen(req, timeout=90) as response:
        return json.load(response)

def slug(name):
    return re.sub(r'[^A-Za-z0-9]+', '-', name).strip('-')

def unique(name, names, song):
    candidate = name.rstrip() + ' [' + slug(song) + ']'
    suffix = 2
    while candidate in names:
        candidate = name.rstrip() + ' [' + slug(song) + '-' + str(suffix) + ']'
        suffix += 1
    return candidate

missing_assets = set()

def asset(value, folder, strict=False):
    value = value.replace('&comma;', ',')
    decoded = html.unescape(html.unescape(value))
    candidates = []
    for text in [value, decoded]:
        path = Path(text)
        candidates.extend([path] if path.is_absolute() else [folder / path, SHOW / path])
    found = next((p for p in candidates if p.exists()), candidates[0])
    if strict and not found.exists():
        missing_assets.add(str(found))
    return str(found.resolve())

def normalize_child(child, folder):
    child = copy.deepcopy(child)
    for e in child.iter():
        for key, value in list(e.attrib.items()):
            if value and re.search(r'\.(png|jpe?g|gif|bmp|webp|svg|mp4|mov|fs)$', value, re.I):
                e.set(key, asset(value, folder))
    return child

def normalize_settings(text, folder):
    tokens = []
    for token in (text or '').split(','):
        if '=' not in token:
            tokens.append(token)
            continue
        key, value = token.split('=', 1)
        if value and ('FILEPICKER' in key or 'filename' in key.lower()):
            value = asset(value, folder, strict=True).replace(',', '&comma;')
        tokens.append(key + '=' + value)
    return ','.join(tokens)

master_path = SHOW / 'xlights_rgbeffects.xml'
assert master_path.read_bytes() == (backup / 'Before/xlights_rgbeffects.xml').read_bytes(), 'Master changed since snapshot; preserve new edits before retrying.'
tree = ET.parse(master_path)
master = tree.getroot()
models = {m.get('name'): m for m in master.findall('./models/model')}
original_master_models = set(models)
groups = {g.get('name'): g for g in master.findall('./modelGroups/modelGroup')}
for model in models.values():
    for i, child in enumerate(list(model)):
        if child.tag in ['faceInfo', 'stateInfo', 'subModel']:
            model.remove(child)
            model.insert(i, normalize_child(child, SHOW))
group_registry = defaultdict(dict)
for name, group in groups.items():
    group_registry[name][canon(group, ('name',))] = name
definition_registry = {}
archives = {}
plans = {}
sequence_trees = {}

for song in record['songs']:
    name = song['song']
    folder = Path(song['xsq']).parent
    root = ET.parse(backup / 'Before' / Path(song['layout']).relative_to(SHOW)).getroot()
    source_models = {m.get('name'): m for m in root.findall('./models/model')}
    source_groups = {g.get('name'): g for g in root.findall('./modelGroups/modelGroup')}
    aliases, sub_aliases = {}, {}
    for source_name, source in source_models.items():
        if source_name in original_master_models:
            aliases[source_name] = source_name
            continue
        # These legacy reference models have no installed controller. Keep
        # their geometry/definitions available without adding physical outputs.
        physical = copy.deepcopy(source)
        for key in ['name', 'Controller', 'StartChannel', 'ModelChain', 'Active', 'LayoutGroup']:
            physical.attrib.pop(key, None)
        for child in list(physical):
            if child.tag in ['ControllerConnection', 'faceInfo', 'stateInfo', 'subModel']:
                physical.remove(child)
        signature = canon(physical)
        key = (source_name, signature)
        if key in archives:
            aliases[source_name] = archives[key]
            continue
        target_name = source_name if source_name not in models else unique(source_name, models, name)
        target = copy.deepcopy(source)
        target.set('name', target_name)
        target.set('Controller', 'No Controller')
        target.set('StartChannel', '1')
        target.set('Active', '0')
        target.set('LayoutGroup', 'Unassigned')
        target.attrib.pop('ModelChain', None)
        for child in list(target):
            if child.tag in ['ControllerConnection', 'faceInfo', 'stateInfo', 'subModel']:
                target.remove(child)
        master.find('models').append(target)
        models[target_name] = target
        archives[key] = target_name
        aliases[source_name] = target_name
    for source_name, source in source_models.items():
        destination = models[aliases[source_name]]
        for raw in source.findall('subModel'):
            child = normalize_child(raw, folder)
            old_name = child.get('name')
            candidates = {c.get('name'): c for c in destination.findall('subModel')}
            target_name = old_name
            if old_name in candidates and canon(candidates[old_name], ('name',)) != canon(child, ('name',)):
                identical = next((n for n, c in candidates.items() if canon(c, ('name',)) == canon(child, ('name',))), None)
                target_name = identical or unique(old_name, candidates, name)
            if target_name not in candidates:
                child.set('name', target_name)
                destination.append(child)
            sub_aliases[source_name + '/' + old_name] = aliases[source_name] + '/' + target_name
    definitions = {'faceInfo': {}, 'stateInfo': {}}
    for tag in definitions:
        bundles = defaultdict(dict)
        for source_name, source in source_models.items():
            for raw in source.findall(tag):
                child = normalize_child(raw, folder)
                bundles[child.get('Name')][aliases[source_name]] = child
        for old_name, bundle in bundles.items():
            signature = tuple(sorted((n, canon(c, ('Name',))) for n, c in bundle.items()))
            registry_key = (tag, old_name, signature)
            if registry_key in definition_registry:
                target_name = definition_registry[registry_key]
            else:
                conflicts = []
                existing_names = set()
                for model_name, child in bundle.items():
                    current = {c.get('Name'): c for c in models[model_name].findall(tag)}
                    existing_names.update(current)
                    if old_name in current and canon(current[old_name], ('Name',)) != canon(child, ('Name',)):
                        conflicts.append(model_name)
                target_name = unique(old_name, existing_names, name) if conflicts else old_name
                definition_registry[registry_key] = target_name
            definitions[tag][old_name] = target_name
            for model_name, child in bundle.items():
                existing = next((c for c in models[model_name].findall(tag) if c.get('Name') == target_name), None)
                if existing is None:
                    child.set('Name', target_name)
                    models[model_name].append(child)
                else:
                    assert canon(existing, ('Name',)) == canon(child, ('Name',)), (name, tag, old_name, model_name)
    seq_path = Path(song['xsq'])
    seq_tree = ET.parse(backup / 'Before' / seq_path.relative_to(SHOW))
    seq_root = seq_tree.getroot()
    db = list(seq_root.find('EffectDB'))
    needs_default_state = False
    for e in seq_root.findall('./ElementEffects/Element'):
        for effect in e.findall('.//Effect'):
            if effect.get('name') == 'State':
                settings = dict(t.split('=', 1) for t in (db[int(effect.get('ref'))].text or '').split(',') if '=' in t)
                if not settings.get('E_CHOICE_State_StateDefinition'):
                    needs_default_state = True
    if needs_default_state:
        default_name = 'Imported default [' + slug(name) + ']'
        definitions['stateInfo'][''] = default_name
        for source_name, source in source_models.items():
            first = source.find('stateInfo')
            if first is not None:
                child = normalize_child(first, folder)
                child.set('Name', default_name)
                models[aliases[source_name]].append(child)
    group_aliases, visiting = {}, set()
    def resolve(member):
        if member in source_groups:
            return merge_group(member)
        if member in sub_aliases:
            return sub_aliases[member]
        if '/' in member:
            parent, sub = member.split('/', 1)
            return aliases.get(parent, parent) + '/' + sub
        return aliases.get(member, member)
    def merge_group(old_name):
        if old_name in group_aliases:
            return group_aliases[old_name]
        assert old_name not in visiting, ('Group cycle', name, old_name)
        visiting.add(old_name)
        group = copy.deepcopy(source_groups[old_name])
        group.set('models', ','.join(resolve(n) for n in group.get('models', '').split(',') if n))
        signature = canon(group, ('name',))
        existing = group_registry[old_name].get(signature)
        if existing is None:
            existing = old_name if old_name not in groups else unique(old_name, groups, name)
            group.set('name', existing)
            groups[existing] = group
            group_registry[old_name][signature] = existing
            master.find('modelGroups').append(group)
        visiting.remove(old_name)
        group_aliases[old_name] = existing
        return existing
    for group_name in source_groups:
        merge_group(group_name)
    all_aliases = {**aliases, **sub_aliases, **group_aliases}
    original_effect_count = len(seq_root.findall('./ElementEffects/Element[@type="model"]//Effect'))
    timing_before = [canon(e) for e in seq_root.findall('./ElementEffects/Element') if e.get('type') == 'timing']
    for entry in seq_root.find('EffectDB'):
        entry.text = normalize_settings(entry.text, folder)
    media = seq_root.find('head/mediaFile')
    if media is not None and media.text:
        media.text = asset(media.text, folder, strict=True)
    db_parent = seq_root.find('EffectDB')
    setting_indexes = {e.text or '': i for i, e in enumerate(db_parent)}
    for tag in ['DisplayElements', 'ElementEffects']:
        parent = seq_root.find(tag)
        if parent is None:
            continue
        for element in parent:
            if element.get('type') != 'model':
                continue
            original_target = element.get('name')
            element.set('name', all_aliases.get(original_target, original_target))
            if tag != 'ElementEffects':
                continue
            for effect in element.findall('.//Effect'):
                if effect.get('ref') is None:
                    continue
                original_ref = int(effect.get('ref'))
                old_settings = list(db_parent)[original_ref].text or ''
                tokens = []
                saw_state_definition = False
                for token in old_settings.split(','):
                    if '=' not in token:
                        tokens.append(token)
                        continue
                    key, value = token.split('=', 1)
                    if key == 'E_CHOICE_Faces_FaceDefinition':
                        value = definitions['faceInfo'].get(value, value)
                    elif key in ['E_CHOICE_Faces_UseState', 'E_CHOICE_State_StateDefinition']:
                        if key == 'E_CHOICE_State_StateDefinition':
                            saw_state_definition = True
                        value = definitions['stateInfo'].get(value, value)
                    elif ('Model' in key or 'Group' in key) and value in all_aliases:
                        value = all_aliases[value]
                    tokens.append(key + '=' + value)
                if effect.get('name') == 'State' and needs_default_state and not saw_state_definition:
                    tokens.append('E_CHOICE_State_StateDefinition=' + definitions['stateInfo'][''])
                text = ','.join(tokens)
                if text != old_settings:
                    if text not in setting_indexes:
                        entry = copy.deepcopy(list(db_parent)[original_ref])
                        entry.text = text
                        setting_indexes[text] = len(db_parent)
                        db_parent.append(entry)
                    effect.set('ref', str(setting_indexes[text]))
    assert len(seq_root.findall('./ElementEffects/Element[@type="model"]//Effect')) == original_effect_count
    assert [canon(e) for e in seq_root.findall('./ElementEffects/Element') if e.get('type') == 'timing'] == timing_before
    dest = staged / seq_path.relative_to(SHOW)
    dest.parent.mkdir(parents=True, exist_ok=True)
    seq_tree.write(dest, encoding='utf-8', xml_declaration=True)
    view = ET.SubElement(master.find('views'), 'view', name='Song: ' + name)
    source_view = next((v for v in root.findall('./views/view') if v.get('name') == 'Default'), None)
    view.set('models', ','.join(resolve(n) for n in source_view.get('models', '').split(',') if n) if source_view is not None else ','.join(group_aliases.values()))
    plans[name] = {'aliases': all_aliases, 'definitions': definitions, 'effect_count': original_effect_count,
                   'xsq': str(seq_path), 'staged': str(dest), 'rendered': False, 'timing_tracks_preserved': True}
    print('STAGED SONG', name, original_effect_count, 'effects;', sum(k != v for k, v in all_aliases.items()), 'renamed targets', flush=True)

assert not missing_assets, ('Missing sequence assets', sorted(missing_assets))
# Every imported group must resolve to a retained model/group. Source groups
# occasionally contain obsolete names; retain that fact for review, not hardware.
missing_members = []
for name, group in groups.items():
    for member in group.get('models', '').split(','):
        if member and member not in groups and member.split('/')[0] not in models:
            missing_members.append((name, member))
assert not missing_members, ('Unresolved group members', missing_members[:30])
tree.write(staged / 'xlights_rgbeffects.xml', encoding='utf-8', xml_declaration=True)
(backup / 'migration plan.json').write_text(json.dumps(plans, indent=2))
record.update(plan=str(backup / 'migration plan.json'), group_count=len(groups), model_count=len(models),
              legacy_reference_models=sorted(set(models) - {m.get('name') for m in ET.parse(backup / 'Before/xlights_rgbeffects.xml').findall('./models/model')}),
              all_sequence_assets_resolved=True)
REPORT.write_text(json.dumps(record, indent=2))
print('STAGED CONSOLIDATED LAYOUT', len(models), 'models,', len(groups), 'groups', flush=True)
xl('closexLights', force='false')
for _ in range(60):
    try:
        with socket.create_connection(('127.0.0.1', 49913), timeout=.5):
            pass
    except OSError:
        break
    time.sleep(.5)
else:
    raise RuntimeError('xLights did not close')
shutil.copy2(staged / 'xlights_rgbeffects.xml', master_path)
for name, plan in plans.items():
    shutil.copy2(plan['staged'], plan['xsq'])
subprocess.run(['open', '-n', '-a', 'xLights', '--args', '-q', '-a', '-s', str(SHOW)], check=True)
for _ in range(90):
    try:
        xl('getVersion')
        break
    except (OSError, TimeoutError):
        time.sleep(2)
else:
    raise RuntimeError('xLights did not reopen')
xl('saveLayout')
controllers = xl('getControllers')['controllers']
assert {(c['name'], c['startchannel'], c['channels']) for c in controllers} == {(c['name'], c['startchannel'], c['channels']) for c in record['master_controllers_before']}, 'Consolidation changed physical allocation'
record.update(consolidated=True, controllers_after=controllers, songs=plans)
REPORT.write_text(json.dumps(record, indent=2))
print('CONSOLIDATED: ONE HALLOWEEN SHOW; PHYSICAL CONTROLLER RANGES UNCHANGED', flush=True)
