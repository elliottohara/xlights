"""Script-font "Holy" on Projector + Entry + Downstairs — brightness breathes.

Covers every chorus "… holy" that closes the triad:
  And the angels cry holy / All creation cries holy / You are lifted high holy
in C1, C2a, and C3 (9 windows).

Static centered Text (no movement). Brightness value curve rises and falls
with the sung melisma (soft → peak mid-hold → soft).

Targets (L0 each):
  - Projector
  - Matrix - Entry
  - Matrix - Downstairs Window

Run (Slot A default port 49913):
  python3 "Christmas/Sequences/Holy Forever 2026/Tools/angels_cry_holy_text.py"
  [--dry-run] [--clear-only]
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "Tools"))
import xlights_api as x

SEQUENCE = Path(__file__).resolve().parents[1] / "Holy Forever 2026.xsq"
BACKUP = SEQUENCE.with_name(SEQUENCE.name + ".bak-before-angels-cry-holy-text")
EMPTY_SOURCE = "House"

# Lyrics Lead word-layer "holy"/"Holy" closing angels / creation / lifted-high.
HOLY_WINDOWS = [
    # C1
    (70425, 72850),
    (77275, 79250),
    (83975, 86275),
    # C2a
    (130075, 132625),
    (138525, 139925),
    (144750, 146150),
    # C3
    (238150, 239550),
    (244375, 245775),
    (251150, 252550),
]

# Brightness curve over each effect (0–400 palette scale): soft → peak → soft.
# Normalized 0–1 on Min=0 Max=400.
BRIGHT_LO = 35
BRIGHT_HI = 100

TARGETS = {
    "Projector": {"font_size": 64},
    "Matrix - Entry": {"font_size": 20},
    "Matrix - Downstairs Window": {"font_size": 24},
}


def brightness_curve() -> str:
    """Rise through the first half of the holy, peak mid, fall out."""
    lo = BRIGHT_LO / 400.0
    hi = BRIGHT_HI / 400.0
    mid_lo = (BRIGHT_LO + (BRIGHT_HI - BRIGHT_LO) * 0.35) / 400.0
    values = (
        f"0.0000:{lo:.4f};"
        f"0.1800:{mid_lo:.4f};"
        f"0.4200:{hi:.4f};"
        f"0.5800:{hi:.4f};"
        f"0.8200:{mid_lo:.4f};"
        f"1.0000:{lo:.4f}"
    )
    return (
        "Active=TRUE|Id=ID_VALUECURVE_Brightness|Type=Custom|"
        f"Min=0.00|Max=400.00|RV=TRUE|Values={values}|"
    )


def settings_for(cfg: dict) -> str:
    font = f"'brush script mt' {cfg['font_size']} utf-8"
    return (
        "E_CHECKBOX_TextNoRepeat=0,"
        "E_CHECKBOX_TextToCenter=0,"
        "E_CHECKBOX_Text_Color_PerWord=0,"
        "E_CHECKBOX_Text_PixelOffsets=0,"
        "E_CHOICE_Text_Count=none,"
        "E_CHOICE_Text_Dir=none,"
        "E_CHOICE_Text_Effect=normal,"
        "E_CHOICE_Text_Font=Use OS Fonts,"
        "E_FILEPICKERCTRL_Text_File=,"
        f"E_FONTPICKER_Text_Font={font},"
        "E_SLIDER_Text_XEnd=0,"
        "E_SLIDER_Text_XStart=0,"
        "E_SLIDER_Text_YEnd=0,"
        "E_SLIDER_Text_YStart=0,"
        "E_TEXTCTRL_Text=Holy,"
        "E_TEXTCTRL_Text_Speed=10,"
        "T_TEXTCTRL_Fadein=.08,"
        "T_TEXTCTRL_Fadeout=.20"
    )


def palette_for() -> str:
    return (
        "C_BUTTON_Palette1=#FFFFFF,C_CHECKBOX_Palette1=1,"
        f"C_VALUECURVE_Brightness={brightness_curve()}"
    )


def read_l0(model: str) -> list[tuple[str, int, int]]:
    layers = x.xl("getEffectIDs", model=model)["effects"]
    if not layers or not layers[0]:
        return []
    out = []
    for eid in layers[0]:
        e = x.xl("getEffectSettings", model=model, layer="0", id=str(eid))
        out.append((e["name"], int(e["startTime"]), int(e["endTime"])))
    return sorted(out, key=lambda t: t[1])


def wipe_l0(model: str) -> None:
    src = x.xl("getEffectIDs", model=EMPTY_SOURCE)["effects"]
    assert len(src) == 1 and not src[0], f"{EMPTY_SOURCE} unusable as wipe source: {src}"
    x.xl("cloneModelEffects", target=model, source=EMPTY_SOURCE, eraseModel="true")


def owned_by_us(effects: list[tuple[str, int, int]]) -> bool:
    if not effects:
        return True
    return all(
        name == "Text" and 70000 <= s < 255000 and e - s <= 3000
        for name, s, e in effects
    )


def main() -> None:
    dry = "--dry-run" in sys.argv
    clear_only = "--clear-only" in sys.argv

    info = x.xl("getOpenSequence")
    assert "Holy Forever 2026" in info.get("seq", ""), f"wrong sequence open: {info}"
    assert int(info.get("len", 0)) == 308314, f"unexpected length: {info}"

    print(f"Holy windows ({len(HOLY_WINDOWS)} — static + brightness breath):")
    for s, e in HOLY_WINDOWS:
        print(f"  {s}-{e}  ({e - s} ms)")
    print(f"brightness {BRIGHT_LO} → {BRIGHT_HI} → {BRIGHT_LO}")

    if dry:
        for model, cfg in TARGETS.items():
            print(
                f"would {'clear' if clear_only else 'rebuild'} {model} "
                f"font={cfg['font_size']} static + brightness VC"
            )
        print("dry run: no changes made")
        return

    if not BACKUP.exists():
        shutil.copy2(SEQUENCE, BACKUP)
        print(f"backup: {BACKUP.name}")

    settings_by_model = {m: settings_for(cfg) for m, cfg in TARGETS.items()}
    palette = palette_for()

    for model, cfg in TARGETS.items():
        before = read_l0(model)
        if before and not owned_by_us(before):
            raise SystemExit(
                f"REFUSING TO WIPE unexpected L0 on {model}: {before}"
            )
        if before:
            wipe_l0(model)
            print(f"wiped {model} L0 ({len(before)} effects)")
        else:
            print(f"{model} L0 already empty")

        if clear_only:
            continue

        settings = settings_by_model[model]
        for s, e in HOLY_WINDOWS:
            x.add_effect(model, 0, "Text", settings, palette, s, e)
            print(f"  + {model} Text {s}-{e}")

        after = read_l0(model)
        expected = [("Text", s, e) for s, e in HOLY_WINDOWS]
        if after != expected:
            raise SystemExit(f"{model} L0 mismatch: got {after}, expected {expected}")

    x.save(str(SEQUENCE))
    print(f"saved {SEQUENCE}")
    print("done.")


if __name__ == "__main__":
    main()
