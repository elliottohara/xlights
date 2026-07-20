"""PC1 "your name" meteor chase into Christ (whole house + matrices).

Restores the proven `Whole Scene w Matrixes` Per-Preview `Meteors Implode`
aimed at Christ (X/Y offsets). The earlier house-group split only painted
outlines / icicles — `Windows` is outline submodels, not the matrix panels —
and Per Model Per Preview made each prop implode into itself instead of
toward Christ.

Christ blinks + parent Off masks stay on the four sung "name" bass pairs.

Close the sequence, run cleanup_pc1_convergence.py (clears the old house-group
meteors), reopen, then:

    XLIGHTS_API_PORT=49914 python3 \
      "Christmas/Sequences/Holy Forever 2026/Tools/pc1_house_name_chase.py"

Then re-apply star-only descents: `Tools/pc1_star_descent.py`.
"""
from pathlib import Path
import sys


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[3]
sys.path.insert(0, str(REPO_ROOT / "Tools"))

import xlights_api as x


OUT = SCRIPT_DIR.parent / "Holy Forever 2026.xsq"
STAR_TARGET = "Tree Topper"
CHRIST_TARGET = "GE Merry Christmas/Christ"
SIGN_TARGET = "GE Merry Christmas"
MEGA_TREE = "Mega Tree"
SCENE_TARGET = "Whole Scene w Matrixes"
OLD_SCENE_TARGET = "Whole Scene"

PC1_START = 40950
PC1_END = 67570
OUTER_TRAVEL_MS = 1375
SCENE_LAYER = 0
OLD_SCENE_LAYER = 1

NAME_WORDS = (
    (42250, 43175),
    (45600, 46625),
    (48950, 50250),
    (62175, 63400),
)

# Leftover targets from the house-group experiment — must be empty in PC1.
LEGACY_HOUSE_TARGETS = (
    "Colum Shrubs",
    "House Outline",
    "Roof",
    "Verts",
    "Windows",
    "Colums",
    "Icicles GRP",
)

# Whole Scene preview bounds are x=-811..470 and y=203..821. The Christ
# submodel's center is approximately (-279, 491), which maps to x=41.5% and
# y=46.6%. Meteors offsets are twice the delta from buffer center.
CHRIST_X_OFFSET = -17
CHRIST_Y_OFFSET = -7

SCENE_METEORS_SETTINGS = (
    "B_CHOICE_BufferStyle=Per Preview,"
    "B_SLIDER_Blur=2,"
    "E_CHECKBOX_FadeWithDistance=0,"
    "E_CHECKBOX_Meteors_UseMusic=0,"
    "E_CHOICE_Meteors_Effect=Implode,"
    "E_CHOICE_Meteors_Type=Palette,"
    "E_SLIDER_Meteors_Count=81,"
    "E_SLIDER_Meteors_Length=52,"
    "E_SLIDER_Meteors_Speed=50,"
    "E_SLIDER_Meteors_Swirl_Intensity=0,"
    "E_SLIDER_Meteors_WamupFrames=36,"
    f"E_TEXTCTRL_Meteors_XOffset={CHRIST_X_OFFSET},"
    f"E_TEXTCTRL_Meteors_YOffset={CHRIST_Y_OFFSET},"
    "T_CHOICE_LayerMethod=Normal,"
    "T_TEXTCTRL_Fadein=.08,"
    "T_TEXTCTRL_Fadeout=.35"
)
SCENE_METEORS_PALETTE = (
    "C_BUTTON_Palette1=#8A4512,"
    "C_BUTTON_Palette2=#D88924,"
    "C_BUTTON_Palette3=#FFC857,"
    "C_CHECKBOX_Palette1=1,"
    "C_CHECKBOX_Palette2=1,"
    "C_CHECKBOX_Palette3=1,"
    "C_SLIDER_Brightness=80"
)


def effect_rows(model, layer):
    ids = x.xl("getEffectIDs", model=model)["effects"]
    if layer >= len(ids):
        return []
    rows = []
    for effect_id in ids[layer]:
        effect = x.xl(
            "getEffectSettings", model=model, layer=layer, id=effect_id
        )
        rows.append(
            {
                "id": effect_id,
                "layer": layer,
                "name": effect.get("name", ""),
                "start": int(effect["startTime"]),
                "end": int(effect["endTime"]),
                "settings": effect.get("settings", {}),
                "palette": effect.get("palette", {}),
            }
        )
    return rows


def star_pulses():
    ids = x.xl("getEffectIDs", model=STAR_TARGET)["effects"]
    rows = []
    for layer, layer_ids in enumerate(ids):
        for effect_id in layer_ids:
            effect = x.xl(
                "getEffectSettings",
                model=STAR_TARGET,
                layer=layer,
                id=effect_id,
            )
            start = int(effect["startTime"])
            if (
                effect.get("name") == "Shockwave"
                and PC1_START < start < PC1_END
            ):
                rows.append(
                    {
                        "layer": layer,
                        "name": "Shockwave",
                        "start": start,
                        "end": int(effect["endTime"]),
                        "settings": effect.get("settings", {}),
                        "palette": effect.get("palette", {}),
                    }
                )
    rows.sort(key=lambda row: (row["start"], row["layer"]))
    if len(rows) != 16:
        raise RuntimeError(f"Expected 16 PC1 Tree Topper pulses, found: {rows}")
    return rows


def pulse_clusters(pulses):
    clusters = []
    i = 0
    while i < len(pulses):
        lead = pulses[i]
        cluster_end = lead["end"]
        members = [lead]
        i += 1
        while i < len(pulses) and pulses[i]["start"] <= cluster_end:
            members.append(pulses[i])
            cluster_end = max(cluster_end, pulses[i]["end"])
            i += 1
        if len(members) != 2:
            raise RuntimeError(f"Expected a star double-hit, found: {members}")
        clusters.append(
            {
                "start": lead["start"] - OUTER_TRAVEL_MS,
                "first_star": lead["start"],
                "end": cluster_end,
            }
        )
    if len(clusters) != 8:
        raise RuntimeError(f"Expected eight star pairs, found: {clusters}")
    return name_word_clusters(clusters)


def name_word_clusters(clusters):
    kept = []
    for cluster in clusters:
        first_star = cluster["first_star"]
        if any(
            word_start <= first_star < word_end
            for word_start, word_end in NAME_WORDS
        ):
            kept.append(cluster)
    if len(kept) != 4:
        raise RuntimeError(
            f"Expected four 'name' bass pairs, found: {kept}"
        )
    return kept


def map_string(values):
    return ",".join(f"{key}={value}" for key, value in values.items())


def christ_on_settings(pulse):
    settings = {
        "E_TEXTCTRL_Eff_On_End": "100",
        "E_TEXTCTRL_Eff_On_Start": "100",
    }
    settings.update(
        {
            key: value
            for key, value in pulse["settings"].items()
            if key.startswith("T_")
        }
    )
    return settings


def prior_christ_effects():
    prior = []
    ids = x.xl("getEffectIDs", model=CHRIST_TARGET)["effects"]
    for layer in range(len(ids)):
        for row in effect_rows(CHRIST_TARGET, layer):
            if row["name"] == "Off":
                continue
            if row["end"] <= PC1_START or row["start"] >= PC1_END:
                continue
            if layer == 0 and row["name"] != "On":
                raise RuntimeError(f"Unexpected Christ L0 effect: {row}")
            if layer > 0 and row["name"] not in {"Shockwave", "On"}:
                raise RuntimeError(f"Unexpected Christ pulse effect: {row}")
            prior.append(row)
    return prior


def prior_sign_masks():
    prior = []
    for row in effect_rows(SIGN_TARGET, 0):
        if (
            row["name"] == "Off"
            and row["end"] > PC1_START
            and row["start"] < PC1_END
        ):
            prior.append(row)
        elif (
            row["name"] != "Off"
            and row["end"] > PC1_START
            and row["start"] < PC1_END
        ):
            raise RuntimeError(f"Unexpected Merry Christmas L0 effect: {row}")
    return prior


def prior_scene_meteors():
    prior = []
    for model, layer in (
        (OLD_SCENE_TARGET, OLD_SCENE_LAYER),
        (SCENE_TARGET, SCENE_LAYER),
    ):
        for row in effect_rows(model, layer):
            if row["name"] == "Off":
                continue
            if row["end"] <= PC1_START or row["start"] >= PC1_END:
                continue
            if row["name"] != "Meteors":
                raise RuntimeError(
                    f"Unexpected {model} L{layer} effect: {row}"
                )
            prior.append((model, row))
    return prior


def prior_legacy_house_meteors():
    prior = {}
    for target in LEGACY_HOUSE_TARGETS:
        rows = [
            row
            for row in effect_rows(target, 0)
            if row["name"] == "Meteors"
            and row["end"] > PC1_START
            and row["start"] < PC1_END
        ]
        if rows:
            prior[target] = rows
    return prior


def prior_tree_ascent_meteors():
    """Legacy Up/Implode on Mega Tree L1 — ignore star-only Down descents."""
    prior = []
    for row in effect_rows(MEGA_TREE, 1):
        if row["name"] == "Off":
            continue
        if row["end"] <= PC1_START or row["start"] >= PC1_END:
            continue
        if row["name"] != "Meteors":
            raise RuntimeError(f"Unexpected Mega Tree L1 effect: {row}")
        direction = row["settings"].get("E_CHOICE_Meteors_Effect", "")
        if direction == "Down":
            continue
        prior.append(row)
    return prior


def signature(row):
    return (
        row["layer"],
        row["name"],
        row["start"],
        row["end"],
        tuple(sorted(row["settings"].items())),
        tuple(sorted(row["palette"].items())),
    )


def expected_christ(pulses):
    return [
        {
            **pulse,
            "name": "On",
            "settings": christ_on_settings(pulse),
        }
        for pulse in pulses
        if any(
            word_start <= pulse["start"] < word_end
            for word_start, word_end in NAME_WORDS
        )
    ]


def wanted_windows(clusters):
    return {(cluster["start"], cluster["end"]) for cluster in clusters}


def scene_ok(scene_prior, clusters):
    new_scene = [row for model, row in scene_prior if model == SCENE_TARGET]
    old_scene = [row for model, row in scene_prior if model == OLD_SCENE_TARGET]
    wanted = wanted_windows(clusters)
    if old_scene:
        return False
    if len(new_scene) != len(clusters):
        return False
    if {(row["start"], row["end"]) for row in new_scene} != wanted:
        return False
    for row in new_scene:
        settings = row["settings"]
        if settings.get("E_CHOICE_Meteors_Effect") != "Implode":
            return False
        if settings.get("B_CHOICE_BufferStyle") != "Per Preview":
            return False
        if settings.get("E_TEXTCTRL_Meteors_XOffset") != str(CHRIST_X_OFFSET):
            return False
        if settings.get("E_TEXTCTRL_Meteors_YOffset") != str(CHRIST_Y_OFFSET):
            return False
    return True


def main():
    dry_run = "--dry-run" in sys.argv

    info = x.xl("getOpenSequence")
    if Path(info.get("fullseq", "")).resolve() != OUT.resolve():
        raise RuntimeError(f"Wrong sequence open: {info}")
    if int(info.get("len", 0)) != 308314:
        raise RuntimeError(f"Unexpected sequence length: {info}")

    pulses = star_pulses()
    clusters = pulse_clusters(pulses)
    christ_prior = prior_christ_effects()
    sign_prior = prior_sign_masks()
    scene_prior = prior_scene_meteors()
    legacy_house = prior_legacy_house_meteors()
    tree_ascent = prior_tree_ascent_meteors()
    expected = expected_christ(pulses)
    windows = wanted_windows(clusters)

    print(
        f"{SCENE_TARGET} L{SCENE_LAYER}: Implode toward Christ "
        f"offset ({CHRIST_X_OFFSET}, {CHRIST_Y_OFFSET})"
    )
    for index, cluster in enumerate(clusters, start=1):
        print(
            f"  window #{index}: {cluster['start']}-{cluster['end']} "
            f"(first star {cluster['first_star']})"
        )

    christ_ok = [signature(row) for row in sorted(
        christ_prior, key=lambda row: (row["start"], row["layer"])
    )] == [signature(row) for row in expected]
    sign_ok = (
        len(sign_prior) == len(clusters)
        and all(
            row["start"] == cluster["start"] and row["end"] == cluster["end"]
            for row, cluster in zip(
                sorted(sign_prior, key=lambda row: row["start"]),
                sorted(clusters, key=lambda row: row["start"]),
            )
        )
    )
    no_legacy = not legacy_house and not tree_ascent
    scene_built = scene_ok(scene_prior, clusters)

    if christ_ok and sign_ok and no_legacy and scene_built:
        print(
            "already built: Whole Scene w Matrixes → Christ + sign; "
            "no legacy house-group meteors"
        )
        return

    if christ_prior or sign_prior or scene_prior or legacy_house or tree_ascent:
        raise RuntimeError(
            "Conflicting or legacy PC1 meteor effects found. Close xLights, run "
            "cleanup_pc1_convergence.py, reopen, then rebuild with this script "
            "(then pc1_star_descent.py)."
        )

    if dry_run:
        print("dry-run: no writes")
        return

    for cluster in clusters:
        x.add_effect(
            SIGN_TARGET,
            0,
            "Off",
            "",
            "",
            cluster["start"],
            cluster["end"],
        )

    for pulse in expected:
        x.add_effect(
            CHRIST_TARGET,
            pulse["layer"],
            "On",
            map_string(christ_on_settings(pulse)),
            map_string(pulse["palette"]),
            pulse["start"],
            pulse["end"],
        )

    for cluster in clusters:
        x.add_effect(
            SCENE_TARGET,
            SCENE_LAYER,
            "Meteors",
            SCENE_METEORS_SETTINGS,
            SCENE_METEORS_PALETTE,
            cluster["start"],
            cluster["end"],
        )

    actual_christ = []
    ids = x.xl("getEffectIDs", model=CHRIST_TARGET)["effects"]
    for layer in range(len(ids)):
        actual_christ.extend(
            row
            for row in effect_rows(CHRIST_TARGET, layer)
            if row["name"] == "On"
            and PC1_START < row["start"] < PC1_END
        )
    actual_christ.sort(key=lambda row: (row["start"], row["layer"]))
    if [signature(row) for row in actual_christ] != [
        signature(row) for row in expected
    ]:
        raise RuntimeError("Christ pulses do not exactly match Tree Topper")

    if not scene_ok(prior_scene_meteors(), clusters):
        raise RuntimeError("Whole Scene w Matrixes windows mismatch after add")

    if prior_legacy_house_meteors() or prior_tree_ascent_meteors():
        raise RuntimeError("Legacy house-group or Mega Tree ascent still present")

    live_sign_masks = [
        row
        for row in effect_rows(SIGN_TARGET, 0)
        if row["name"] == "Off"
        and any(
            row["start"] == cluster["start"] and row["end"] == cluster["end"]
            for cluster in clusters
        )
    ]
    if len(live_sign_masks) != len(clusters):
        raise RuntimeError(
            f"Expected {len(clusters)} sign masks, found: {live_sign_masks}"
        )

    x.save(str(OUT))
    print(f"saved {OUT}")
    print("next: run pc1_star_descent.py to restore star-only Mega Tree Downs")


if __name__ == "__main__":
    main()
