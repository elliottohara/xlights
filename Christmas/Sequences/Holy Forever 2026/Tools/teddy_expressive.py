"""Rebuild EFL Teddy for Holy Forever 2026 — pink bow + expressive States.

Casting (Lyrics Female = Jenn Johnson part):
  V2, C2b–C2c, PC2a–C3. C2a (shared chorus) mouths Lyrics Choir so she stays
  present wherever the arrangement lists her.

Layers (vendor pattern from You Make It Feel Like Christmas / Can-Can):
  L0 arms State poses
  L1 eye-direction State
  L2 Brows State
  L3 Faces (def `Teddy `, UseState `Teddy PinkBow`, timing track)

Arms/brows/eyes are keyed to lyric phrase moments — raises on praise peaks,
tender brows on redemption lines, eyes heavenward on worship words.

Idempotent: clears every EFL Teddy effect via .xsq edit (API can't delete /
multi-layer wipe), close/reopen, then addEffect. Saves when not --dry-run.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import time
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / 'Tools'))
import xlights_api as x

SEQUENCE = TOOLS_DIR.parent / 'Holy Forever 2026.xsq'
SECTIONS = json.loads((TOOLS_DIR / 'sections.json').read_text())
EXPECTED_DURATION = 308314
MODEL = 'EFL Teddy'
FACE_DEF = 'Teddy '
FACE_STATE = 'Teddy PinkBow'
EMPTY_SOURCE = 'House'
FRAME = 25

# Warm fur / pad accents — Graduate blends these; CustomColors on the state
# defs still supply bow/eye/brow forced colors where set.
STATE_PALETTE = (
    'C_BUTTON_Palette1=#804000,C_BUTTON_Palette2=#FF8811,'
    'C_BUTTON_Palette3=#FF80C0,C_BUTTON_Palette4=#0000FF,'
    'C_CHECKBOX_Palette1=1,C_CHECKBOX_Palette2=1,'
    'C_CHECKBOX_Palette3=1,C_CHECKBOX_Palette4=1'
)
FACE_PALETTE = 'C_BUTTON_Palette1=#FFFFFF,C_CHECKBOX_Palette1=1'


def snap(ms: int) -> int:
    return int(round(ms / FRAME) * FRAME)


def sec(name: str) -> tuple[int, int]:
    s = SECTIONS[name]
    return int(s['s']), int(s['e'])


def lines(section: str) -> list[dict]:
    return SECTIONS[section]['lines']


def face_settings(track: str, fadeout: str | None = None) -> str:
    parts = [
        'E_CHECKBOX_Faces_Outline=1',
        'E_CHOICE_Faces_EyeBlinkFrequency=Normal',
        'E_CHOICE_Faces_Eyes=Auto',
        f'E_CHOICE_Faces_FaceDefinition={FACE_DEF}',
        f'E_CHOICE_Faces_TimingTrack={track}',
        f'E_CHOICE_Faces_UseState={FACE_STATE}',
    ]
    if fadeout:
        parts.append(f'T_TEXTCTRL_Fadeout={fadeout}')
    return ','.join(parts)


BEAT_TRACK = 'Beat Count'
BEAT_DEFS = {'flapping (beats)', 'leaning (beats)',
             'left wave (beats)', 'right wave (beats)'}


def state_settings(definition: str, state: str, fade_ms: int = 0,
                   fadein: str | None = None, fadeout: str | None = None) -> str:
    parts = [
        'E_CHOICE_State_Color=Graduate',
        'E_CHOICE_State_Mode=Default',
        f'E_CHOICE_State_State={state}',
        f'E_CHOICE_State_StateDefinition={definition}',
        f'E_SLIDER_State_Fade_Time={fade_ms}',
    ]
    if fadein:
        parts.append(f'T_TEXTCTRL_Fadein={fadein}')
    if fadeout:
        parts.append(f'T_TEXTCTRL_Fadeout={fadeout}')
    return ','.join(parts)


def beat_state_settings(definition: str) -> str:
    """Beat-driven state animation: the 1/2/3/4 Beat Count labels step the
    matching 1-4 states inside the definition (vendor recipe)."""
    return (
        'E_CHOICE_State_Color=Graduate,'
        'E_CHOICE_State_Mode=Default,'
        f'E_CHOICE_State_StateDefinition={definition},'
        f'E_CHOICE_State_TimingTrack={BEAT_TRACK},'
        'E_SLIDER_State_Fade_Time=0'
    )


def face_blocks() -> list[tuple[int, int, str, str | None]]:
    """(start, end, timing_track, fadeout) for L3 Faces."""
    v2s, v2e = sec('V2')
    c2a_s, c2a_e = sec('C2a')
    c2b_s, _ = sec('C2b')
    _, c2c_e = sec('C2c')
    pc2a_s, _ = sec('PC2a')
    _, c3e = sec('C3c')
    blocks = [
        (v2s, v2e + 300, 'Lyrics Female', None),
        # Arrangement: Teddy sings C2a with the cast; Female track has no C2a lines.
        (c2a_s, c2a_e + 300, 'Lyrics Choir', None),
        (c2b_s, c2c_e + 300, 'Lyrics Female', None),
        (pc2a_s, c3e + 1500, 'Lyrics Female', '1.5'),
    ]
    # Clamp each block before the next start.
    out = []
    for i, (s, e, track, fade) in enumerate(blocks):
        if i + 1 < len(blocks):
            e = min(e, blocks[i + 1][0])
        out.append((snap(s), snap(e), track, fade))
    return out


def _span(line: dict, start_off: int = 0, end_off: int = 0) -> tuple[int, int]:
    s = snap(int(line['s']) + start_off)
    e = snap(int(line['e']) + end_off)
    if e <= s:
        e = s + FRAME
    return s, e


def _mid_third(line: dict) -> tuple[int, int]:
    s, e = int(line['s']), int(line['e'])
    dur = e - s
    return snap(s + dur // 3), snap(s + 2 * dur // 3)


def arm_cues() -> list[tuple[int, int, str, str | None]]:
    """(start, end, definition, state) — state=None means Beat Count drives it.

    Beat-driven wave/lean/flap blocks carry the groove; held poses punctuate
    the praise peaks so she isn't doing one motion all song.
    """
    cues: list[tuple[int, int, str, str | None]] = []

    def beat(s, e, definition):
        s, e = snap(s), snap(e)
        if e > s:
            cues.append((s, e, definition, None))

    def pose(s, e, state):
        s, e = snap(s), snap(e)
        if e > s:
            cues.append((s, e, 'arms', state))

    v2 = lines('V2')
    c2a = lines('C2a')
    c2b = lines('C2b')
    c2c = lines('C2c')
    c3a = lines('C3a')
    c3b = lines('C3b')
    c3c = lines('C3c')

    # --- V2: backbeat starts here — gentle sway, one wave, raise on amen ---
    beat(v2[0]['s'], v2[2]['e'], 'leaning (beats)')
    beat(v2[3]['s'], v2[3]['e'], 'right wave (beats)')   # sing the song forever
    beat(v2[4]['s'], v2[4]['e'] - 900, 'leaning (beats)')
    pose(v2[4]['e'] - 900, v2[4]['e'] + 200, 'up')       # …and amen

    # --- C2a: chorus — flap with the choir, raise on Holy forever ---
    beat(c2a[0]['s'], c2a[2]['e'], 'flapping (beats)')
    pose(c2a[3]['s'], c2a[3]['e'] - 600, 'mid')
    pose(c2a[3]['e'] - 600, c2a[3]['e'] + 300, 'up')     # Holy forever

    # --- C2b her feature: one-arm waves, big finish ---
    beat(c2b[0]['s'], c2b[0]['e'], 'left wave (beats)')  # Hear your people sing
    beat(c2b[1]['s'], c2b[1]['e'] - 600, 'right wave (beats)')
    pose(c2b[1]['e'] - 600, c2b[1]['e'] + 200, 'up')     # King of kings

    # --- C2c: settle back, raise into the section end ---
    beat(c2c[0]['s'], c2c[0]['e'], 'leaning (beats)')
    pose(c2c[1]['s'], c2c[1]['e'] - 1000, 'mid')
    pose(c2c[1]['e'] - 1000, c2c[1]['e'] + 300, 'up')    # Holy forever

    # --- PC2a: flap → held raises on "above them all" / "Jesus" ---
    pa = lines('PC2a')
    beat(pa[0]['s'], pa[1]['e'], 'flapping (beats)')     # highest / greatest
    pose(pa[2]['s'], pa[2]['e'] - 400, 'mid')
    pose(pa[2]['e'] - 400, pa[2]['e'], 'up')             # above them all
    beat(pa[3]['s'], pa[4]['e'], 'leaning (beats)')      # thrones / powers
    pose(pa[5]['s'], pa[5]['e'] - 400, 'mid')
    pose(pa[5]['e'] - 400, pa[5]['e'], 'up')             # …Jesus

    # --- PC2b: bigger — alternate single-arm waves, then flap ---
    pb = lines('PC2b')
    beat(pb[0]['s'], pb[1]['e'], 'left wave (beats)')
    beat(pb[2]['s'], pb[2]['e'], 'right wave (beats)')
    beat(pb[3]['s'], pb[4]['e'], 'flapping (beats)')
    pose(pb[5]['s'], pb[5]['e'] - 400, 'mid')
    pose(pb[5]['e'] - 400, pb[5]['e'], 'up')

    # --- C3a: climax — flap, then held high on "lifted high" ---
    beat(c3a[0]['s'], c3a[1]['e'], 'flapping (beats)')
    pose(c3a[2]['s'], c3a[2]['e'], 'up')                 # You are lifted high
    pose(c3a[3]['s'], c3a[3]['e'] - 500, 'mid')
    pose(c3a[3]['e'] - 500, c3a[3]['e'] + 300, 'up')

    # --- C3b: her feature reprise — waves again ---
    beat(c3b[0]['s'], c3b[0]['e'], 'left wave (beats)')
    beat(c3b[1]['s'], c3b[1]['e'], 'right wave (beats)')

    # --- C3c: ease down, final raise held into the fade ---
    beat(c3c[0]['s'], c3c[0]['e'] - 500, 'leaning (beats)')
    pose(c3c[0]['e'] - 500, c3c[0]['e'], 'up')
    pose(c3c[1]['s'], c3c[1]['e'] - 450, 'mid')
    pose(c3c[1]['e'] - 450, c3c[1]['e'] + 300, 'up')     # final Holy forever

    return _merge_arm_cues(cues)


def _merge_arm_cues(cues):
    cues = sorted((snap(s), snap(e), d, st) for s, e, d, st in cues
                  if snap(e) > snap(s))
    out = []
    for s, e, d, st in cues:
        if out and s < out[-1][1]:
            s = out[-1][1]
        if e <= s:
            continue
        out.append((s, e, d, st))
    return out


def brow_cues() -> list[tuple[int, int, str]]:
    cues: list[tuple[int, int, str]] = []

    def add(s, e, pose):
        s, e = snap(s), snap(e)
        if e > s:
            cues.append((s, e, pose))

    # V2 tender → hopeful
    v2 = lines('V2')
    add(*_span(v2[0]), 'sad')                           # forgiven / redeemed
    add(*_span(v2[1]), 'highbrows')                     # sing forever
    add(*_span(v2[2]), 'sad')                           # freedom / bear His name
    add(*_span(v2[3]), 'highbrows')
    add(*_span(v2[4]), 'highbrows')                     # amen

    for sec_name in ('C2a', 'C2b', 'C2c', 'C3a', 'C3b', 'C3c'):
        for L in lines(sec_name):
            t = L['text'].lower()
            if 'forever' in t or 'lifted high' in t or 'king of kings' in t:
                add(*_span(L), 'highbrows')
            elif 'holy' in t:
                # peek of wonder on the word holy (last ~⅓)
                a, b = _mid_third(L)
                add(L['s'], a, 'highbrows')
                add(a, L['e'], 'highbrows')
            else:
                add(*_span(L), 'highbrows')

    for sec_name in ('PC2a', 'PC2b'):
        for i, L in enumerate(lines(sec_name)):
            t = L['text'].lower()
            if 'highest' in t or 'greatest' in t or 'above' in t:
                add(*_span(L), 'highbrows')
            elif 'jesus' in t:
                add(*_span(L), 'highbrows')
            else:
                # slight asymmetry for life
                add(*_span(L), 'spockleft' if i % 2 == 0 else 'spockright')

    return _merge_poses(cues)


def eye_cues() -> list[tuple[int, int, str]]:
    cues: list[tuple[int, int, str]] = []

    def add(s, e, pose):
        s, e = snap(s), snap(e)
        if e > s:
            cues.append((s, e, pose))

    # Duet: glance toward lead (stage left of Teddy ≈ right-look varies by layout;
    # upright/up for worship is safest + most readable).
    v2 = lines('V2')
    add(*_span(v2[0]), 'upleft')
    add(*_span(v2[1]), 'up')
    add(*_span(v2[2]), 'upright')
    add(*_span(v2[3]), 'up')
    add(*_span(v2[4]), 'up')

    for sec_name in ('C2a', 'C2c', 'C3a', 'C3c'):
        for i, L in enumerate(lines(sec_name)):
            t = L['text'].lower()
            if 'forever' in t or 'lifted' in t:
                add(*_span(L), 'up')
            else:
                add(*_span(L), 'upleft' if i % 2 == 0 else 'upright')

    # Her feature — look out / up more deliberately
    for L in lines('C2b'):
        add(*_span(L), 'up')

    for L in lines('C3b'):
        add(*_span(L), 'up')

    for sec_name in ('PC2a', 'PC2b'):
        for i, L in enumerate(lines(sec_name)):
            t = L['text'].lower()
            if 'above' in t or 'jesus' in t:
                add(*_span(L), 'up')
            else:
                add(*_span(L), 'left' if i % 2 == 0 else 'right')

    return _merge_poses(cues)


def _merge_poses(cues: list[tuple[int, int, str]]) -> list[tuple[int, int, str]]:
    """Sort, clamp overlaps (earlier keeps the slot), drop zero-length."""
    cues = sorted((snap(s), snap(e), p) for s, e, p in cues if snap(e) > snap(s))
    out: list[tuple[int, int, str]] = []
    for s, e, p in cues:
        if out and s < out[-1][1]:
            s = out[-1][1]
        if e <= s:
            continue
        if out and out[-1][2] == p and s <= out[-1][1]:
            out[-1] = (out[-1][0], max(out[-1][1], e), p)
        else:
            out.append((s, e, p))
    return out


def clear_teddy_xsq(path: Path, dry: bool) -> int:
    """Remove every effect under EFL Teddy; leave a single empty EffectLayer."""
    text = path.read_text(encoding='utf-8')
    pattern = re.compile(
        r'(<Element type="model" name="EFL Teddy">)(.*?)(</Element>)',
        re.S,
    )
    m = pattern.search(text)
    if not m:
        raise RuntimeError('EFL Teddy ElementEffects block not found')
    inner = m.group(2)
    n = len(re.findall(r'<Effect\b', inner))
    replacement = (
        f'{m.group(1)}\n'
        f'      <EffectLayer/>\n'
        f'    {m.group(3)}'
    )
    print(f'  clear EFL Teddy: {n} effects → empty EffectLayer'
          f'{" (dry-run)" if dry else ""}')
    if not dry:
        path.write_text(pattern.sub(replacement, text, count=1), encoding='utf-8')
    return n


def assert_open() -> None:
    info = x.xl('getOpenSequence')
    assert info.get('seq') == 'Holy Forever 2026', info
    assert int(info.get('len', 0)) == EXPECTED_DURATION, info
    assert Path(info.get('fullseq', '')).resolve() == SEQUENCE.resolve(), info


def reopen() -> None:
    x.xl('closeSequence', force='true', quiet='true')
    x.xl('openSequence', seq=str(SEQUENCE), timeout=120)
    # allow UI to settle
    for _ in range(40):
        try:
            assert_open()
            return
        except Exception:
            time.sleep(0.25)
    assert_open()


def add_states(layer: int, definition: str, cues: list[tuple[int, int, str]],
               dry: bool) -> int:
    n = 0
    for s, e, pose in cues:
        settings = state_settings(definition, pose, fade_ms=80)
        print(f'  L{layer} State {definition}/{pose} {s}-{e}')
        if not dry:
            x.add_effect(MODEL, layer, 'State', settings, STATE_PALETTE, s, e)
        n += 1
    return n


def add_arm_states(cues, dry: bool) -> int:
    n = 0
    for s, e, definition, pose in cues:
        if pose is None:
            settings = beat_state_settings(definition)
            label = f'{definition} @ {BEAT_TRACK}'
        else:
            settings = state_settings(definition, pose, fade_ms=80)
            label = f'{definition}/{pose}'
        print(f'  L0 State {label} {s}-{e}')
        if not dry:
            x.add_effect(MODEL, 0, 'State', settings, STATE_PALETTE, s, e)
        n += 1
    return n


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--no-save', action='store_true',
                    help='build but skip saveSequence')
    args = ap.parse_args()
    dry = args.dry_run

    assert_open()
    faces = face_blocks()
    arms = arm_cues()
    brows = brow_cues()
    eyes = eye_cues()
    print(f'plan: {len(faces)} Faces, {len(arms)} arms, {len(brows)} brows, '
          f'{len(eyes)} eyes')
    for s, e, track, fade in faces:
        print(f'  L3 Faces {s}-{e} track={track} fade={fade}')

    if dry:
        add_arm_states(arms, True)
        add_states(1, 'eye direction', eyes, True)
        add_states(2, 'Brows', brows, True)
        print('dry-run only — no changes')
        return

    # Save live session, backup, clear via .xsq, reopen.
    x.save(str(SEQUENCE))
    bak = SEQUENCE.with_suffix(SEQUENCE.suffix + '.bak-before-teddy-expressive')
    shutil.copy2(SEQUENCE, bak)
    print(f'  backup → {bak.name}')
    clear_teddy_xsq(SEQUENCE, dry=False)
    reopen()

    src = x.xl('getEffectIDs', model=EMPTY_SOURCE)['effects']
    assert all(not layer for layer in src), f'{EMPTY_SOURCE} not empty: {src}'
    left = x.xl('getEffectIDs', model=MODEL)['effects']
    assert all(not layer for layer in left), f'Teddy not empty after clear: {left}'

    n = 0
    n += add_arm_states(arms, False)
    n += add_states(1, 'eye direction', eyes, False)
    n += add_states(2, 'Brows', brows, False)

    for s, e, track, fade in faces:
        print(f'  L3 Faces {s}-{e} {track}')
        x.add_effect(MODEL, 3, 'Faces', face_settings(track, fade),
                     FACE_PALETTE, s, e)
        n += 1

    # Verify
    ids = x.xl('getEffectIDs', model=MODEL)['effects']
    assert len(ids) >= 4, ids
    assert len(ids[0]) == len(arms), (len(ids[0]), len(arms))
    assert len(ids[1]) == len(eyes), (len(ids[1]), len(eyes))
    assert len(ids[2]) == len(brows), (len(ids[2]), len(brows))
    assert len(ids[3]) == len(faces), (len(ids[3]), len(faces))

    # Spot-check PinkBow + one of each state
    sample = x.xl('getEffectSettings', model=MODEL, layer='3', id=str(ids[3][0]))
    st = sample['settings']
    assert sample.get('name') == 'Faces', sample
    assert st.get('E_CHOICE_Faces_UseState') == FACE_STATE, st
    assert st.get('E_CHOICE_Faces_FaceDefinition') == FACE_DEF, st
    assert st.get('E_CHOICE_Faces_TimingTrack') == faces[0][2], st

    arm0 = x.xl('getEffectSettings', model=MODEL, layer='0', id=str(ids[0][0]))
    assert arm0.get('name') == 'State', arm0
    st0 = arm0['settings']
    if arms[0][3] is None:
        assert st0.get('E_CHOICE_State_StateDefinition') == arms[0][2], st0
        assert st0.get('E_CHOICE_State_TimingTrack') == BEAT_TRACK, st0
    else:
        assert st0.get('E_CHOICE_State_StateDefinition') == 'arms', st0

    eye0 = x.xl('getEffectSettings', model=MODEL, layer='1', id=str(ids[1][0]))
    assert eye0['settings'].get('E_CHOICE_State_StateDefinition') == 'eye direction'

    brow0 = x.xl('getEffectSettings', model=MODEL, layer='2', id=str(ids[2][0]))
    assert brow0['settings'].get('E_CHOICE_State_StateDefinition') == 'Brows'

    print(f'verified: {n} effects on {MODEL} '
          f'(L0={len(ids[0])} L1={len(ids[1])} L2={len(ids[2])} L3={len(ids[3])})')

    if not args.no_save:
        x.save(str(SEQUENCE))
        print(f'saved {SEQUENCE}')
    else:
        print('built but not saved (--no-save)')


if __name__ == '__main__':
    main()
