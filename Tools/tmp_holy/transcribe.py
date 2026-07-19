"""Word-level transcription of the Holy Forever vocal via faster-whisper."""
import json
import sys

from faster_whisper import WhisperModel

AUDIO = '/Users/elliott.ohara/xlights/Tools/tmp_holy/audio.wav'
OUT = '/Users/elliott.ohara/xlights/Tools/tmp_holy/words.json'
MODEL = sys.argv[1] if len(sys.argv) > 1 else 'medium'

model = WhisperModel(MODEL, device='cpu', compute_type='int8')
segments, info = model.transcribe(
    AUDIO, word_timestamps=True, vad_filter=False,
    condition_on_previous_text=False, beam_size=5,
    initial_prompt='Holy Forever, a worship song by Chris Tomlin.')

words = []
for seg in segments:
    for w in seg.words or []:
        words.append({'w': w.word.strip(), 's': round(w.start, 3), 'e': round(w.end, 3)})
    print(f'[{seg.start:7.2f} {seg.end:7.2f}] {seg.text}', flush=True)

with open(OUT, 'w') as f:
    json.dump(words, f, indent=1)
print(f'WROTE {len(words)} words -> {OUT}')
