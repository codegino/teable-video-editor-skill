#!/usr/bin/env python3
"""Local word-level transcription for the Herk Edit Kit (replaces its ElevenLabs step).

    python3 transcribe.py <video> [--language tl|en|auto] [--secondary en] [--model medium] [--out raw.json]

Writes {text, audio_duration_secs, words: [{text, start, end}]} next to the video by default.
Footage never leaves the sandbox. Needs: python3 -m pip install faster-whisper
"""
import argparse
import json
import subprocess
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument('video')
parser.add_argument('--language', default='auto', help='Whisper code (tl, en, es, ...) or auto')
parser.add_argument('--secondary', nargs='*', default=[], help='Other languages mixed in (Taglish: --language tl --secondary en)')
parser.add_argument('--model', default='medium')
parser.add_argument('--threads', type=int, default=4)
parser.add_argument('--out')
args = parser.parse_args()

video = Path(args.video)
out = Path(args.out) if args.out else video.with_suffix('.json')
duration = float(subprocess.check_output(
    ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(video)], text=True))

from faster_whisper import WhisperModel  # noqa: E402

# Mixed speech (Taglish) must auto-detect so code-switching is kept, not translated.
language = None if args.language == 'auto' or args.secondary else args.language
model = WhisperModel(args.model, device='cpu', compute_type='int8', cpu_threads=args.threads)
segments, info = model.transcribe(str(video), language=language, task='transcribe', beam_size=5,
                                  word_timestamps=True, vad_filter=True)
words = [{'text': w.word.strip(), 'start': round(w.start, 3), 'end': round(w.end, 3)}
         for s in segments for w in (s.words or []) if w.word.strip() and w.end >= w.start]
if not words:
    raise SystemExit('No words with timestamps came back. Is there speech in this video?')
out.write_text(json.dumps({'text': ' '.join(w['text'] for w in words), 'audio_duration_secs': duration,
                           'language_code': info.language, 'model': args.model, 'words': words},
                          ensure_ascii=False, indent=2), encoding='utf-8')
print(f'Wrote {len(words)} words ({duration:.1f} s, {info.language}) to {out}')
