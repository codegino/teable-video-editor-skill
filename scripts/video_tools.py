#!/usr/bin/env python3
"""Local media preparation. No network uploads, publishing, or destructive writes."""
import argparse
import json
import math
import subprocess
from pathlib import Path

DEFAULT_STYLE = Path(__file__).resolve().parents[1] / 'references' / 'my-style.json'


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


def inspect_video(path):
    return json.loads(subprocess.check_output([
        'ffprobe', '-v', 'error', '-show_format', '-show_streams', '-of', 'json', str(path)
    ], text=True))


def checked_words(transcript):
    duration = float(transcript['audio_duration_secs'])
    if not math.isfinite(duration) or duration <= 0:
        raise ValueError('Source duration must be a positive finite number.')
    result = []
    for word in transcript.get('words', []):
        text = str(word.get('text', '')).strip()
        if not text:
            continue
        start, end = float(word['start']), float(word['end'])
        if not all(math.isfinite(x) for x in [start, end]) or start < 0 or end < start or end > duration + .05:
            raise ValueError(f'Invalid word interval: {word}')
        if result and start < result[-1]['start']:
            raise ValueError('Words are out of order. Review the transcript instead of silently sorting.')
        result.append(dict(word, text=text, start=start, end=min(end, duration)))
    return duration, result


def plan_cuts(transcript, style):
    duration, words = checked_words(transcript)
    cfg = style['pace']
    threshold = float(cfg['silence_threshold_seconds'])
    breath = float(cfg['retained_pause_seconds'])
    guard = float(cfg['word_guard_seconds'])
    if threshold <= 0 or breath < 0 or guard < 0:
        raise ValueError('Invalid pause settings.')
    deletes = []
    long_only = cfg.get('trim_leading_trailing_only_when_long', True)
    if words and cfg.get('trim_silence', True):
        first = words[0]['start']
        head = max(float(cfg['head_pad_seconds']), guard)
        if first > head and (not long_only or first > threshold):
            deletes.append({'start': 0.0, 'end': first-head, 'reason': 'long leading silence'})
        # Track the furthest spoken end so overlapping ASR tokens cannot expose speech to cuts.
        prev_end = words[0]['end']
        for word in words[1:]:
            gap = word['start'] - prev_end
            if gap > threshold:
                left = max(guard, breath/2)
                right = max(guard, breath/2)
                begin, end = prev_end+left, word['start']-right
                if end-begin >= .04:
                    deletes.append({'start': begin, 'end': end, 'reason': 'long internal silence'})
            prev_end = max(prev_end, word['end'])
        tail = max(float(cfg['tail_pad_seconds']), guard)
        if duration-prev_end > tail and (not long_only or duration-prev_end > threshold):
            deletes.append({'start': prev_end+tail, 'end': duration, 'reason': 'long trailing silence'})
    # A clip without detected speech stays whole for visual review.
    keep = []
    cursor = 0.0
    for item in deletes:
        if item['start'] < cursor - 1e-6:
            raise ValueError('Overlapping cuts; review transcript.')
        if item['start'] > cursor:
            keep.append({'start': cursor, 'end': item['start']})
        cursor = item['end']
    if cursor < duration:
        keep.append({'start': cursor, 'end': duration})
    removed = sum(d['end']-d['start'] for d in deletes)
    def retime(t):
        return t-sum(max(0, min(t,d['end'])-d['start']) for d in deletes)
    retimed = []
    for w in words:
        for d in deletes:
            if d['start'] < w['end']-1e-7 and d['end'] > w['start']+1e-7:
                raise ValueError(f'A proposed cut touches speech: {w["text"]}')
        retimed.append(dict(w, source_start=w['start'], source_end=w['end'],
                            start=round(retime(w['start']),6), end=round(retime(w['end']),6)))
    edl = {'source_duration': duration, 'edited_duration': round(duration-removed,6),
           'removed_seconds': round(removed,6), 'delete_ranges': deletes, 'keep_ranges': keep,
           'status': 'proposal; review context before rendering', 'settings': cfg}
    return edl, {'audio_duration_secs': edl['edited_duration'], 'source_audio_duration_secs': duration,
                 'words': retimed, 'language': transcript.get('language'),
                 'requested_language': transcript.get('requested_language')}


def caption_events(transcript, style):
    """Build phrase chunks by default; preserve measured word timing for review.

    Grouping is a readable first pass, not a language parser. Review phrase
    boundaries and use break_before/break_after on words for editorial control.
    """
    duration, words = checked_words(transcript)
    cfg = style['captions']
    mode = cfg['mode']
    if mode == 'off':
        return []
    if mode not in ('phrase_chunks', 'single_word'):
        raise ValueError(f'Unknown caption mode: {mode}')
    for i, word in enumerate(words):
        if len(word['text'].split()) != 1:
            raise ValueError(f'Use aligned word tokens, not sentence timestamps: {word["text"]!r}')
        if word['end'] <= word['start'] or (i and word['start'] <= words[i-1]['start']):
            raise ValueError('Zero-duration or shared word onset; review alignment before captioning.')
        if i and word['start'] < words[i-1]['end'] - 1e-6:
            raise ValueError('Overlapping caption word intervals; review alignment before captioning.')

    if mode == 'single_word':
        groups = [[word] for word in words]
    else:
        min_words = int(cfg['target_words_min'])
        max_words = int(cfg['max_words'])
        max_chars = int(cfg['max_chars'])
        max_seconds = float(cfg['max_duration_seconds'])
        gap_limit = float(cfg['pause_break_seconds'])
        if not (1 <= min_words <= max_words and max_chars > 0 and max_seconds > 0 and gap_limit >= 0):
            raise ValueError('Invalid phrase chunk settings.')
        groups, group = [], []
        for word in words:
            if group:
                previous = group[-1]
                position_changed = word.get('center_y_fraction', cfg['center_y_fraction']) != previous.get('center_y_fraction', cfg['center_y_fraction'])
                boundary = (word.get('break_before') or previous.get('break_after') or
                            word.get('source') != previous.get('source') or position_changed or
                            word['start']-previous['end'] >= gap_limit or
                            len(group) >= max_words or
                            len(' '.join(w['text'] for w in group+[word])) > max_chars or
                            word['end']-group[0]['start'] > max_seconds)
                if boundary:
                    groups.append(group)
                    group = []
            group.append(word)
            # A.I. and similar acronyms are not automatic sentence endings.
            ending = word['text'].rstrip('\"\'”’)]}')
            sentence_end = (bool(ending) and ending[-1] in cfg['sentence_breaks'] and
                            not (ending.endswith('.') and ending.count('.') > 1))
            phrase_end = bool(ending) and ending[-1] in cfg['phrase_breaks'] and len(group) >= min_words
            if sentence_end or phrase_end or word.get('break_after'):
                groups.append(group)
                group = []
        if group:
            groups.append(group)

    events = []
    for i, group in enumerate(groups):
        start = group[0]['start']
        next_start = groups[i+1][0]['start'] if i+1 < len(groups) else duration
        end = min(duration, group[-1]['end']+float(cfg['max_hold_after_word_seconds']), next_start)
        text = ' '.join(w['text'] for w in group)
        if end <= start:
            raise ValueError('Nonpositive caption duration; review word alignment.')
        event = {'text': text, 'start': start, 'end': round(end, 6), 'mode': mode,
                 'animation': cfg['animation'] if mode == 'phrase_chunks' else 'single-word pop',
                 'color': cfg['color'],
                 'center_y_fraction': group[0].get('center_y_fraction', cfg['center_y_fraction']),
                 'words': [dict(w) for w in group]}
        if mode == 'single_word':
            event['pop_seconds'] = min(float(cfg['pop_seconds']), (end-start)/2)
        else:
            event['entrance_seconds'] = min(float(cfg['entrance_seconds']), (end-start)/3)
            # Width and line count need the actual renderer/font; do not guess
            # character-based line breaks or silently truncate long words.
            event['layout_review_required'] = (len(text) > int(cfg['max_chars']) or
                                               any(len(w['text']) > int(cfg['max_chars_per_line']) for w in group) or
                                               group[-1]['end']-start > float(cfg['max_duration_seconds']))
        events.append(event)
    return events


def srt_timestamp(t):
    ms = round(t*1000)
    seconds, ms = divmod(ms,1000)
    minutes, seconds = divmod(seconds,60)
    hours, minutes = divmod(minutes,60)
    return f'{hours:02}:{minutes:02}:{seconds:02},{ms:03}'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    probe = sub.add_parser('inspect')
    probe.add_argument('file'); probe.add_argument('--out', required=True)
    trans = sub.add_parser('transcribe')
    trans.add_argument('file'); trans.add_argument('--out', required=True)
    trans.add_argument('--language', required=True, choices=['tagalog','english','taglish'])
    trans.add_argument('--model', default='medium')
    trans.add_argument('--threads',type=int,default=4)
    for name in ['plan','captions']:
        p = sub.add_parser(name); p.add_argument('transcript'); p.add_argument('--out-dir', required=True)
        p.add_argument('--style', required=True, help='Resolved style JSON imported from the selected Markdown profile')
    args = parser.parse_args()
    if args.command == 'inspect':
        save(args.out, inspect_video(args.file))
    elif args.command == 'transcribe':
        from faster_whisper import WhisperModel
        probe = inspect_video(args.file)
        if not any(s.get('codec_type')=='audio' for s in probe['streams']):
            raise ValueError('No audio stream. Continue with a visual-only edit; do not fabricate speech.')
        model = WhisperModel(args.model, device='cpu', compute_type='int8', cpu_threads=args.threads)
        language = {'tagalog':'tl','english':'en','taglish':None}[args.language]
        segments, info = model.transcribe(args.file, language=language, task='transcribe',
                                         beam_size=5, word_timestamps=True, vad_filter=True)
        words=[]; sentences=[]
        for segment in segments:
            sentences.append(segment.text.strip())
            for word in segment.words or []:
                words.append({'text':word.word.strip(),'start':word.start,'end':word.end,
                              'probability':word.probability})
        save(args.out, {'source':str(Path(args.file).resolve()), 'text':' '.join(sentences),
                        'audio_duration_secs':float(probe['format']['duration']), 'words':words,
                        'requested_language':args.language,'language':info.language,'model':args.model,
                        'review_status':'machine transcript; review uncertain words'})
    elif args.command == 'plan':
        edl, retimed = plan_cuts(load(args.transcript),load(args.style))
        folder = Path(args.out_dir)
        save(folder/'edl.json',edl); save(folder/'retimed.json',retimed)
        print(f'Proposed duration: {edl["edited_duration"]:.3f}s; silence removed: {edl["removed_seconds"]:.3f}s')
    else:
        events = caption_events(load(args.transcript),load(args.style))
        folder = Path(args.out_dir);folder.mkdir(parents=True,exist_ok=True)
        save(folder/'caption-events.json',events)
        srt='\n'.join(f'{i+1}\n{srt_timestamp(e["start"])} --> {srt_timestamp(e["end"])}\n{e["text"]}\n' for i,e in enumerate(events))
        (folder/'captions.srt').write_text(srt,encoding='utf-8')
        print(f'Generated {len(events)} nonoverlapping caption events ({load(args.style)["captions"]["mode"]}).')

if __name__ == '__main__':
    main()
