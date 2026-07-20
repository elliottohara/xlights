"""Blink Christ with the star and implode whole-scene meteors into it.

PC1 behavior:

* `GE Merry Christmas/Christ` receives 16 full-submodel On pulses using the
  Tree Topper's exact bass-drum timing, palettes, and transition fades,
  replacing the four lyric-timed "Your name" glows.
* `Whole Scene w Matrixes` receives eight amber/gold Meteors Implode windows
  matching the Mega Tree's bass-pair windows. The radial center is offset to
  the Christ submodel's preview position.

Run with xLights open on this worktree's Holy Forever sequence:

    XLIGHTS_API_PORT=49914 python3 \
      "Christmas/Sequences/Holy Forever 2026/Tools/pc1_christ_convergence.py"
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
SCENE_TARGET = "Whole Scene w Matrixes"
OLD_SCENE_TARGET = "Whole Scene"

PC1_START = 40950
PC1_END = 67570
OUTER_TRAVEL_MS = 1375

# Whole Scene preview bounds are x=-811..470 and y=203..821. The Christ
# submodel's center is approximately (-279, 491), which maps to x=41.5% and
# y=46.6%. Meteors offsets are twice the delta from buffer center.
CHRIST_X_OFFSET = -17
CHRIST_Y_OFFSET = -7
SCENE_LAYER = 0
OLD_SCENE_LAYER = 1

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
    return clusters


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


def prior_scene_effects():
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


def signature(row):
    return (
        row["layer"],
        row["name"],
        row["start"],
        row["end"],
        tuple(sorted(row["settings"].items())),
        tuple(sorted(row["palette"].items())),
    )


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
    scene_prior = prior_scene_effects()
    sign_prior = prior_sign_masks()

    print(
        f"Christ: replace {len(christ_prior)} live effect(s) with "
        f"{len(pulses)} full-text star-timed On pulses"
    )
    for index, cluster in enumerate(clusters, start=1):
        print(
            f"  scene #{index}: Implode {cluster['start']}-{cluster['end']} "
            f"toward offset ({CHRIST_X_OFFSET}, {CHRIST_Y_OFFSET}); "
            f"first star {cluster['first_star']}"
        )

    build_start = min(cluster["start"] for cluster in clusters)
    build_end = max(cluster["end"] for cluster in clusters)
    expected_christ = [
        {
            **pulse,
            "name": "On",
            "settings": christ_on_settings(pulse),
        }
        for pulse in pulses
    ]
    christ_ok = [signature(row) for row in sorted(
        christ_prior, key=lambda row: (row["start"], row["layer"])
    )] == [signature(row) for row in expected_christ]
    new_scene = [
        row for model, row in scene_prior if model == SCENE_TARGET
    ]
    old_scene = [
        row for model, row in scene_prior if model == OLD_SCENE_TARGET
    ]
    wanted_scene = {
        (cluster["start"], cluster["end"]) for cluster in clusters
    }
    scene_ok = (
        not old_scene
        and len(new_scene) == len(clusters)
        and {(row["start"], row["end"]) for row in new_scene} == wanted_scene
    )
    sign_ok = (
        len(sign_prior) == 1
        and sign_prior[0]["start"] == build_start
        and sign_prior[0]["end"] == build_end
    )

    if christ_prior or scene_prior or sign_prior:
        if christ_ok and scene_ok and sign_ok:
            print("already built: Christ, scene convergence, and sign mask match")
            return
        raise RuntimeError(
            "Conflicting PC1 Christ/scene effects found. Run "
            "cleanup_pc1_convergence.py with xLights closed, reopen, "
            "then rebuild; refusing to leave Off stubs."
        )

    if dry_run:
        print("dry-run: no writes")
        return

    # The expanded scene group contains the whole sign. An individual parent
    # Off masks that lower group effect; the Christ submodel pulses below are
    # then rendered back on over the masked parent.
    x.add_effect(
        SIGN_TARGET,
        0,
        "Off",
        "",
        "",
        build_start,
        build_end,
    )

    for pulse in pulses:
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
        signature(row) for row in expected_christ
    ]:
        raise RuntimeError("Christ pulses do not exactly match Tree Topper")

    actual_scene = [
        row
        for row in effect_rows(SCENE_TARGET, SCENE_LAYER)
        if row["name"] == "Meteors"
        and PC1_START <= row["start"] < PC1_END
    ]
    got_scene = {(row["start"], row["end"]) for row in actual_scene}
    if got_scene != wanted_scene:
        raise RuntimeError(
            f"Whole Scene windows differ: got={got_scene}, wanted={wanted_scene}"
        )

    live_sign_masks = [
        row
        for row in effect_rows(SIGN_TARGET, 0)
        if row["name"] == "Off"
        and row["start"] == build_start
        and row["end"] == build_end
    ]
    if len(live_sign_masks) != 1:
        raise RuntimeError(
            f"Expected one full-sign mask, found: {live_sign_masks}"
        )

    x.save(str(OUT))
    print(f"saved {OUT}")


if __name__ == "__main__":
    main()
