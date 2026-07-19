"""Build the per-voice lyric timing template for Holy Forever 2026.

Aligns faster-whisper word timestamps against the canonical lyric lines,
breaks words into Preston Blair phonemes with xLights' own dictionaries, and
writes a timing-only .xsq template (importXLightsSequence ready) with three
voice tracks:

  Lyrics Lead    - Chris Tomlin part (Snowman)
  Lyrics Female  - Jenn Johnson part (Teddy)
  Lyrics Choir   - ensemble part (bulbs, santa, grinch, tree, penguins)

Outputs:
  Timing Templates/Holy Forever Lyrics.xsq
  Tools/tmp_holy/sections.json   (per-line + per-section times for face placement)
"""
import difflib
import json
import re
import xml.sax.saxutils as sx

WORDS_JSON = '/Users/elliott.ohara/xlights/Tools/tmp_holy/words.json'
TEMPLATE_OUT = '/Users/elliott.ohara/xlights/Timing Templates/Holy Forever Lyrics.xsq'
SECTIONS_OUT = '/Users/elliott.ohara/xlights/Tools/tmp_holy/sections.json'
DICT = '/Applications/xLights.app/Contents/Resources/dictionaries/standard_dictionary'
EXT_DICT = '/Applications/xLights.app/Contents/Resources/dictionaries/extended_dictionary'
MAPPING = '/Applications/xLights.app/Contents/Resources/dictionaries/phoneme_mapping'
DURATION_MS = 308314
FRAME = 25

# ---------------- canonical lyrics: (section, line) ------------------------------
S = 'sections'
LINES = []
def sec(name, *lines):
    for ln in lines:
        LINES.append((name, ln))

sec('V1',
    "A thousand generations falling down in worship",
    "To sing the song of ages to the Lamb",
    "And all who've gone before us and all who will believe",
    "Will sing the song of ages to the Lamb")
sec('PC1',
    "Your name is the highest",
    "Your name is the greatest",
    "Your name stands above them all",
    "All thrones and dominions",
    "All powers and positions",
    "Your name stands above them all")
sec('C1',
    "And the angels cry holy",
    "All creation cries holy",
    "You are lifted high holy",
    "Holy forever")
sec('V2',
    "If you've been forgiven and if you've been redeemed",
    "Sing the song forever to the Lamb",
    "If you walk in freedom and if you bear His name",
    "Sing the song forever to the Lamb",
    "We'll sing the song forever and amen")
sec('C2a',
    "And the angels cry holy",
    "All creation cries holy",
    "You are lifted high holy",
    "Holy forever")
sec('C2b',
    "Hear your people sing holy",
    "To the King of kings holy")
sec('C2c',
    "You will always be holy",
    "Holy forever")
sec('PC2a',
    "Your name is the highest",
    "Your name is the greatest",
    "Your name stands above them all",
    "All thrones and dominions",
    "All powers and positions",
    "Your name stands above them all Jesus")
sec('PC2b',
    "Your name is the highest",
    "Your name is the greatest",
    "Your name stands above them all",
    "All thrones and dominions",
    "All powers and positions",
    "Your name stands above them all")
sec('C3a',
    "And the angels cry holy",
    "All creation cries holy",
    "You are lifted high holy",
    "Holy forever")
sec('C3b',
    "Hear your people sing holy",
    "To the King of kings holy")
sec('C3c',
    "You will always be holy",
    "Holy forever")
sec('OUT',
    "You will always be holy",
    "Holy forever")

# ---------------- phoneme machinery ----------------------------------------------
def load_mapping():
    m = {}
    for raw in open(MAPPING, encoding='utf-8', errors='replace'):
        line = raw.split('#')[0].strip()
        if not line or line.startswith('.'):
            continue
        parts = line.split()
        if len(parts) >= 2:
            m[parts[0]] = parts[1]
    return m

def load_dict():
    d = {}
    for path in (DICT, EXT_DICT):
        try:
            fh = open(path, encoding='latin-1')
        except OSError:
            continue
        for raw in fh:
            if raw.startswith(';;;') or not raw.strip():
                continue
            parts = raw.split()
            word = parts[0].upper()
            if '(' in word:      # alternate pronunciations WORD(2)
                continue
            d.setdefault(word, parts[1:])
    return d

CMU2PB = load_mapping()
CMUDICT = load_dict()

def word_phonemes(word):
    key = word.upper().strip(".,!?;:\"()")
    for cand in (key, key.replace("'", "")):
        if cand in CMUDICT:
            return [CMU2PB.get(p, 'etc') for p in CMUDICT[cand]]
    if key.endswith('S') and key[:-1] in CMUDICT:      # simple plural: THRONES
        return [CMU2PB.get(p, 'etc') for p in CMUDICT[key[:-1]]] + ['etc']
    # crude fallback: vowels -> AI, consonants -> etc
    out = []
    for ch in key:
        if ch in 'AEIOU':
            out.append({'A': 'AI', 'E': 'E', 'I': 'AI', 'O': 'O', 'U': 'U'}[ch])
        elif ch.isalpha():
            out.append('etc')
    print(f'  !! no dict entry for {word!r}, fallback {out}')
    return out or ['etc']

# ---------------- alignment ------------------------------------------------------
def norm(w):
    return re.sub(r"[^a-z']", '', w.lower())

def sim(a, b):
    if a == b:
        return 1.0
    return difflib.SequenceMatcher(None, a, b).ratio()

def align(ref, hyp):
    """Global alignment; near-matches (ratio>=0.6) also yield timestamp pairs."""
    n, m = len(ref), len(hyp)
    INS = DEL = 1.0
    simcache = {}
    def s(i, j):
        k = (ref[i], hyp[j])
        if k not in simcache:
            simcache[k] = sim(*k)
        return simcache[k]
    dp = [[0.0] * (m + 1) for _ in range(n + 1)]
    bt = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        dp[i][0] = i * DEL; bt[i][0] = 1
    for j in range(1, m + 1):
        dp[0][j] = j * INS; bt[0][j] = 2
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            r = s(i - 1, j - 1)
            sub = 0.0 if r == 1.0 else (0.4 if r >= 0.6 else 1.2)
            best = dp[i - 1][j - 1] + sub, 0
            if dp[i - 1][j] + DEL < best[0]:
                best = dp[i - 1][j] + DEL, 1
            if dp[i][j - 1] + INS < best[0]:
                best = dp[i][j - 1] + INS, 2
            dp[i][j], bt[i][j] = best
    pairs = []
    i, j = n, m
    while i > 0 or j > 0:
        op = bt[i][j]
        if op == 0:
            if s(i - 1, j - 1) >= 0.6:
                pairs.append((i - 1, j - 1))
            i, j = i - 1, j - 1
        elif op == 1:
            i -= 1
        else:
            j -= 1
    return dict(reversed(pairs))

def snap(ms):
    return int(round(ms / FRAME)) * FRAME

def main():
    hyp_words = json.load(open(WORDS_JSON))
    hyp_tokens = [norm(w['w']) for w in hyp_words]

    ref_tokens, ref_line = [], []
    for li, (_, line) in enumerate(LINES):
        for w in line.split():
            ref_tokens.append(norm(w))
            ref_line.append(li)

    matches = align(ref_tokens, hyp_tokens)
    print(f'aligned {len(matches)}/{len(ref_tokens)} reference words '
          f'({len(hyp_tokens)} transcribed)')

    # assign times: matched words directly; gaps interpolated inside the line
    times = [None] * len(ref_tokens)
    for ri, hj in matches.items():
        times[ri] = (hyp_words[hj]['s'] * 1000, hyp_words[hj]['e'] * 1000)

    # interpolate unmatched
    for i, t in enumerate(times):
        if t is not None:
            continue
        prev = next((k for k in range(i - 1, -1, -1) if times[k]), None)
        nxt = next((k for k in range(i + 1, len(times)) if times[k]), None)
        if prev is None or nxt is None:
            raise SystemExit(f'cannot interpolate word {i} ({ref_tokens[i]})')
        span_s, span_e = times[prev][1], times[nxt][0]
        gap_words = nxt - prev - 1
        pos = i - prev - 1
        w = (span_e - span_s) / max(gap_words, 1)
        times[i] = (span_s + pos * w, span_s + (pos + 1) * w)
        print(f'  interpolated {ref_tokens[i]!r} in line {ref_line[i]}')

    # clamp section starts against the human-placed section marks in the
    # existing sequence (whisper bleeds phrase starts backwards into silence).
    # value = (anchor_ms, max_pickup_ms allowed before the anchor)
    ANCHORS = {
        'V1': (15520, 250), 'PC1': (41850, 900), 'C1': (67570, 900),
        'V2': (95100, 900), 'C2a': (127630, 900), 'C2b': (154150, 900),
        'PC2a': (181900, 900), 'PC2b': (207210, 900),
        'C3a': (234230, 900), 'C3b': (260760, 900), 'OUT': (287290, 600),
    }
    seen = set()
    for li, (section, _) in enumerate(LINES):
        if section not in ANCHORS or section in seen:
            continue
        seen.add(section)
        floor, _prev = ANCHORS[section][0] - ANCHORS[section][1], None
        idxs = [i for i in range(len(ref_tokens)) if ref_line[i] == li]
        cur = floor
        moved = False
        for i in idxs:
            s, e = times[i]
            if s < cur:
                s = cur
                e = max(e, s + 150)
                times[i] = (s, e)
                moved = True
            cur = times[i][1]
        if moved:
            print(f'  clamped {section} start to >= {floor}ms '
                  f'(anchor {ANCHORS[section][0]})')

    # per-line phrase spans + word marks
    lines_out = []      # (section, text, s, e, [(word, s, e)])
    for li, (section, text) in enumerate(LINES):
        idxs = [i for i in range(len(ref_tokens)) if ref_line[i] == li]
        ws = []
        for i in idxs:
            s, e = times[i]
            ws.append([text.split()[i - idxs[0]], s, e])
        s, e = ws[0][1], ws[-1][2]
        lines_out.append({'section': section, 'text': text, 's': s, 'e': e, 'words': ws})

    # sanity: monotonic, no crazy line durations
    prev_e = 0
    for L in lines_out:
        assert L['e'] > L['s'], L
        if L['s'] < prev_e - 50:
            print(f"  !! overlap: {L['text']!r} starts {prev_e - L['s']:.0f}ms early")
        prev_e = L['e']

    # snap + enforce order and minimum widths; keep marks per line
    cursor = 0
    idx_in_sec, seen_sec = {}, {}
    for li, L in enumerate(lines_out):
        idx_in_sec[li] = seen_sec.get(L['section'], 0)
        seen_sec[L['section']] = idx_in_sec[li] + 1

        ps, pe = max(snap(L['s']), cursor), snap(L['e'])
        pe = max(pe, ps + FRAME)
        cursor = pe
        wmarks, pmarks = [], []
        wcur = ps
        nw = len(L['words'])
        for k, (w, ws_, we_) in enumerate(L['words']):
            remaining = nw - k - 1
            s = max(snap(ws_), wcur)
            s = min(s, pe - FRAME * (remaining + 1))
            e = snap(we_)
            e = max(e, s + (150 if s + 150 <= pe - FRAME * remaining else FRAME))
            e = min(e, pe - FRAME * remaining)
            if k == nw - 1:
                e = pe
            wmarks.append((w, s, e))
            wcur = e
            # phonemes: even split of the word span
            phs = word_phonemes(w)
            n = len(phs)
            span = e - s
            if span < n * FRAME:            # too tight: merge to fewer marks
                phs = phs[:max(1, span // FRAME)]
                n = len(phs)
            edges = [s + snap(span * i / n) for i in range(n)] + [e]
            edges = [snap(x) for x in edges]
            for a in range(n):
                x0, x1 = edges[a], edges[a + 1]
                if x1 <= x0:
                    x1 = x0 + FRAME
                pmarks.append((phs[a], x0, min(x1, e) if a == n - 1 else x1))
        L['s'], L['e'] = ps, pe
        L['wmarks'], L['pmarks'] = wmarks, pmarks

    # ------- per-voice track membership (line level) -------
    # C2b: lead sings backup with the female feature ("Hear Your people sing…")
    LEAD_SECS = {'V1', 'PC1', 'C1', 'C2a', 'C2b', 'C2c', 'PC2a', 'PC2b',
                 'C3a', 'C3b', 'C3c', 'OUT'}
    FEMALE_SECS = {'V2', 'C2b', 'C2c', 'PC2a', 'PC2b', 'C3a', 'C3b', 'C3c'}
    CHOIR_SECS = {'C1', 'C2a', 'C2b', 'C2c', 'PC2a', 'PC2b', 'C3a', 'C3b', 'C3c'}

    def member(track, li, L):
        if track == 'Lyrics Lead':
            # lead sings the 'amen' close of V2 but not the rest of the verse
            return L['section'] in LEAD_SECS or (
                L['section'] == 'V2' and idx_in_sec[li] == 4)
        if track == 'Lyrics Female':
            return L['section'] in FEMALE_SECS
        return L['section'] in CHOIR_SECS

    def layer(marks):
        out = ['      <EffectLayer>']
        for label, s, e in marks:
            out.append(f'        <Effect label={sx.quoteattr(label)} '
                       f'startTime="{int(s)}" endTime="{int(e)}" />')
        out.append('      </EffectLayer>')
        return '\n'.join(out)

    def track_xml(name):
        lines = [L for li, L in enumerate(lines_out) if member(name, li, L)]
        # phrase layer needs gap fillers (house template convention)
        filled, cur = [], 0
        for L in lines:
            if L['s'] > cur:
                filled.append(('', cur, L['s']))
            filled.append((L['text'], L['s'], L['e']))
            cur = L['e']
        if cur < DURATION_MS:
            filled.append(('', cur, snap(DURATION_MS - FRAME)))
        words = [m for L in lines for m in L['wmarks']]
        phos = [m for L in lines for m in L['pmarks']]
        print(f'  {name}: {len(lines)} phrases, {len(words)} words, {len(phos)} phonemes')
        return (f'    <Element type="timing" name="{name}">\n'
                f'{layer(filled)}\n{layer(words)}\n{layer(phos)}\n    </Element>')

    TRACKS = ['Lyrics Lead', 'Lyrics Female', 'Lyrics Choir']
    display = '\n'.join(
        f'    <Element collapsed="0" type="timing" name="{t}" visible="1" views="" active="1" />'
        for t in TRACKS)
    elements = '\n'.join(track_xml(t) for t in TRACKS)

    xml = f'''<?xml version='1.0' encoding='UTF-8'?>
<xsequence BaseChannel="0" ChanCtrlBasic="0" ChanCtrlColor="0" FixedPointTiming="1" ModelBlending="false">
  <head>
    <version>2026.12</version>
    <author />
    <song>Holy Forever</song>
    <artist>Chris Tomlin</artist>
    <sequenceTiming>25 ms</sequenceTiming>
    <sequenceType>Media</sequenceType>
    <mediaFile>/Users/elliott.ohara/xlights/Videos/Chris Tomlin - Holy Forever (Lyric Video).mp4</mediaFile>
    <sequenceDuration>308.314</sequenceDuration>
  </head>
  <nextid>1</nextid>
  <Jukebox />
  <ColorPalettes />
  <EffectDB />
  <DataLayers />
  <DisplayElements>
{display}
  </DisplayElements>
  <ElementEffects>
{elements}
  </ElementEffects>
  <lastView>0</lastView>
  <TimingTags />
</xsequence>
'''
    with open(TEMPLATE_OUT, 'w') as f:
        f.write(xml)

    # section spans for face placement
    sections = {}
    for L in lines_out:
        s = sections.setdefault(L['section'], {'s': L['s'], 'e': L['e'], 'lines': []})
        s['s'] = min(s['s'], L['s']); s['e'] = max(s['e'], L['e'])
        s['lines'].append({'text': L['text'], 's': L['s'], 'e': L['e']})
    with open(SECTIONS_OUT, 'w') as f:
        json.dump(sections, f, indent=1)

    for name, s in sections.items():
        print(f"  {name:5s} {s['s']:7.0f} - {s['e']:7.0f}")
    print(f'wrote {TEMPLATE_OUT}')

if __name__ == '__main__':
    main()
