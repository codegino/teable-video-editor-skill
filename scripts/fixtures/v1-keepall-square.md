# My style

Profile: Keep. Brand: none.

## Format

- Square 1:1, 1080×1080; frame rate: preserve source when practical; otherwise 30.
- preserve subjects; contain with blurred backdrop when a crop would lose content.
- h264/aac MP4; target 5M; fast start on.

## Language

- Default: english. Explicit language in each request overrides this. Never translate.

## Multiple videos

- One edit per video; merge only when requested, using the requested order or attachment order.

## Captions

- Mode: off.
- For phrase chunks: 3–6 words, max 2 lines (~34 characters per line), about 3.0 seconds maximum.
- Break at sentence/phrase boundaries and pauses ≥0.45s. Whole phrase visible together; entrance 0.12s; hold ≤0.18s after the last word.
- #FFFFFF, locally licensed bold sans-serif, 54px (minimum 36px); 0 4px 12px rgba(0,0,0,0.8).
- Position 76% down; alternate 66%. Side margin 90px; bottom margin 113px. Check faces, hands, graphics and app controls.

## Branding

- Branding off. Website: none; handle: none.
- Palette: background #102B2D, accent #EFA269, secondary accent #2B8F96, primary text #FFFFFF, secondary text #C4D9D9.
- Intro off (2.5s): title/handle over live footage, gentle entrance; do not delay speech.
- Outro off (1.8s): use the selected palette and identity; hold through the last frame.
- No branded intro/outro when branding is off. Do not invent missing identity or a logo.

## Hook

- off: truthful title in first 3.0s, at most 7 words.

## Pace

- keep_all. Silence trimming off; when enabled, cut only gaps >1.25s and retain 0.45s.
- Head pad 0.3s, tail pad 0.5s. Protect every word; keep fillers/repeats/retakes unless explicitly requested otherwise.

## Graphics

- Graphics off. no added graphics unless explicitly requested.
- Demonstrate explicitly requested effects at the spoken cue; labels alone do not count. Preserve speech and avoid face/gesture collisions.

## Transitions

- on: gentle crossfade or opacity reveal, 0.2s, at least 3.0s apart. Whoosh off. Preserve speech timing.

## Color

- subtle orange and teal; strength subtle. Convert HDR to SDR first and keep whites natural.

## Sound

- Original voice; no replacement narration. Background music off.
- When music is enabled/requested: quiet instrumental below the voice; retain that job choice across revisions.
- Effects: quiet whoosh on selected transitions, small pops on cards or hook. Never a pop on every caption word.
- Speech target -16 LUFS, true peak ≤-1.5 dBTP, highpass 70Hz.

## Before handing over a draft

- Decode the full render, inspect all effects, transitions and first/last frames; check video-only motion around any reported stall. Distinguish intentional graphic holds. State when listening or full visual playback was unavailable.

## Delivery

- MP4.
- Do not post or upload externally without a separate request.

## Style reference

- Reference: none.
- Desired traits: use the settings above.
- Status: not supplied.

## Reuse this profile

- Save this Markdown file and attach it with your next recording in a fresh skill session. No original video or account connection is required to read the profile.
- The settings block is the precise configuration. If you edit the prose, ask the assistant to reconcile it and regenerate this file before editing. Per-video overrides do not change this profile unless you ask.

## Machine-readable settings

<!-- teable-video-editor-profile:v1 -->
```json
{
  "profile_version": 1,
  "style": {
    "version": 3,
    "name": "Keep",
    "format": {
      "orientation": "square",
      "aspect_ratio": "1:1",
      "width": 1080,
      "height": 1080,
      "platforms": [
        "social feed"
      ],
      "framing": "preserve subjects; contain with blurred backdrop when a crop would lose content",
      "fps": "preserve source when practical; otherwise 30",
      "codec": "h264",
      "audio_codec": "aac",
      "pixel_format": "yuv420p",
      "faststart": true,
      "delivery_video_bitrate": "5M",
      "delivery_bitrate_policy": "1080p30 starting point; increase if real output loses detail, never sacrifice legibility to hit a size"
    },
    "language": {
      "ask_if_unspecified": false,
      "supported": [
        "tagalog",
        "english",
        "taglish"
      ],
      "translate": false,
      "transcription": "local multilingual faster-whisper",
      "model": "medium",
      "default": "english"
    },
    "multiple_videos": {
      "default": "separate outputs",
      "merge_only_when_requested": true,
      "merge_order": "user order, otherwise attachment order"
    },
    "captions": {
      "mode": "off",
      "target_words_min": 3,
      "max_words": 6,
      "max_chars": 64,
      "max_lines": 2,
      "max_chars_per_line": 34,
      "max_duration_seconds": 3.0,
      "pause_break_seconds": 0.45,
      "sentence_breaks": ".!?…",
      "phrase_breaks": ",;:",
      "manual_boundaries": "reviewed per-word break_before/break_after flags",
      "animation": "whole-chunk gentle fade/slide; all words visible together",
      "entrance_seconds": 0.12,
      "single_word_emphasis": "occasional deliberate emphasis or an explicit per-job request, never the whole default edit",
      "pop_seconds": 0.09,
      "pop_scale_from": 0.86,
      "color": "#FFFFFF",
      "shadow": "0 4px 12px rgba(0,0,0,0.8)",
      "background": "none by default; subtle dark scrim only if needed for legibility",
      "font": "locally licensed bold sans-serif",
      "font_size_px": 54,
      "min_font_size_px": 36,
      "max_width_px": 900,
      "position": "lower third",
      "center_y_fraction": 0.76,
      "raised_center_y_fraction": 0.66,
      "adaptive_position": true,
      "avoid": [
        "faces",
        "hands",
        "gestures",
        "graphics",
        "platform controls"
      ],
      "safe_horizontal_px": 90,
      "safe_bottom_px": 113,
      "max_hold_after_word_seconds": 0.18
    },
    "branding": {
      "enabled": false,
      "website": "",
      "handle": "",
      "palette": {
        "background": "#102B2D",
        "accent": "#EFA269",
        "secondary_accent": "#2B8F96",
        "primary_text": "#FFFFFF",
        "secondary_text": "#C4D9D9"
      },
      "intro": {
        "seconds": 2.5,
        "mode": "brief title and handle over live footage; no delay to speech",
        "motion": "gentle fade/slide",
        "enabled": false
      },
      "outro": {
        "seconds": 1.8,
        "mode": "deep-teal card, thin peach accent line, white website, muted pale-teal handle",
        "motion": "gentle reveal; hold readable through final frame",
        "enabled": false
      },
      "scope": "subtle branding applies to intro/outro, not to the strength of requested effects",
      "name": ""
    },
    "hook": {
      "enabled": false,
      "first_seconds": 3.0,
      "style": "short readable title integrated with the branded opening",
      "content": "short truthful hook derived from spoken content",
      "max_words": 7
    },
    "pace": {
      "style": "keep_all",
      "silence_threshold_seconds": 1.25,
      "retained_pause_seconds": 0.45,
      "head_pad_seconds": 0.3,
      "tail_pad_seconds": 0.5,
      "word_guard_seconds": 0.1,
      "trim_leading_trailing_only_when_long": true,
      "delete_filler_words": false,
      "delete_repetitions_or_retakes": false,
      "never_cut_words": true,
      "trim_silence": false
    },
    "graphics": {
      "enabled": false,
      "style": "transcript-timed visual demonstrations, motion graphics and frosted-glass panels when relevant",
      "density": "no added graphics unless explicitly requested",
      "spoken_effects_are_brief": true,
      "effect_manifest_required": true,
      "labels_are_not_demonstrations": true,
      "speed_change_target": "infer from nearby speech: text motion, B-roll, or source; preserve spoken meaning and retime if source changes",
      "avoid_covering_faces_or_gestures": true,
      "avoid_unrelated_broll": true,
      "no_forced_branding": true
    },
    "transitions": {
      "enabled": true,
      "style": "gentle crossfade or opacity reveal",
      "seconds": 0.2,
      "where": [
        "suitable trimmed pauses",
        "clear new thoughts",
        "requested effect demonstrations"
      ],
      "minimum_spacing_seconds": 3.0,
      "preserve_speech_timing": true,
      "whoosh": false
    },
    "color": {
      "style": "subtle orange and teal",
      "warm_skin": true,
      "cooler_background": true,
      "orange": "#EFA269",
      "teal": "#2B8F96",
      "strength": "subtle",
      "hdr_to_sdr_first": true,
      "sdr_primaries": "bt709",
      "preserve_natural_whites": true
    },
    "sound": {
      "original_voice": true,
      "replacement_narration": false,
      "music": false,
      "music_when_requested": "quiet instrumental, ducked below voice; preserve the request across revisions of that video",
      "effects": [
        "quiet whoosh on selected transitions",
        "small pops on cards or hook"
      ],
      "pop_every_caption_word": false,
      "effects_relative_to_speech_db": -16,
      "speech_target_lufs": -16,
      "max_true_peak_db": -1.5,
      "highpass_hz": 70
    },
    "verification": {
      "full_decode": true,
      "freeze_detection": true,
      "distinguish_intentional_graphic_holds": true,
      "reported_stall_check_window_seconds": 4,
      "video_only_frame_hashes": true,
      "inspect_each_effect": true,
      "inspect_contiguous_transition_frames": true
    },
    "delivery": {
      "mp4": true,
      "subtitles_srt": false,
      "editable_project_zip": false,
      "publish_automatically": false,
      "upload_to_drive_automatically": false
    },
    "style_reference": {
      "url_or_name": "",
      "reviewed_traits": "",
      "status": "not supplied"
    }
  }
}
```
