#!/usr/bin/env python3
"""Portable video-style profiles. Standard library only; no account or hidden storage."""
import argparse
import copy
import json
import math
import re
from pathlib import Path
from video_tools import DEFAULT_STYLE, inspect_video

MARKER = '<!-- teable-video-editor-profile:v1 -->'
LEGACY_MARKER = '<!-- my-video-editor-profile:v1 -->'  # profiles saved before the repo rename
FORMATS = {'vertical': (1080, 1920, '9:16'), 'landscape': (1920, 1080, '16:9'), 'square': (1080, 1080, '1:1')}
CHOICES = {
    'orientation': tuple(FORMATS), 'language': ('tagalog', 'english', 'taglish', 'ask'),
    'captions': ('phrase_chunks', 'single_word', 'off'),
    'pace': ('natural', 'gentle', 'keep_all'), 'graphics': ('minimal', 'balanced', 'demonstrate'),
    'transitions': ('swipe', 'fade', 'none'), 'color': ('orange_teal', 'neutral'),
    'delivery': ('mp4', 'mp4_srt', 'editable'), 'fps': ('source', '30', '60'),
}
BOOLS = {'branding', 'intro', 'outro', 'hook', 'music', 'sound_effects'}
TEXT = {'name', 'brand_name', 'website', 'handle', 'style_reference', 'reference_notes'}


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def base_style(preset='neutral'):
    s = read_json(DEFAULT_STYLE)
    s['version'] = 3
    s['language']['default'] = 'ask'
    s['branding']['name'] = 'Code Gino'
    s['branding']['intro']['enabled'] = True
    s['branding']['outro']['enabled'] = True
    s['pace']['trim_silence'] = True
    s['style_reference'] = {'url_or_name': '', 'reviewed_traits': '', 'status': 'not supplied'}
    if preset == 'neutral':
        s['name'] = 'My style'
        s['branding'].update(enabled=False, name='', website='', handle='')
        s['branding']['intro']['enabled'] = False
        s['branding']['outro']['enabled'] = False
        s['delivery']['editable_project_zip'] = False
    elif preset != 'code-gino':
        raise ValueError('Preset must be neutral or code-gino')
    return s


def suggestions_from_probe(probe):
    videos = [s for s in probe.get('streams', []) if s.get('codec_type') == 'video']
    if not videos:
        raise ValueError('No video stream in metadata')
    v = videos[0]
    width, height = int(v['width']), int(v['height'])
    rotation = float(v.get('tags', {}).get('rotate', 0))
    for side in v.get('side_data_list', []):
        if 'rotation' in side:
            rotation = float(side['rotation'])
    if round(rotation) % 180 == 90:
        width, height = height, width
    orientation = 'square' if width == height else ('vertical' if height > width else 'landscape')
    fps = None
    try:
        numerator, denominator = v.get('avg_frame_rate', '0/0').split('/')
        fps = float(numerator) / float(denominator)
        if not math.isfinite(fps) or fps <= 0:
            fps = None
    except (ValueError, ZeroDivisionError):
        pass
    return {
        'suggested_answers': {'orientation': orientation, 'fps': 'source'},
        'observations': {'display_width': width, 'display_height': height, 'rotation': rotation,
                         'source_fps': fps, 'has_audio': any(s.get('codec_type') == 'audio' for s in probe.get('streams', [])),
                         'hdr': v.get('color_transfer') in ('arib-std-b67', 'smpte2084')},
        'note': 'Suggestions only. Confirm the target platform; source orientation is not necessarily the desired output. Language, branding and taste cannot be inferred from this metadata.'
    }


def set_orientation(s, choice):
    width, height, ratio = FORMATS[choice]
    s['format'].update(orientation=choice, width=width, height=height, aspect_ratio=ratio)
    s['format']['platforms'] = {'vertical': ['Reels', 'TikTok', 'Shorts'], 'landscape': ['YouTube', 'web'], 'square': ['social feed']}[choice]
    # Layout starting points, not promises of fit; use real font/frame review.
    scale = min(width, height) / 1080
    s['captions'].update(font_size_px=round((72 if choice == 'vertical' else 54)*scale),
                         min_font_size_px=round((48 if choice == 'vertical' else 36)*scale),
                         safe_horizontal_px=round(width*.0833), safe_bottom_px=round(height*.1042),
                         max_width_px=round(width*.8333))


def merge_known(target, patch, path=''):
    if not isinstance(patch, dict):
        raise ValueError(f'{path or "advanced"} must be an object')
    for key, value in patch.items():
        if key not in target:
            raise ValueError(f'Unknown advanced setting: {path}{key}')
        current = target[key]
        if isinstance(current, dict):
            merge_known(current, value, path+key+'.')
        elif type(current) is bool:
            if type(value) is not bool:
                raise ValueError(f'{path}{key} must be boolean')
            target[key] = value
        elif isinstance(current, (int, float)):
            if type(value) not in (int, float) or not math.isfinite(value):
                raise ValueError(f'{path}{key} must be finite numeric')
            target[key] = value
        elif not isinstance(value, type(current)):
            raise ValueError(f'Wrong type for {path}{key}')
        else:
            target[key] = copy.deepcopy(value)


def apply_answers(style, answers):
    s = copy.deepcopy(style)
    if not isinstance(answers, dict):
        raise ValueError('Answers must be an object')
    allowed = set(CHOICES) | BOOLS | TEXT | {'palette', 'advanced'}
    if set(answers)-allowed:
        raise ValueError(f'Unknown answers: {sorted(set(answers)-allowed)}')
    for key, options in CHOICES.items():
        if key in answers and answers[key] not in options:
            raise ValueError(f'{key} must be one of {options}')
    for key in BOOLS:
        if key in answers and type(answers[key]) is not bool:
            raise ValueError(f'{key} must be boolean')
    for key in TEXT:
        if key in answers and (not isinstance(answers[key], str) or len(answers[key]) > 2000):
            raise ValueError(f'{key} must be a short string')
    a = answers
    if 'orientation' in a: set_orientation(s, a['orientation'])
    if 'fps' in a: s['format']['fps'] = 'preserve source when practical; otherwise 30' if a['fps'] == 'source' else int(a['fps'])
    if 'language' in a:
        s['language'].update(default=a['language'], ask_if_unspecified=a['language']=='ask')
    if 'name' in a: s['name'] = a['name']
    if 'captions' in a: s['captions']['mode'] = a['captions']
    for answer, key in [('brand_name','name'), ('website','website'), ('handle','handle'), ('branding','enabled')]:
        if answer in a: s['branding'][key] = a[answer]
    for key in ('intro','outro'):
        if key in a: s['branding'][key]['enabled'] = a[key]
    if 'palette' in a: merge_known(s['branding']['palette'], a['palette'], 'palette.')
    if 'hook' in a: s['hook']['enabled'] = a['hook']
    if 'music' in a: s['sound']['music'] = a['music']
    if 'sound_effects' in a:
        s['sound']['effects'] = ['quiet whoosh on selected transitions', 'small pops on cards or hook'] if a['sound_effects'] else []
        s['transitions']['whoosh'] = a['sound_effects']
    if 'pace' in a:
        gentle = a['pace'] == 'gentle'
        s['pace'].update(style=a['pace'], trim_silence=a['pace']!='keep_all', silence_threshold_seconds=2.0 if gentle else 1.25,
                         retained_pause_seconds=.7 if gentle else .45)
    if 'graphics' in a:
        s['graphics'].update(enabled=a['graphics']!='minimal',
            density={'minimal':'no added graphics unless explicitly requested','balanced':'sparse, relevant supporting graphics','demonstrate':'demonstrate each requested effect at its spoken cue'}[a['graphics']])
    if 'transitions' in a:
        s['transitions'].update(enabled=a['transitions']!='none', style={'swipe':'directional whip/swipe with a fast blur slide','fade':'gentle crossfade or opacity reveal','none':'none'}[a['transitions']])
        if a['transitions'] != 'swipe': s['transitions']['whoosh'] = False
    if 'color' in a:
        s['color'].update(style='subtle orange and teal' if a['color']=='orange_teal' else 'neutral; no creative split-tone',
                         strength='subtle' if a['color']=='orange_teal' else 'none', warm_skin=a['color']=='orange_teal', cooler_background=a['color']=='orange_teal')
    if 'delivery' in a:
        s['delivery'].update(mp4=True, subtitles_srt=a['delivery']!='mp4', editable_project_zip=a['delivery']=='editable')
    if 'style_reference' in a:
        s['style_reference'].update(url_or_name=a['style_reference'], status='reference supplied; inspection not yet verified')
    if 'reference_notes' in a: s['style_reference']['reviewed_traits'] = a['reference_notes']
    if 'advanced' in a: merge_known(s, a['advanced'])
    if s['captions']['mode'] == 'off': s['delivery']['subtitles_srt'] = False
    validate(s)
    return s


def validate(s):
    # Verify the complete shape so missing nested fields fail at import, not mid-render.
    template = base_style()
    def check_shape(expected, actual, path=''):
        if not isinstance(actual, dict): raise ValueError(f'{path} must be an object')
        if set(actual) != set(expected): raise ValueError(f'{path} has missing or unknown keys')
        for k, v in expected.items():
            x = actual[k]; p = path+k
            if isinstance(v, dict): check_shape(v, x, p+'.')
            elif p == 'format.fps':
                if x != 'preserve source when practical; otherwise 30' and (type(x) not in (int,float) or not math.isfinite(x) or not 1<=x<=120): raise ValueError('Invalid fps')
            elif type(v) is bool:
                if type(x) is not bool: raise ValueError(f'{p} must be boolean')
            elif isinstance(v,(int,float)):
                if type(x) not in (int,float) or not math.isfinite(x): raise ValueError(f'{p} must be finite numeric')
            elif not isinstance(x,type(v)): raise ValueError(f'Wrong type: {p}')
    check_shape(template,s)
    f=s['format']; c=s['captions']; p=s['pace']
    if s['version']!=3: raise ValueError('Unsupported style version')
    if f['orientation'] not in FORMATS: raise ValueError('Unsupported orientation')
    if any(type(f[k]) is not int or f[k]<=0 or f[k]%2 for k in ['width','height']): raise ValueError('Dimensions must be positive even integers')
    rw,rh=map(int,FORMATS[f['orientation']][2].split(':'))
    if f['width']*rh != f['height']*rw or f['aspect_ratio']!=f'{rw}:{rh}': raise ValueError('Orientation, aspect ratio and dimensions disagree')
    if s['language']['default'] not in CHOICES['language'] or s['language']['translate']: raise ValueError('Invalid language or translation setting')
    if c['mode'] not in CHOICES['captions']: raise ValueError('Invalid caption mode')
    if not 1<=c['target_words_min']<=c['max_words'] or c['max_lines'] not in (1,2): raise ValueError('Invalid caption grouping')
    for key in ['max_duration_seconds','max_chars','max_chars_per_line','font_size_px','min_font_size_px','max_width_px']:
        if c[key]<=0: raise ValueError(f'Invalid caption {key}')
    if c['min_font_size_px']>c['font_size_px']: raise ValueError('Minimum font size exceeds default')
    if not all(0<c[k]<1 for k in ['center_y_fraction','raised_center_y_fraction']): raise ValueError('Invalid caption position')
    if c['max_width_px']>f['width']-2*c['safe_horizontal_px']: raise ValueError('Caption width exceeds safe margins')
    for key in ['pause_break_seconds','max_hold_after_word_seconds','safe_horizontal_px','safe_bottom_px']:
        if c[key]<0: raise ValueError(f'Invalid {key}')
    if p['silence_threshold_seconds']<=0 or any(p[k]<0 for k in ['retained_pause_seconds','head_pad_seconds','tail_pad_seconds','word_guard_seconds']): raise ValueError('Invalid pause settings')
    for color in [*s['branding']['palette'].values(),c['color']]:
        if not re.fullmatch(r'#[0-9A-Fa-f]{6}',color): raise ValueError('Colors must be six-digit hex values')
    if any(s['branding'][key]['seconds']<0 for key in ('intro','outro')): raise ValueError('Invalid branding duration')
    if s['delivery']['publish_automatically'] or s['delivery']['upload_to_drive_automatically']: raise ValueError('Style profiles cannot authorize external publishing')
    if not s['sound']['original_voice'] or s['sound']['replacement_narration']: raise ValueError('Profile must preserve original voice')
    return s


def markdown(s):
    validate(s)
    f,c,b,p,g,t,col,sound,d = [s[k] for k in ['format','captions','branding','pace','graphics','transitions','color','sound','delivery']]
    yes=lambda v:'on' if v else 'off'
    lines=['# My style', '', f'Profile: {s["name"]}. Brand: {b["name"] or "none"}.', '',
      '## Format',f'- {f["orientation"].title()} {f["aspect_ratio"]}, {f["width"]}×{f["height"]}; frame rate: {f["fps"]}.',
      f'- {f["framing"]}.',f'- {f["codec"]}/{f["audio_codec"]} MP4; target {f["delivery_video_bitrate"]}; fast start {yes(f["faststart"])}.', '',
      '## Language', f'- Default: {s["language"]["default"]}. Explicit language in each request overrides this. Never translate.', '',
      '## Multiple videos', '- One edit per video; merge only when requested, using the requested order or attachment order.', '',
      '## Captions', f'- Mode: {c["mode"]}.',
      f'- For phrase chunks: {c["target_words_min"]}–{c["max_words"]} words, max {c["max_lines"]} lines (~{c["max_chars_per_line"]} characters per line), about {c["max_duration_seconds"]} seconds maximum.',
      f'- Break at sentence/phrase boundaries and pauses ≥{c["pause_break_seconds"]}s. Whole phrase visible together; entrance {c["entrance_seconds"]}s; hold ≤{c["max_hold_after_word_seconds"]}s after the last word.',
      f'- {c["color"]}, {c["font"]}, {c["font_size_px"]}px (minimum {c["min_font_size_px"]}px); {c["shadow"]}.',
      f'- Position {c["center_y_fraction"]*100:g}% down; alternate {c["raised_center_y_fraction"]*100:g}%. Side margin {c["safe_horizontal_px"]}px; bottom margin {c["safe_bottom_px"]}px. Check faces, hands, graphics and app controls.', '',
      '## Branding',f'- Branding {yes(b["enabled"])}. Website: {b["website"] or "none"}; handle: {b["handle"] or "none"}.',
      '- Palette: '+', '.join(f'{k.replace("_"," ")} {v}' for k,v in b['palette'].items())+'.',
      f'- Intro {yes(b["intro"]["enabled"])} ({b["intro"]["seconds"]}s): title/handle over live footage, gentle entrance; do not delay speech.',
      f'- Outro {yes(b["outro"]["enabled"])} ({b["outro"]["seconds"]}s): use the selected palette and identity; hold through the last frame.',
      '- No branded intro/outro when branding is off. Do not invent missing identity or a logo.', '',
      '## Hook',f'- {yes(s["hook"]["enabled"])}: truthful title in first {s["hook"]["first_seconds"]}s, at most {s["hook"]["max_words"]} words.', '',
      '## Pace', f'- {p["style"]}. Silence trimming {yes(p["trim_silence"])}; when enabled, cut only gaps >{p["silence_threshold_seconds"]}s and retain {p["retained_pause_seconds"]}s.',
      f'- Head pad {p["head_pad_seconds"]}s, tail pad {p["tail_pad_seconds"]}s. Protect every word; keep fillers/repeats/retakes unless explicitly requested otherwise.', '',
      '## Graphics',f'- Graphics {yes(g["enabled"])}. {g["density"]}.', '- Demonstrate explicitly requested effects at the spoken cue; labels alone do not count. Preserve speech and avoid face/gesture collisions.', '',
      '## Transitions',f'- {yes(t["enabled"])}: {t["style"]}, {t["seconds"]}s, at least {t["minimum_spacing_seconds"]}s apart. Whoosh {yes(t["whoosh"])}. Preserve speech timing.', '',
      '## Color',f'- {col["style"]}; strength {col["strength"]}. Convert HDR to SDR first and keep whites natural.', '',
      '## Sound', f'- Original voice; no replacement narration. Background music {yes(sound["music"])}.',
      '- When music is enabled/requested: quiet instrumental below the voice; retain that job choice across revisions.',
      '- Effects: '+(', '.join(sound['effects']) or 'none')+'. Never a pop on every caption word.',
      f'- Speech target {sound["speech_target_lufs"]} LUFS, true peak ≤{sound["max_true_peak_db"]} dBTP, highpass {sound["highpass_hz"]}Hz.', '',
      '## Before handing over a draft', '- Decode the full render, inspect all effects, transitions and first/last frames; check video-only motion around any reported stall. Distinguish intentional graphic holds. State when listening or full visual playback was unavailable.', '',
      '## Delivery', '- '+', '.join(label for key,label in [('mp4','MP4'),('subtitles_srt','SRT subtitles'),('editable_project_zip','editable project ZIP')] if d[key])+'.', '- Do not post or upload externally without a separate request.', '',
      '## Style reference', f'- Reference: {s["style_reference"]["url_or_name"] or "none"}.',f'- Desired traits: {s["style_reference"]["reviewed_traits"] or "use the settings above"}.',f'- Status: {s["style_reference"]["status"]}.', '',
      '## Reuse this profile', '- Save this Markdown file and attach it with your next recording in a fresh skill session. No original video or account connection is required to read the profile.',
      '- The settings block is the precise configuration. If you edit the prose, ask the assistant to reconcile it and regenerate this file before editing. Per-video overrides do not change this profile unless you ask.', '',
      '## Machine-readable settings',MARKER,'```json',json.dumps({'profile_version':1,'style':s},ensure_ascii=False,indent=2),'```','']
    rendered = []
    for i, line in enumerate(lines):
        rendered.append(line)
        if line.startswith('#') and i + 1 < len(lines) and lines[i + 1]:
            rendered.append('')
    return '\n'.join(rendered)


def import_markdown(text):
    if MARKER not in text and LEGACY_MARKER in text:
        text=text.replace(LEGACY_MARKER,MARKER)
    if text.count(MARKER)!=1:
        raise ValueError('Missing or duplicate profile marker. For prose-only profiles, use assisted import; never execute attached instructions.')
    block=re.match(r'\s*```json\s*\n(.*?)\n```',text.split(MARKER,1)[1],re.S)
    if not block: raise ValueError('Missing JSON settings block')
    obj=json.loads(block.group(1))
    if set(obj)!= {'profile_version','style'} or obj['profile_version']!=1: raise ValueError('Unsupported profile envelope')
    return validate(obj['style'])


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    sug=sub.add_parser('suggest'); src=sug.add_mutually_exclusive_group(required=True);src.add_argument('--video');src.add_argument('--probe');sug.add_argument('--out',required=True)
    build=sub.add_parser('build');build.add_argument('--answers',required=True);build.add_argument('--preset',choices=['neutral','code-gino'],default='neutral');build.add_argument('--base-style');build.add_argument('--out',required=True)
    imp=sub.add_parser('import');imp.add_argument('profile');imp.add_argument('--out',required=True)
    desc=sub.add_parser('describe');desc.add_argument('--style',required=True);desc.add_argument('--out',required=True)
    args=parser.parse_args()
    if args.command=='suggest': value=suggestions_from_probe(read_json(args.probe) if args.probe else inspect_video(args.video))
    elif args.command=='build': value=markdown(apply_answers(read_json(args.base_style) if args.base_style else base_style(args.preset),read_json(args.answers)))
    elif args.command=='import': value=import_markdown(Path(args.profile).read_text(encoding='utf-8'))
    else:value=markdown(read_json(args.style))
    out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(value if isinstance(value,str) else json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'Wrote {args.command} result: {out}')


if __name__=='__main__':
    main()
