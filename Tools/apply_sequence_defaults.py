"""Mirror projector choreography on Tune To with a readable frequency overlay.

Uses native importXLightsSequence and addEffect. XML edits only clear the explicitly
owned Tune To target and insert empty overlay layers; donor effects are native
clones, with their settings, palettes, timing and relative layers preserved.
"""
import argparse
from datetime import datetime
import hashlib
import html
import json
from pathlib import Path
import re
import shutil
import xml.etree.ElementTree as ET
import zipfile

import xlights_api as x

def _kv(value):
    return dict(t.split('=',1) for t in (value or '').split(',') if '=' in t)

def _signature(root,element,folder=None):
    db=list(root.find('EffectDB'));pal=list(root.find('ColorPalettes'))
    def settings(f):
        cfg=_kv(db[int(f.get('ref'))].text)
        if folder:
            for key,value in list(cfg.items()):
                if value and ('FILEPICKER' in key or key.endswith('Filename')):
                    path=Path(html.unescape(value).replace('&comma;',','))
                    cfg[key]=str(path if path.is_absolute() else folder/path)
        return cfg
    return [[(f.get('name'),f.get('startTime'),f.get('endTime'),
              settings(f),pal[int(f.get('palette'))].text)
             for f in layer.findall('Effect')] for layer in element.findall('EffectLayer')]

def _equivalent(a,b):
    """Native media import may copy identical assets into the song Media tree."""
    if len(a)!=len(b):return False
    hashes={}
    def digest(path):
        if path not in hashes:
            with Path(path).open('rb') as stream:hashes[path]=hashlib.file_digest(stream,'sha256').hexdigest()
        return hashes[path]
    for left,right in zip(a,b):
        if len(left)!=len(right):return False
        for x,y in zip(left,right):
            if x[:3]!=y[:3] or x[4]!=y[4] or x[3].keys()!=y[3].keys():return False
            for key,value in x[3].items():
                other=y[3][key]
                if value==other:continue
                if not ('FILEPICKER' in key or key.endswith('Filename')):return False
                if not value or not other or not Path(value).is_file() or not Path(other).is_file():return False
                if digest(value)!=digest(other):return False
    return True

def apply_defaults(sequence, source=None, frequency=None):
    sequence=Path(sequence).resolve();folder=sequence.parent
    policy_path=folder/'Tools/sequence_defaults.json'
    policy=json.loads(policy_path.read_text()) if policy_path.exists() else {}
    cfg=policy.get('tune_to',{})
    if cfg.get('enabled',True) is False:
        return {'enabled':False}
    frequency=frequency or cfg.get('frequency','87.9')
    assert re.fullmatch(r'\d{2,3}(?:\.\d)?',str(frequency)),frequency
    opened=x.xl('getOpenSequence',timeout=15)
    assert Path(opened['fullseq']).resolve()==sequence,('Wrong sequence open',opened)
    x.save(str(sequence))
    root=ET.parse(sequence).getroot()
    layout_path=folder/'xlights_rgbeffects.xml'
    for candidate in [folder, *folder.parents]:
        policy=candidate/'show-folder-policy.json'
        if policy.exists() and json.loads(policy.read_text()).get('mode')=='single':
            layout_path=candidate/'xlights_rgbeffects.xml'
            break
    layout=ET.parse(layout_path).getroot()
    asset_base=layout_path.parent
    model_names={m.get('name') for m in layout.findall('./models/model')}
    assert 'Tune To' in model_names,'Layout has no Tune To model; do not invent output hardware.'
    groups={g.get('name'):g.get('models','').split(',') for g in layout.findall('./modelGroups/modelGroup')}
    def expand(n,seen=()):
        assert n not in seen,('Group cycle',n)
        return [v for m in groups[n] if m for v in expand(m,seen+(n,))] if n in groups else [n]
    elements={e.get('name'):e for e in root.findall('./ElementEffects/Element') if e.get('type')=='model'}
    if source is None:
        candidates=[n for n,e in elements.items() if e.findall('.//Effect') and set(expand(n))=={'Projector'}]
        assert len(candidates)<=1,('Multiple projector effect rows; provide an explicit source',candidates)
        source=candidates[0] if candidates else None
    if source:
        assert source in elements and set(expand(source))=={'Projector'},('Source must exclusively drive Projector',source)
    source_sig=_signature(root,elements[source],asset_base) if source else []
    other_sigs={n:_signature(root,e,asset_base) for n,e in elements.items() if n!='Tune To'}
    duration=int(opened['len'])//int(opened['framems'])*int(opened['framems'])
    band=cfg.get('band_percent',30)
    assert 15<=band<=50,band
    subbuffer=f'B_CUSTOM_SubBuffer=0x0x100x{band}'
    old_target=_signature(root,elements['Tune To'],asset_base) if 'Tune To' in elements else []
    if (len(old_target)==len(source_sig)+2 and _equivalent(old_target[2:],source_sig)
        and len(old_target[0])==len(old_target[1])==1
        and old_target[0][0][0]=='Text' and old_target[1][0][0]=='On'
        and old_target[0][0][1:3]==('0',str(duration))
        and old_target[1][0][1:3]==('0',str(duration))
        and old_target[0][0][3].get('E_TEXTCTRL_Text')==f'Tune to {frequency}'
        and all(old_target[i][0][3].get('B_CUSTOM_SubBuffer')==subbuffer.split('=',1)[1] for i in [0,1])):
        return dict(enabled=True,unchanged=True,source=source,target='Tune To',frequency=str(frequency),
                    mirrored_effects=sum(map(len,source_sig)),overlay_layers=[0,1],band_percent=band,
                    all_other_effects_unchanged=True)
    backup=folder/'Backups'/('Projector Tune To '+datetime.now().strftime('%Y%m%d-%H%M%S-%f'))
    backup.mkdir(parents=True)
    shutil.copy2(sequence,backup/sequence.name)
    x.xl('closeSequence',quiet='true',force='false')
    tree=ET.parse(sequence);r=tree.getroot();parent=r.find('ElementEffects')
    target=next((e for e in parent if e.get('name')=='Tune To'),None)
    if target is None:
        target=ET.SubElement(parent,'Element',name='Tune To',type='model',visible='true',collapsed='false')
        ET.SubElement(r.find('DisplayElements'),'Element',name='Tune To',type='model',visible='true',collapsed='false')
    # Clear all old target layers, including layers beyond the source's count.
    # cloneModelEffects eraseModel alone does not clear those extra layers.
    for layer in list(target):
        if layer.tag=='EffectLayer':target.remove(layer)
    ET.SubElement(target,'EffectLayer')
    tree.write(sequence,encoding='utf-8',xml_declaration=True)
    x.xl('openSequence',seq=str(sequence),promptIssues='false')
    if source:
        # Use the native importer: this xLights build caches the clone source in
        # a function-static pointer, which becomes stale across close/reopen.
        # A mapped native import remains safe across repeated applications.
        snapshot=ET.parse(backup/sequence.name)
        for tag in ['ElementEffects','DisplayElements']:
            for el in list(snapshot.getroot().find(tag)):
                if el.get('name')!=source:snapshot.getroot().find(tag).remove(el)
        assets=set()
        for layer in source_sig:
            for effect in layer:
                for key,value in effect[3].items():
                    if value and ('FILEPICKER' in key or key.endswith('Filename')):
                        asset=Path(value)
                        assert asset.exists(),('Missing projector asset',asset)
                        assets.add(asset)
        audio=snapshot.getroot().findtext('head/mediaFile')
        if audio and Path(audio).exists():assets.add(Path(audio))
        for entry in snapshot.getroot().find('EffectDB'):
            if not entry.text:continue
            fields=[]
            for token in entry.text.split(','):
                if '=' not in token:fields.append(token);continue
                key,value=token.split('=',1)
                if value and ('FILEPICKER' in key or key.endswith('Filename')):
                    path=Path(value.replace('&comma;',','))
                    if not path.is_absolute():
                        value=str(asset_base/path).replace(',','&comma;')
                fields.append(key+'='+value)
            entry.text=','.join(fields)
        snapshot_path=backup/'Projector source.xsq'
        snapshot.write(snapshot_path,encoding='utf-8',xml_declaration=True)
        package=backup/'Projector source.zip'
        by_name={}
        for asset in assets:
            if asset.name in by_name:
                with asset.open('rb') as a,by_name[asset.name].open('rb') as b:
                    assert hashlib.file_digest(a,'sha256').digest()==hashlib.file_digest(b,'sha256').digest(),('Conflicting projector media filenames',asset,by_name[asset.name])
            else:by_name[asset.name]=asset
        with zipfile.ZipFile(package,'w',compression=zipfile.ZIP_STORED) as archive:
            archive.write(snapshot_path,'Projector source/Projector source.xsq')
            archive.write(layout_path,'Projector source/xlights_rgbeffects.xml')
            for asset in by_name.values():
                archive.write(asset,'Projector source/Media/'+asset.name)
        mapfile=backup/'Projector to Tune To.xjmap'
        mapfile.write_text(json.dumps(dict(mappings=[dict(model='Tune To',strand='',node='',mapping=source,color='#FFFFFF')],
            timingtracks=[dict(name=e.get('name'),enabled=False) for e in root.findall('./ElementEffects/Element') if e.get('type')=='timing'],
            eraseexisting=False,importblendmode=True,importfacestosequence=False,importmedia=True,
            videodir=str(folder/'Media/VendorVideos'),imagedir=str(folder/'Media/VendorImages'),
            shaderdir=str(folder/'Media/VendorShaders'),facesdir=str(folder/'Media/VendorFaces')),indent=2))
        x.xl('importXLightsSequence',filename=str(package),mapmethod='file',mapfile=str(mapfile),importmedia='true')
        x.save(str(sequence));x.xl('closeSequence',quiet='true',force='false')
        tree=ET.parse(sequence);r=tree.getroot()
        target=next(e for e in r.findall('./ElementEffects/Element') if e.get('name')=='Tune To')
        assert _equivalent(_signature(r,target,asset_base),source_sig),'Native projector import differs from source'
        package.unlink()  # Generated package is recoverable from the saved source and media.
        # xLights composites from the last layer toward layer zero. Reserve two
        # top layers for the label and its solid black backing strip.
        target.insert(0,ET.Element('EffectLayer'))
        target.insert(0,ET.Element('EffectLayer'))
        tree.write(sequence,encoding='utf-8',xml_declaration=True)
        x.xl('openSequence',seq=str(sequence),promptIssues='false')
    common=subbuffer+',T_CHOICE_LayerMethod=Normal,T_TEXTCTRL_Fadein=0,T_TEXTCTRL_Fadeout=0'
    x.add_effect('Tune To',1,'On',common+',E_TEXTCTRL_Eff_On_Start=100,E_TEXTCTRL_Eff_On_End=100',
                 'C_BUTTON_Palette1=#000000,C_CHECKBOX_Palette1=1',0,duration)
    text=f'Tune to {frequency}'
    settings=(common+',E_CHOICE_Text_Dir=none,E_CHOICE_Text_Effect=normal,E_CHOICE_Text_Font=Use OS Fonts,'
              'E_FONTPICKER_Text_Font=Arial 14,E_TEXTCTRL_Text='+text+
              ',E_TEXTCTRL_Text_Speed=0,E_SLIDER_Text_XStart=0,E_SLIDER_Text_YStart=0')
    x.add_effect('Tune To',0,'Text',settings,'C_BUTTON_Palette1=#FFFFFF,C_CHECKBOX_Palette1=1',0,duration)
    x.save(str(sequence))
    final=ET.parse(sequence).getroot()
    final_elements={e.get('name'):e for e in final.findall('./ElementEffects/Element') if e.get('type')=='model'}
    assert all(_signature(final,final_elements[n],asset_base)==sig for n,sig in other_sigs.items()),'A non-Tune To effect changed'
    target_sig=_signature(final,final_elements['Tune To'],asset_base)
    assert _equivalent(target_sig[2:],source_sig) if source else len(target_sig)==2
    result=dict(enabled=True,source=source,target='Tune To',frequency=str(frequency),
                mirrored_effects=sum(map(len,source_sig)),overlay_layers=[0,1],
                band_percent=band,backup=str(backup),all_other_effects_unchanged=True)
    (folder/'Tools/tune_to_defaults_applied.json').write_text(json.dumps(result,indent=2))
    return result

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('sequence',type=Path)
    parser.add_argument('--source')
    parser.add_argument('--frequency')
    args=parser.parse_args()
    print(json.dumps(apply_defaults(args.sequence,args.source,args.frequency),indent=2),flush=True)

if __name__=='__main__':main()
