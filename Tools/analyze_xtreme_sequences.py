#!/usr/bin/env python3
"""Mine Xtreme Sequences vendor packages (Imports/xS_*) for style/submodel patterns.

For each package: parses the vendor xlights_rgbeffects.xml (models, submodels,
model groups and their members) and the sequence file (.xsq or legacy .xml
xsequence), then emits aggregate stats as JSON for report writing.

Second mode — analyze already-mapped sequences against a specific layout:
    analyze_xtreme_sequences.py --layout <xlights_rgbeffects.xml> <out.json> <seq.xsq> [...]
Used for the Xtreme sequences imported/mapped onto Elliott's own Christmas layout.
"""
import json
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path

IMPORTS = Path("/Volumes/Personal-Drive/xlights/Imports")


def find_sequence_file(pkg: Path):
    cands = sorted(pkg.glob("*.xsq")) + [
        p for p in sorted(pkg.glob("*.xml"))
        if p.name not in ("xlights_rgbeffects.xml", "xlights_networks.xml",
                          "xlights_keybindings.xml", "xlights_rgbeffects.xml.old.xml")
    ]
    # verify it's an xsequence
    for p in cands:
        try:
            head = p.open("rb").read(400).decode("utf-8", "ignore")
        except OSError:
            continue
        if "<xsequence" in head:
            return p
    return None


def parse_layout(pkg: Path):
    f = pkg / "xlights_rgbeffects.xml"
    if not f.exists():
        return None
    root = ET.parse(f).getroot()
    models = {}
    for m in root.iter("model"):
        name = m.get("name")
        if not name:
            continue
        subs = [sm.get("name") for sm in m.findall("subModel")]
        models[name] = {
            "DisplayAs": m.get("DisplayAs"),
            "submodels": subs,
        }
    groups = {}
    for g in root.iter("modelGroup"):
        name = g.get("name")
        members = [x.strip() for x in (g.get("models") or "").split(",") if x.strip()]
        sub_members = [x for x in members if "/" in x]
        groups[name] = {
            "members": members,
            "n_members": len(members),
            "n_submodel_members": len(sub_members),
        }
    return {"models": models, "groups": groups}


def parse_sequence(seq_path: Path):
    root = ET.parse(seq_path).getroot()
    head = root.find("head")
    meta = {}
    if head is not None:
        for k in ("version", "song", "artist", "sequenceDuration", "sequenceTiming"):
            el = head.find(k)
            meta[k] = el.text if el is not None else None
    effect_db = [e.text or "" for e in root.iter("Effect0")]  # not used
    db = root.find("EffectDB")
    settings_db = [e.text or "" for e in db.iter("Effect")] if db is not None else []

    elements = {}
    effect_names = Counter()
    layer_depth = Counter()
    setting_refs = Counter()  # which EffectDB entries actually used
    timing_tracks = []
    ee = root.find("ElementEffects")
    if ee is None:
        return None
    for el in ee.findall("Element"):
        etype = el.get("type")
        name = el.get("name")
        if etype == "timing":
            timing_tracks.append(name)
            continue
        layers = el.findall("EffectLayer")
        n_eff = 0
        for lyr in layers:
            for eff in lyr.findall("Effect"):
                n_eff += 1
                effect_names[eff.get("name")] += 1
                ref = eff.get("ref")
                if ref is not None:
                    setting_refs[int(ref)] += 1
        # nested submodel layers (rare in vendor files but check)
        subs = el.findall("SubModelEffectLayer")
        for lyr in subs:
            for eff in lyr.findall("Effect"):
                n_eff += 1
                effect_names[eff.get("name")] += 1
        if n_eff:
            elements[name] = {"layers": len(layers), "effects": n_eff}
            layer_depth[len(layers)] += 1
    # settings analysis over *used* EffectDB entries, weighted by use count
    buf_styles = Counter()
    layer_methods = Counter()
    transitions = Counter()
    special = Counter()
    for ref, cnt in setting_refs.items():
        if ref >= len(settings_db):
            continue
        s = settings_db[ref]
        m = re.search(r"B_CHOICE_BufferStyle=([^,]+)", s)
        if m:
            buf_styles[m.group(1)] += cnt
        m = re.search(r"T_CHOICE_LayerMethod=([^,]+)", s)
        if m:
            layer_methods[m.group(1)] += cnt
        for key in ("T_CHOICE_In_Transition_Type", "T_CHOICE_Out_Transition_Type"):
            m = re.search(key + r"=([^,]+)", s)
            if m:
                transitions[m.group(1)] += cnt
        if "T_CHECKBOX_Canvas=1" in s:
            special["canvas"] += cnt
        if "Active=TRUE" in s:
            special["value_curves"] += cnt
        if "B_CUSTOM_SubBuffer=" in s:
            special["subbuffer"] += cnt
        if "T_TEXTCTRL_Fadeout=" in s:
            special["fadeout"] += cnt
        if "T_TEXTCTRL_Fadein=" in s:
            special["fadein"] += cnt
    return {
        "meta": meta,
        "n_elements_with_effects": len(elements),
        "elements": elements,
        "effect_names": dict(effect_names.most_common()),
        "layer_depth": dict(sorted(layer_depth.items())),
        "buffer_styles": dict(buf_styles.most_common()),
        "layer_methods": dict(layer_methods.most_common()),
        "transitions": dict(transitions.most_common()),
        "special": dict(special),
        "timing_tracks": timing_tracks,
        "total_effects": sum(effect_names.values()),
    }


def classify_elements(seq, layout):
    """Split sequenced element names into: submodel-group, plain group, whole model, direct submodel."""
    out = {"submodel_group": [], "model_group": [], "model": [], "direct_submodel": [], "unknown": []}
    groups = layout["groups"] if layout else {}
    models = layout["models"] if layout else {}
    for name in seq["elements"]:
        if "/" in name:
            out["direct_submodel"].append(name)
        elif name in groups:
            if groups[name]["n_submodel_members"] > 0:
                out["submodel_group"].append(name)
            else:
                out["model_group"].append(name)
        elif name in models:
            out["model"].append(name)
        else:
            out["unknown"].append(name)
    return out


def parse_layout_file(f: Path):
    root = ET.parse(f).getroot()
    models = {}
    for m in root.iter("model"):
        name = m.get("name")
        if not name:
            continue
        subs = [sm.get("name") for sm in m.findall("subModel")]
        models[name] = {"DisplayAs": m.get("DisplayAs"), "submodels": subs}
    groups = {}
    for g in root.iter("modelGroup"):
        name = g.get("name")
        members = [x.strip() for x in (g.get("models") or "").split(",") if x.strip()]
        groups[name] = {
            "members": members,
            "n_members": len(members),
            "n_submodel_members": len([x for x in members if "/" in x]),
        }
    return {"models": models, "groups": groups}


def main_layout_mode(layout_file: Path, out: Path, seq_files):
    layout = parse_layout_file(layout_file)
    results = {}
    for sf in seq_files:
        sf = Path(sf)
        entry = {"sequence_file": str(sf)}
        try:
            seq = parse_sequence(sf)
        except Exception as e:
            entry["sequence_error"] = str(e)
            results[sf.stem] = entry
            continue
        if seq:
            entry["sequence"] = seq
            cls = classify_elements(seq, layout)
            entry["element_classes"] = {k: len(v) for k, v in cls.items()}
            entry["element_class_names"] = cls
        results[sf.stem] = entry
    out.write_text(json.dumps(results, indent=1))
    for name, e in results.items():
        seq = e.get("sequence")
        print(f"\n== {name}")
        if not seq:
            print("  ERROR:", e.get("sequence_error"))
            continue
        print(f"  v{seq['meta'].get('version')} {seq['n_elements_with_effects']} elements, "
              f"{seq['total_effects']} effects; classes={e['element_classes']}")
        print(f"  top effects: {list(seq['effect_names'].items())[:8]}")
        print(f"  layer depth: {seq['layer_depth']}")
        print(f"  buffer styles: {list(seq['buffer_styles'].items())[:5]}")
        print(f"  layer methods: {list(seq['layer_methods'].items())[:5]}")
        print(f"  special: {seq['special']}")
        print(f"  timing tracks: {seq['timing_tracks']}")


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--layout":
        main_layout_mode(Path(sys.argv[2]), Path(sys.argv[3]), sys.argv[4:])
        return
    results = {}
    for pkg in sorted(IMPORTS.glob("xS_*")):
        if not pkg.is_dir():
            continue
        entry = {"package": pkg.name}
        layout = None
        try:
            layout = parse_layout(pkg)
        except Exception as e:
            entry["layout_error"] = str(e)
        if layout:
            n_models = len(layout["models"])
            n_subs = sum(len(m["submodels"]) for m in layout["models"].values())
            sub_groups = {k: v for k, v in layout["groups"].items() if v["n_submodel_members"] > 0}
            entry["layout"] = {
                "n_models": n_models,
                "n_submodels": n_subs,
                "n_groups": len(layout["groups"]),
                "n_submodel_groups": len(sub_groups),
                "top_submodel_models": sorted(
                    ((k, len(v["submodels"])) for k, v in layout["models"].items() if v["submodels"]),
                    key=lambda x: -x[1])[:15],
            }
        seq_file = find_sequence_file(pkg)
        if seq_file:
            entry["sequence_file"] = seq_file.name
            try:
                seq = parse_sequence(seq_file)
                if seq:
                    entry["sequence"] = seq
                    if layout:
                        cls = classify_elements(seq, layout)
                        entry["element_classes"] = {k: len(v) for k, v in cls.items()}
                        entry["element_class_names"] = cls
            except Exception as e:
                entry["sequence_error"] = str(e)
        results[pkg.name] = entry
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("xtreme_analysis.json")
    out.write_text(json.dumps(results, indent=1))
    # quick console summary
    for name, e in results.items():
        seq = e.get("sequence")
        lay = e.get("layout")
        print(f"\n== {name}")
        if lay:
            print(f"  layout: {lay['n_models']} models, {lay['n_submodels']} submodels, "
                  f"{lay['n_groups']} groups ({lay['n_submodel_groups']} submodel-groups)")
        if seq:
            print(f"  seq: {e.get('sequence_file')} v{seq['meta'].get('version')} "
                  f"{seq['n_elements_with_effects']} elements, {seq['total_effects']} effects")
            if "element_classes" in e:
                print(f"  element classes: {e['element_classes']}")
            top = list(seq["effect_names"].items())[:10]
            print(f"  top effects: {top}")
            print(f"  layer depth: {seq['layer_depth']}")
            print(f"  buffer styles: {list(seq['buffer_styles'].items())[:6]}")
            print(f"  layer methods: {list(seq['layer_methods'].items())[:6]}")
            print(f"  special: {seq['special']}")


if __name__ == "__main__":
    main()
