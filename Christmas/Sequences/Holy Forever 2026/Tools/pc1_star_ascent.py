"""Build meteor-only Mega Tree chases for PC1 bass pairs on sung "name" only.

Each of the four windows uses only amber/gold `Meteors Up` across the whole
tree when the lead vocal says "name" — not during thrones/powers/positions.

Run with xLights open on this worktree's Holy Forever sequence:

    XLIGHTS_API_PORT=49914 python3 \
      "Christmas/Sequences/Holy Forever 2026/Tools/pc1_star_ascent.py"
"""
from pathlib import Path
import sys


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[3]
sys.path.insert(0, str(REPO_ROOT / "Tools"))

import xlights_api as x


OUT = SCRIPT_DIR.parent / "Holy Forever 2026.xsq"
TARGET = "Mega Tree"
STAR_TARGET = "Tree Topper"

PC1_START = 40950
L0_CLEANUP_START = 41850  # preserves the intro cross ending here
OUTER_TRAVEL_MS = 1375
PC1_END = 67570

# Lyrics Lead word-layer "name" marks in PC1 — tree meteors only on these.
NAME_WORDS = (
    (42250, 43175),
    (45600, 46625),
    (48950, 50250),
    (62175, 63400),
)

METEORS_SETTINGS = (
    "B_CHOICE_BufferStyle=Default,"
    "B_SLIDER_Blur=2,"
    "E_CHECKBOX_Meteors_UseMusic=0,"
    "E_CHOICE_Meteors_Effect=Up,"
    "E_CHOICE_Meteors_Type=Palette,"
    "E_SLIDER_Meteors_Count=9,"
    "E_SLIDER_Meteors_Length=20,"
    "E_SLIDER_Meteors_Speed=18,"
    "E_SLIDER_Meteors_Swirl_Intensity=0,"
    "T_CHOICE_LayerMethod=Normal,"
    "T_TEXTCTRL_Fadein=.08,"
    "T_TEXTCTRL_Fadeout=.35"
)
METEORS_PALETTE = (
    "C_BUTTON_Palette1=#8A4512,"
    "C_BUTTON_Palette2=#D88924,"
    "C_BUTTON_Palette3=#FFC857,"
    "C_CHECKBOX_Palette2=1,"
    "C_CHECKBOX_Palette1=1,"
    "C_CHECKBOX_Palette3=1,"
    "C_SLIDER_Brightness=68"
)


def effect_rows(model, layer):
    """Return current effect rows for one model layer."""
    ids = x.xl("getEffectIDs", model=model)["effects"]
    if layer >= len(ids):
        return []
    rows = []
    for effect_id in ids[layer]:
        settings = x.xl(
            "getEffectSettings", model=model, layer=layer, id=effect_id
        )
        rows.append(
            {
                "id": effect_id,
                "name": settings.get("name", ""),
                "start": int(settings["startTime"]),
                "end": int(settings["endTime"]),
            }
        )
    return rows


def star_clusters():
    """Find every overlapping lead/follow Tree Topper pair in PC1."""
    rows = []
    ids = x.xl("getEffectIDs", model=STAR_TARGET)["effects"]
    for layer, layer_ids in enumerate(ids):
        for effect_id in layer_ids:
            settings = x.xl(
                "getEffectSettings",
                model=STAR_TARGET,
                layer=layer,
                id=effect_id,
            )
            start = int(settings["startTime"])
            end = int(settings["endTime"])
            if (
                settings.get("name") != "Off"
                and PC1_START < start < PC1_END
            ):
                rows.append((start, end))

    if not rows:
        raise RuntimeError("No live Tree Topper effect found in PC1")

    rows.sort()
    clusters = []
    i = 0
    while i < len(rows):
        first_start, first_end = rows[i]
        cluster_end = first_end
        members = [(first_start, first_end)]
        i += 1
        while i < len(rows) and rows[i][0] <= cluster_end:
            members.append(rows[i])
            cluster_end = max(cluster_end, rows[i][1])
            i += 1
        if len(members) < 2:
            raise RuntimeError(f"Unpaired Tree Topper effect: {members}")
        clusters.append(
            {
                "first_start": first_start,
                "first_end": first_end,
                "follow_start": members[1][0],
                "end": cluster_end,
            }
        )
    return name_word_clusters(clusters)


def name_word_clusters(clusters):
    """Keep only bass pairs whose lead pulse lands on a sung 'name'."""
    kept = []
    for cluster in clusters:
        first_star = cluster["first_start"]
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


def prior_build_rows(plan):
    """Return only effects in the layers/windows this tool owns."""
    expected_names = {
        0: {"Morph"},
        1: {"Morph", "Meteors"},
        2: {"Meteors"},
        3: {"Shockwave"},
        4: {"Shockwave"},
    }
    ranges = {}
    for layer, _, _, _, start, end, _ in plan:
        ranges.setdefault(layer, []).append((start, end))
    # Retire the removed white/ivory L0 cores from earlier iterations.
    ranges[0] = [(L0_CLEANUP_START, PC1_END)]
    # Retire the removed reveal partners and added tree ripples.
    ranges[2] = [(PC1_START, PC1_END)]
    ranges[3] = [(PC1_START, PC1_END)]
    ranges[4] = [(PC1_START, PC1_END)]

    prior = []
    for layer, allowed in expected_names.items():
        for row in effect_rows(TARGET, layer):
            if row["name"] == "Off":
                continue
            owned = any(
                row["end"] > start and row["start"] < end
                for start, end in ranges.get(layer, [])
            )
            if not owned:
                continue
            if row["name"] not in allowed:
                raise RuntimeError(
                    f"Unexpected effect in owned window: L{layer} {row}"
                )
            prior.append((layer, row))
    return prior


def main():
    dry_run = "--dry-run" in sys.argv

    info = x.xl("getOpenSequence")
    if Path(info.get("fullseq", "")).resolve() != OUT.resolve():
        raise RuntimeError(f"Wrong sequence open: {info}")
    if int(info.get("len", 0)) != 308314:
        raise RuntimeError(f"Unexpected sequence length: {info}")

    clusters = star_clusters()
    if len(clusters) != 8:
        raise RuntimeError(f"Expected eight PC1 star pairs, found: {clusters}")
    clusters = name_word_clusters(clusters)

    plan = []
    previous_end = None

    for index, cluster in enumerate(clusters, start=1):
        star_start = cluster["first_start"]
        follow_start = cluster["follow_start"]
        star_end = cluster["end"]
        outer_start = star_start - OUTER_TRAVEL_MS

        if not outer_start < star_start < follow_start < star_end:
            raise RuntimeError(
                f"Invalid timing for bass pair #{index}: "
                f"{outer_start}, {star_start}, {follow_start}, {star_end}"
            )
        if previous_end is not None and outer_start < previous_end:
            raise RuntimeError(
                f"Bass-pair ascent overlap: prior end {previous_end}, "
                f"next start {outer_start}"
            )
        previous_end = star_end

        plan.append(
            (
                1,
                "Meteors",
                METEORS_SETTINGS,
                METEORS_PALETTE,
                outer_start,
                star_end,
                f"bass-pair whole-tree meteor chase #{index}",
            )
        )
        print(
            f"Bass pair #{index}: Meteors {outer_start}-{star_end}, "
            f"first star {star_start}"
        )

    for layer, effect, _, _, start, end, role in plan:
        print(f"  L{layer} {effect} {start}-{end}: {role}")

    prior = prior_build_rows(plan)
    if prior:
        expected = {
            (layer, effect, start, end)
            for layer, effect, _, _, start, end, _ in plan
        }
        actual = {
            (layer, row["name"], row["start"], row["end"])
            for layer, row in prior
        }
        if actual == expected and len(prior) == len(plan):
            print("already built: all four 'name' Mega Tree meteor windows match")
            return
        raise RuntimeError(
            "Conflicting PC1 Mega Tree effects found. Run "
            "cleanup_pc1_convergence.py with xLights closed, reopen, "
            "then rebuild; refusing to leave Off stubs."
        )

    if dry_run:
        print("dry-run: no writes")
        return

    for layer, effect, settings, palette, start, end, _ in plan:
        x.add_effect(TARGET, layer, effect, settings, palette, start, end)

    for layer, effect, _, _, start, end, role in plan:
        live = [
            row
            for row in effect_rows(TARGET, layer)
            if row["name"] == effect
            and row["start"] == start
            and row["end"] == end
        ]
        if len(live) != 1:
            raise RuntimeError(
                f"Expected one live {role} on L{layer}, found: {live}"
            )

    x.save(str(OUT))
    print(f"saved {OUT}")


if __name__ == "__main__":
    main()
