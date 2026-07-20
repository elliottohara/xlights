"""PC1 Mega Tree descent on star pairs that do NOT fire Christ.

Mirror of the old `Meteors Up` ascent (same travel, palette, density), but
`Meteors Down` starting at the lead Tree Topper hit — after the star fires —
for the four bass pairs that land on thrones/powers/positions / "stands above"
tails (not sung "name").

The four "name" pairs keep Christ + house implode chase; this owns Mega Tree
L1 only inside the four non-name windows.

    XLIGHTS_API_PORT=49914 python3 \
      "Christmas/Sequences/Holy Forever 2026/Tools/pc1_star_descent.py"
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
PC1_END = 67570
OUTER_TRAVEL_MS = 1375
LAYER = 1

# Lyrics Lead word-layer "name" marks — descent skips these (Christ owns them).
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
    "E_CHOICE_Meteors_Effect=Down,"
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
    "C_CHECKBOX_Palette1=1,"
    "C_CHECKBOX_Palette2=1,"
    "C_CHECKBOX_Palette3=1,"
    "C_SLIDER_Brightness=68"
)


def effect_rows(model, layer):
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
                "settings": settings.get("settings", {}),
            }
        )
    return rows


def is_name_hit(first_star):
    return any(
        word_start <= first_star < word_end
        for word_start, word_end in NAME_WORDS
    )


def star_clusters():
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
                settings.get("name") == "Shockwave"
                and PC1_START < start < PC1_END
            ):
                rows.append((start, end))
    if not rows:
        raise RuntimeError("No live Tree Topper Shockwave found in PC1")

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
        if len(members) != 2:
            raise RuntimeError(f"Expected a star double-hit, found: {members}")
        clusters.append(
            {
                "first_star": first_start,
                "end": cluster_end,
            }
        )
    if len(clusters) != 8:
        raise RuntimeError(f"Expected eight PC1 star pairs, found: {clusters}")
    return clusters


def non_name_clusters(clusters):
    kept = [
        cluster
        for cluster in clusters
        if not is_name_hit(cluster["first_star"])
    ]
    if len(kept) != 4:
        raise RuntimeError(
            f"Expected four non-'name' star pairs, found: {kept}"
        )
    return kept


def plan_windows(clusters):
    plan = []
    previous_end = None
    for index, cluster in enumerate(clusters, start=1):
        start = cluster["first_star"]
        end = start + OUTER_TRAVEL_MS
        if end > PC1_END:
            raise RuntimeError(
                f"Descent #{index} overruns PC1: {start}-{end} > {PC1_END}"
            )
        if previous_end is not None and start < previous_end:
            raise RuntimeError(
                f"Descent overlap: prior end {previous_end}, next {start}"
            )
        previous_end = end
        plan.append((start, end, cluster["first_star"], cluster["end"]))
    return plan


def owned_prior(plan):
    wanted = {(start, end) for start, end, _, _ in plan}
    prior = []
    for row in effect_rows(TARGET, LAYER):
        if row["name"] == "Off":
            continue
        if row["end"] <= PC1_START or row["start"] >= PC1_END:
            continue
        if row["name"] != "Meteors":
            raise RuntimeError(
                f"Unexpected Mega Tree L{LAYER} effect in PC1: {row}"
            )
        direction = row["settings"].get("E_CHOICE_Meteors_Effect", "")
        if (row["start"], row["end"]) in wanted:
            if direction != "Down":
                raise RuntimeError(
                    f"Expected Meteors Down in descent window: {row}"
                )
            prior.append(row)
        elif direction == "Down":
            raise RuntimeError(
                f"Unexpected Meteors Down outside descent plan: {row}"
            )
        # Up / Implode leftovers from older builds — refuse rather than Off-park.
        else:
            raise RuntimeError(
                f"Conflicting Mega Tree L{LAYER} Meteors in PC1: {row}. "
                "Close xLights, run cleanup_pc1_convergence.py, reopen, "
                "then rebuild house chase + this descent."
            )
    return prior


def main():
    dry_run = "--dry-run" in sys.argv

    info = x.xl("getOpenSequence")
    if Path(info.get("fullseq", "")).resolve() != OUT.resolve():
        raise RuntimeError(f"Wrong sequence open: {info}")
    if int(info.get("len", 0)) != 308314:
        raise RuntimeError(f"Unexpected sequence length: {info}")

    clusters = non_name_clusters(star_clusters())
    plan = plan_windows(clusters)

    print(f"Mega Tree L{LAYER} Meteors Down after star-only pairs:")
    for index, (start, end, first_star, pair_end) in enumerate(plan, start=1):
        print(
            f"  #{index}: {start}-{end} "
            f"(star pair {first_star}…{pair_end})"
        )

    prior = owned_prior(plan)
    wanted = {(start, end) for start, end, _, _ in plan}
    actual = {(row["start"], row["end"]) for row in prior}
    if actual == wanted and len(prior) == len(plan):
        print("already built: four star-only Mega Tree descents match")
        return

    if prior:
        raise RuntimeError(
            f"Partial / mismatched descent build on Mega Tree L{LAYER}: {prior}"
        )

    if dry_run:
        print("dry-run: no writes")
        return

    for start, end, _, _ in plan:
        x.add_effect(
            TARGET,
            LAYER,
            "Meteors",
            METEORS_SETTINGS,
            METEORS_PALETTE,
            start,
            end,
        )

    live = owned_prior(plan)
    if {(row["start"], row["end"]) for row in live} != wanted:
        raise RuntimeError(f"Post-add descent mismatch: {live}")

    x.save(str(OUT))
    print(f"saved {OUT}")


if __name__ == "__main__":
    main()
