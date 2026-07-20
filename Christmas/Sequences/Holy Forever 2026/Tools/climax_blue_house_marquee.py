"""Add the subtle blue House Outline marquee for the full final chorus.

The effect starts exactly at the live `Final Chorus` song-section label and
ends when the Climax mood ends. A narrow sapphire marquee moves slowly around
the full house outline while a custom brightness curve breathes gently from
38 to 46 on the live `Beat Count` bar downbeats.

The first build started at the later `Final Chorus - Holy Forever` label. This
tool recognizes that exact prior effect, saves a backup, removes only that one
effect from the closed `.xsq`, reopens it, and rebuilds through addEffect. Any
other unexpected House Outline L1 contents cause a refusal.

Run:
  XLIGHTS_API_PORT=49914 python3 \
    "Christmas/Sequences/Holy Forever 2026/Tools/climax_blue_house_marquee.py" \
    [--dry-run]
"""
import re
import shutil
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "Tools"))
import xlights_api as x


SEQUENCE = Path(__file__).resolve().parents[1] / "Holy Forever 2026.xsq"
BACKUP = SEQUENCE.with_name(
    SEQUENCE.name + ".bak-before-final-chorus-marquee"
)
ELEMENT = "House Outline"
LAYER = 1

# Live timing anchors: Song Sections' Final Chorus label, then Mood Afterglow.
START = 234225
END = 287275
PREVIOUS_START = 273650
BAR_DOWNS = [
    233925, 237275, 240600, 243925, 247275, 250600, 253925, 257275,
    260600, 263925, 267275, 270600, 273925, 277275, 280600, 283925,
    287275,
]

LOW = 38
HIGH = 46

SETTINGS = (
    "B_CHOICE_BufferStyle=Single Line,"
    "E_CHECKBOX_Marquee_PixelOffsets=0,"
    "E_CHECKBOX_Marquee_Reverse=0,"
    "E_CHECKBOX_Marquee_WrapX=0,"
    "E_NOTEBOOK_Marquee=Settings,"
    "E_SLIDER_MarqueeXC=0,"
    "E_SLIDER_MarqueeYC=0,"
    "E_SLIDER_Marquee_Band_Size=4,"
    "E_SLIDER_Marquee_ScaleX=100,"
    "E_SLIDER_Marquee_ScaleY=100,"
    "E_SLIDER_Marquee_Skip_Size=9,"
    "E_SLIDER_Marquee_Speed=2,"
    "E_SLIDER_Marquee_Stagger=0,"
    "E_SLIDER_Marquee_Start=0,"
    "E_SLIDER_Marquee_Thickness=2,"
    "T_TEXTCTRL_Fadein=.60,"
    "T_TEXTCTRL_Fadeout=.75"
)


def brightness_curve() -> str:
    """Return a subtle low-mid-low breath for each bar."""
    # Final Chorus starts 300 ms after the 233925 bar downbeat, so enter near
    # the bar's bright point, dip at its midpoint, then peak on each downbeat.
    points = [(START, HIGH)]
    for downbeat, next_downbeat in zip(BAR_DOWNS, BAR_DOWNS[1:]):
        midpoint = (downbeat + next_downbeat) // 2
        if START < midpoint < END:
            points.append((midpoint, LOW))
        if START < next_downbeat <= END:
            points.append((next_downbeat, HIGH))

    span = float(END - START)
    values = ";".join(
        f"{(ms - START) / span:.4f}:{brightness / 400.0:.4f}"
        for ms, brightness in points
    )
    return (
        "Active=TRUE|Id=ID_VALUECURVE_Brightness|Type=Custom|"
        f"Min=0.00|Max=400.00|RV=TRUE|Values={values}|"
    )


def layer_effects() -> list[dict]:
    layers = x.xl("getEffectIDs", model=ELEMENT)["effects"]
    if len(layers) <= LAYER:
        return []
    return [
        x.xl(
            "getEffectSettings",
            model=ELEMENT,
            layer=str(LAYER),
            id=str(effect_id),
        )
        for effect_id in layers[LAYER]
    ]


def is_expected(effect: dict) -> bool:
    return (
        effect.get("name") == "Marquee"
        and int(effect.get("startTime", -1)) == START
        and int(effect.get("endTime", -1)) == END
        and effect.get("palette", {}).get("C_BUTTON_Palette1") == "#2864FF"
        and bool(effect.get("palette", {}).get("C_VALUECURVE_Brightness"))
    )


def is_previous(effect: dict) -> bool:
    """True only for the first, too-late version this task is replacing."""
    return (
        effect.get("name") == "Marquee"
        and int(effect.get("startTime", -1)) == PREVIOUS_START
        and int(effect.get("endTime", -1)) == END
        and effect.get("palette", {}).get("C_BUTTON_Palette1") == "#2864FF"
    )


def without_previous_effect(lines: list[str]) -> list[str]:
    """Remove only the prior marquee line from House Outline L1."""
    element_re = re.compile(r'<Element type="model" name="([^"]+)"')
    effect_re = re.compile(
        rf'<Effect\b[^>]*name="Marquee"[^>]*'
        rf'startTime="{PREVIOUS_START}"[^>]*endTime="{END}"[^>]*/>'
    )
    output = []
    in_element_effects = False
    current_element = None
    layer = -1
    removed = 0

    for line in lines:
        stripped = line.strip()
        if stripped == "<ElementEffects>":
            in_element_effects = True
        elif stripped == "</ElementEffects>":
            in_element_effects = False
        elif in_element_effects:
            match = element_re.search(line)
            if match:
                current_element = match.group(1)
                layer = -1
            elif stripped == "</Element>":
                current_element = None
            elif current_element == ELEMENT and "<EffectLayer" in line:
                layer += 1
            elif (
                current_element == ELEMENT
                and layer == LAYER
                and effect_re.search(line)
            ):
                removed += 1
                continue
        output.append(line)

    if removed != 1:
        raise RuntimeError(
            f"expected exactly one prior {ELEMENT} L{LAYER} marquee; "
            f"found {removed}"
        )
    return output


def replace_previous() -> None:
    """Back up, directly delete the prior effect, and reopen the sequence."""
    x.save(str(SEQUENCE))
    lines = SEQUENCE.read_text(encoding="utf-8").splitlines(keepends=True)
    output = without_previous_effect(lines)

    if not BACKUP.exists():
        shutil.copy2(SEQUENCE, BACKUP)
        print(f"backup: {BACKUP}")
    else:
        print(f"backup already exists: {BACKUP}")

    x.xl("closeSequence", force="true", quiet="true")
    SEQUENCE.write_text("".join(output), encoding="utf-8")
    x.xl("openSequence", seq=str(SEQUENCE), timeout=120)
    assert not layer_effects(), f"{ELEMENT} L{LAYER} was not cleared"
    print(f"removed prior {PREVIOUS_START}-{END} marquee")


def main() -> None:
    dry_run = "--dry-run" in sys.argv
    info = x.xl("getOpenSequence")
    assert "Holy Forever 2026" in info.get("seq", ""), \
        f"wrong sequence open: {info}"

    print(
        f"plan: {ELEMENT} L{LAYER} Marquee {START}-{END}; "
        f"sapphire blue; bar breath {LOW}-{HIGH}"
    )
    print(f"bar downbeats: {[ms for ms in BAR_DOWNS if ms >= START]}")

    existing = layer_effects()
    if len(existing) == 1 and is_expected(existing[0]):
        print("done: exact marquee already present.")
        return
    if len(existing) == 1 and is_previous(existing[0]):
        if dry_run:
            print(
                f"dry run: would replace prior {PREVIOUS_START}-{END} marquee"
            )
            return
        replace_previous()
        existing = []
    if existing:
        summary = [
            (effect.get("name"), effect.get("startTime"), effect.get("endTime"))
            for effect in existing
        ]
        raise SystemExit(
            f"REFUSING TO WRITE: {ELEMENT} L{LAYER} is not empty: {summary}"
        )
    if dry_run:
        print("dry run: no changes made")
        return

    palette = (
        "C_BUTTON_Palette1=#2864FF,"
        "C_CHECKBOX_Palette1=1,"
        f"C_VALUECURVE_Brightness={brightness_curve()}"
    )
    x.add_effect(ELEMENT, LAYER, "Marquee", SETTINGS, palette, START, END)

    after = layer_effects()
    assert len(after) == 1 and is_expected(after[0]), \
        f"verification failed: {after}"
    x.save(str(SEQUENCE))
    print(f"saved: {SEQUENCE}")


if __name__ == "__main__":
    main()
