"""Add intro choir "Holy" lyric track + subtle bulb faces for Holy Forever 2026.

The ethereal pad opens with the choir singing "Holy" twice (same windows as the
downstairs glowing crosses / Whole Scene snow pulses). Whisper can't hear it, so
marks are hand-placed from the verified mid-channel RMS swells.

1. Write Timing Templates/Holy Forever Intro Choir.xsq (track: Lyrics Intro Choir)
2. Import it once into the open sequence (add-only — do not re-import)
3. Add Faces on Singing Bulb L/C/R for the intro, palette matched to the warm
   white/gold cross (no C9 glass). Existing C1+ choir faces are left alone.

Does NOT save or render — scrub in the editor; save when happy.

Re-run is safe for the Faces step (wipe+re-add on bulbs only for the intro
block via off-park is NOT used — instead we delete-by-wipe of ALL bulb faces
and re-add intro + existing choir blocks). Prefer running after a backup if
re-applying. For a clean rebuild of ALL faces including intro, use fix_faces.py.
"""
import sys
from xml.sax.saxutils import escape, quoteattr

sys.path.insert(0, '/Users/elliott.ohara/xlights/Tools')
import xlights_api as x

TRACK = 'Lyrics Intro Choir'
TEMPLATE = ('/Users/elliott.ohara/xlights/Timing Templates/'
            'Holy Forever Intro Choir.xsq')
MEDIA = ('/Users/elliott.ohara/xlights/Videos/'
         'Chris Tomlin - Holy Forever (Lyric Video).mp4')
DURATION_MS = 308314
FRAME = 25
EMPTY_SOURCE = 'House'

# Same windows as glowing crosses / intro snow Holy pulses
HOLYS = [
    (3900, 6600),
    (10550, 13550),
]

# HOLY → HH OW L IY → etc O L E (xLights phoneme_mapping)
PHONEMES = ['etc', 'O', 'L', 'E']

BULBS = [
    'Singing Bulb - Left',
    'Singing Bulb - Center',
    'Singing Bulb - Right',
]

# Subtle cross match: soft warm white mouth/eyes, muted gold glass + base.
# (Chorus C9 R/G/B is intentionally NOT used here.)
CROSS_PAL = (
    'C_BUTTON_Palette1=#EEEAE2,C_CHECKBOX_Palette1=1,'
    'C_BUTTON_Palette2=#EEEAE2,C_CHECKBOX_Palette2=1,'
    'C_BUTTON_Palette3=#C8A878,C_CHECKBOX_Palette3=1,'
    'C_BUTTON_Palette4=#8B6B3D,C_CHECKBOX_Palette4=1,'
    'C_SLIDER_Brightness=45'
)

FACE_DEF = 'Boscoyo ChromaBulb Face'


def snap(ms):
    return int(round(ms / FRAME) * FRAME)


def build_template():
    """3-layer timing track: phrases (contiguous) / words / phonemes."""
    phrases = []  # (label, s, e)
    words = []
    phos = []
    cur = 0
    for s, e in HOLYS:
        s, e = snap(s), snap(e)
        if s > cur:
            phrases.append(('', cur, s))
        phrases.append(('Holy', s, e))
        words.append(('Holy', s, e))
        n = len(PHONEMES)
        span = e - s
        edges = [s + snap(span * i / n) for i in range(n)] + [e]
        for i, p in enumerate(PHONEMES):
            a, b = edges[i], edges[i + 1]
            if b <= a:
                b = a + FRAME
            phos.append((p, a, min(b, e) if i == n - 1 else b))
        cur = e
    if cur < DURATION_MS:
        phrases.append(('', cur, snap(DURATION_MS - FRAME)))

    def layer(marks):
        lines = ['      <EffectLayer>']
        for label, s, e in marks:
            lines.append(f'        <Effect label={quoteattr(label)} '
                         f'startTime="{int(s)}" endTime="{int(e)}" />')
        lines.append('      </EffectLayer>')
        return '\n'.join(lines)

    xml = f'''<?xml version='1.0' encoding='UTF-8'?>
<xsequence BaseChannel="0" ChanCtrlBasic="0" ChanCtrlColor="0" FixedPointTiming="1" ModelBlending="false">
  <head>
    <version>2026.12</version>
    <author />
    <song>Holy Forever</song>
    <artist>Chris Tomlin</artist>
    <sequenceTiming>25 ms</sequenceTiming>
    <sequenceType>Media</sequenceType>
    <mediaFile>{escape(MEDIA)}</mediaFile>
    <sequenceDuration>308.314</sequenceDuration>
  </head>
  <nextid>1</nextid>
  <Jukebox />
  <ColorPalettes />
  <EffectDB />
  <DataLayers />
  <DisplayElements>
    <Element collapsed="0" type="timing" name="{escape(TRACK)}" visible="1" views="" active="1" />
  </DisplayElements>
  <ElementEffects>
    <Element type="timing" name="{escape(TRACK)}">
{layer(phrases)}
{layer(words)}
{layer(phos)}
    </Element>
  </ElementEffects>
  <lastView>0</lastView>
  <TimingTags />
</xsequence>
'''
    with open(TEMPLATE, 'w') as f:
        f.write(xml)
    print(f'wrote {TEMPLATE}')
    print(f'  {TRACK}: {sum(1 for l,_,_ in phrases if l)} phrases, '
          f'{len(words)} words, {len(phos)} phonemes')


def track_exists():
    try:
        r = x.xl('getEffectIDs', model=TRACK, timeout=15)
        return bool(r.get('effects'))
    except Exception:
        return False


def import_track():
    if track_exists():
        print(f'{TRACK} already in sequence — skipping import '
              f'(re-import would risk duplicate marks)')
        return
    print(f'importing {TEMPLATE}…')
    x.import_timings(TEMPLATE)
    assert track_exists(), f'{TRACK} missing after import'
    # spot-check the two Holy word marks
    words = x.xl('getEffectIDs', model=TRACK)['effects'][1]
    got = []
    for eid in words:
        e = x.xl('getEffectSettings', model=TRACK, layer='1', id=str(eid))
        if e.get('name') == 'Holy':
            got.append((int(e['startTime']), int(e['endTime'])))
    assert got == list(HOLYS), f'Holy word marks mismatch: {got}'
    print(f'  verified Holy words at {got}')


def face_settings(fadein=None, fadeout=None):
    s = ('E_CHECKBOX_Faces_Outline=1,E_CHOICE_Faces_EyeBlinkFrequency=Normal,'
         'E_CHOICE_Faces_Eyes=Auto,'
         f'E_CHOICE_Faces_FaceDefinition={FACE_DEF},'
         f'E_CHOICE_Faces_TimingTrack={TRACK}')
    if fadein:
        s += f',T_TEXTCTRL_Fadein={fadein}'
    if fadeout:
        s += f',T_TEXTCTRL_Fadeout={fadeout}'
    return s


def add_bulb_faces():
    """Add one intro Faces block per bulb (3900 → end of 2nd Holy + fade).

    Leaves existing C1+ choir Faces intact: only adds if no intro-era Faces
    already present on layer 0.
    """
    s0, _ = HOLYS[0]
    _, e1 = HOLYS[1]
    # Match cross fades roughly; +300 ms tail like other non-final face blocks
    start, end = s0, e1 + 300

    for el in BULBS:
        ids = x.xl('getEffectIDs', model=el)['effects'][0]
        existing = []
        for eid in ids:
            e = x.xl('getEffectSettings', model=el, layer='0', id=str(eid))
            existing.append((int(e['startTime']), int(e['endTime']),
                             e['settings'].get('E_CHOICE_Faces_TimingTrack'),
                             e.get('name')))
        # already have an intro-choir face?
        if any(t == TRACK for _, _, t, _ in existing):
            print(f'  {el}: intro Faces already present — skip')
            continue
        # refuse to overlap anything
        if any(not (end <= a or start >= b) for a, b, _, _ in existing):
            raise SystemExit(f'{el}: intro window {start}-{end} overlaps {existing}')
        x.add_effect(el, 0, 'Faces',
                     face_settings(fadein='0.50', fadeout='1.50'),
                     CROSS_PAL, start, end)
        print(f'  {el}: Faces {start}-{end} on {TRACK} (cross-warm, brightness 45)')


def main():
    info = x.xl('getOpenSequence')
    assert 'Holy Forever 2026' in info.get('seq', ''), f'wrong sequence open: {info}'

    build_template()
    import_track()
    print('adding intro Faces on singing bulbs…')
    add_bulb_faces()
    print('done (not saved, not rendered)')


if __name__ == '__main__':
    main()
