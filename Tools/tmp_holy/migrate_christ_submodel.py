"""Move Holy Forever's four Christ glows onto a dedicated submodel.

The layout must already contain `GE Merry Christmas/Christ`.  This script
changes only the two relevant submodel rows: it adds and verifies the four
replacement effects first, then wipes the old buffered effects.

Run:
    python3 migrate_christ_submodel.py --dry-run
    python3 migrate_christ_submodel.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
import xlights_api as x


EMPTY_SOURCE = "House"
OLD_TARGET = "GE Merry Christmas/Christmas"
NEW_TARGET = "GE Merry Christmas/Christ"
OLD_BUFFER = "0.00x0.00x69.10x100.00"
PALETTE = {
    "C_BUTTON_Palette1": "#FFC878",
    "C_CHECKBOX_Palette1": "1",
}
BLOCKS = [
    (40950, 44675, "2.23"),
    (45300, 48125, "1.32"),
    (48250, 51750, "2.00"),
    (61450, 64900, "1.95"),
]


def expected(with_buffer: bool) -> list[dict]:
    effects = []
    for start, end, fadein in BLOCKS:
        settings = {
            "E_TEXTCTRL_Eff_On_End": "100",
            "E_TEXTCTRL_Eff_On_Start": "100",
            "T_TEXTCTRL_Fadein": fadein,
            "T_TEXTCTRL_Fadeout": "1.50",
        }
        if with_buffer:
            settings["B_CUSTOM_SubBuffer"] = OLD_BUFFER
        effects.append({
            "name": "On",
            "startTime": start,
            "endTime": end,
            "settings": settings,
            "palette": PALETTE,
        })
    return effects


def get_effects(model: str) -> list[dict]:
    """Return L0 effects and reject unexpected effects on deeper layers."""
    try:
        layers = x.xl("getEffectIDs", model=model, timeout=15).get("effects", [])
    except Exception as exc:
        raise RuntimeError(
            f"{model!r} is unavailable; reload the show folder after adding "
            "the Christ submodel"
        ) from exc
    if any(layer for layer in layers[1:]):
        raise RuntimeError(f"{model} has effects below L0; refusing to touch it")
    result = [
        x.xl("getEffectSettings", model=model, layer=0, id=effect_id, timeout=15)
        for effect_id in (layers[0] if layers else [])
    ]
    return sorted(result, key=lambda effect: (effect["startTime"], effect["endTime"]))


def signature(effect: dict) -> tuple:
    return (
        effect["name"],
        int(effect["startTime"]),
        int(effect["endTime"]),
        tuple(sorted(effect.get("settings", {}).items())),
        tuple(sorted(effect.get("palette", {}).items())),
    )


def signatures(effects: list[dict]) -> list[tuple]:
    return [signature(effect) for effect in effects]


def require_exact(label: str, actual: list[dict], wanted: list[dict]) -> None:
    if signatures(actual) != signatures(wanted):
        raise RuntimeError(
            f"{label} does not match the expected four glows:\n"
            f"{json.dumps(actual, indent=2, sort_keys=True)}"
        )


def settings_string(fadein: str) -> str:
    return ",".join([
        "E_TEXTCTRL_Eff_On_End=100",
        "E_TEXTCTRL_Eff_On_Start=100",
        f"T_TEXTCTRL_Fadein={fadein}",
        "T_TEXTCTRL_Fadeout=1.50",
    ])


def palette_string() -> str:
    return ",".join(f"{key}={value}" for key, value in PALETTE.items())


def wipe_l0(model: str) -> None:
    x.xl(
        "cloneModelEffects",
        target=model,
        source=EMPTY_SOURCE,
        eraseModel="true",
    )
    if get_effects(model):
        raise RuntimeError(f"{model} L0 was not empty after wipe")


def main() -> None:
    dry_run = "--dry-run" in sys.argv
    info = x.xl("getOpenSequence", timeout=15)
    if info.get("seq") != "Holy Forever 2026":
        raise RuntimeError(f"wrong sequence open: {info}")

    if get_effects(EMPTY_SOURCE):
        raise RuntimeError(f"{EMPTY_SOURCE} is no longer an effect-free wipe source")

    old = get_effects(OLD_TARGET)
    new = get_effects(NEW_TARGET)
    expected_old = expected(with_buffer=True)
    expected_new = expected(with_buffer=False)

    old_ok = signatures(old) == signatures(expected_old)
    new_ok = signatures(new) == signatures(expected_new)
    if not ((old_ok and not new) or (old_ok and new_ok) or (not old and new_ok)):
        raise RuntimeError(
            "unexpected migration state; refusing to change either submodel\n"
            f"old={json.dumps(old, indent=2, sort_keys=True)}\n"
            f"new={json.dumps(new, indent=2, sort_keys=True)}"
        )

    if not old and new_ok:
        print("already migrated: Christ has four unbuffered glows; Christmas is empty")
        return

    print(
        f"{'DRY RUN — ' if dry_run else ''}move {len(BLOCKS)} On effects "
        f"from {OLD_TARGET} to {NEW_TARGET}; remove B_CUSTOM_SubBuffer"
    )
    if dry_run:
        return

    if not new:
        try:
            for start, end, fadein in BLOCKS:
                x.add_effect(
                    NEW_TARGET,
                    0,
                    "On",
                    settings_string(fadein),
                    palette_string(),
                    start,
                    end,
                )
            require_exact(NEW_TARGET, get_effects(NEW_TARGET), expected_new)
        except Exception:
            wipe_l0(NEW_TARGET)
            raise

    wipe_l0(OLD_TARGET)
    require_exact(NEW_TARGET, get_effects(NEW_TARGET), expected_new)

    output = info["fullseq"]
    x.save(output)
    print(f"saved {output}")
    print("verified: Christmas L0 empty; Christ L0 has four exact unbuffered glows")


if __name__ == "__main__":
    main()
