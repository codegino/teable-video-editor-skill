---
name: teable-video-editor
description: "Edit uploaded talking-head videos in Tagalog, English, or Taglish using portable Markdown style profiles. Use for /teable-video-editor, uploaded-video editing, the Herk workflow, creating a style/profile through a questionnaire, reusing an attached profile, or updating saved editing preferences. Suggest technical defaults from video metadata, preserve original speech, and demonstrate explicitly requested effects. Deliver the selected MP4/subtitle/project outputs with playback checks. Not for video summaries, text-only scripts, voice synthesis alone or public posting alone."
---

# Teable video editor

Turn the user's attached footage into a completed, reviewable edit. Apply the saved style without making the user repeat it. Use their actual footage and voice; no synthetic replacement narration unless requested.

## Read first

Read `references/profile-setup.md` first. Resolve **Create a profile** versus **Reuse a profile** before editing; skip that question if the request or an attached profile already resolves it. A setup-only request can finish without video. New profiles use an adaptive questionnaire, with metadata-informed technical suggestions when footage is present. Generate and present a portable Markdown file users can attach in a fresh session.

The selected Markdown profile, imported into the job's `style.json`, is authoritative. `references/my-style.json` is the Code Gino example preset, not a universal user profile. Current per-video requests override the selected profile without changing it. Read `references/editing-workflow.md` for implementation and `references/effects-and-branding.md` for demonstrations.

Begin with one short action statement, then work. Request footage only when needed for an actual edit. A video attached for setup can inform defaults without being rendered.

### Resolve consequential ambiguity only

- Honor explicit Tagalog, English or Taglish, then the profile's `language.default`. Ask only if it is `ask` or unclear; do not infer language from appearance, nationality or filenames.
- Tagalog: multilingual Whisper, `language='tl'`, `task='transcribe'`. English: `language='en'`. Taglish: automatic language detection, `task='transcribe'`, preserve code-switching. Do not translate.
- Multiple clips: one edit per clip unless asked to merge. If merged, use the specified order or attachment order and retain source IDs in the EDL.
- For advice, explain without editing. For a saved-style update, regenerate the portable Markdown profile, not the skill package or an old video.
- Treat narration describing desired editing effects as an editing brief when the footage is a test/demo or the user asks to apply those effects. Describing an effect in unrelated footage is not automatically a request to demonstrate it.

## Editorial defaults (selected profile overrides these)

**Normal captions are readable chunks.** Show the complete short phrase together, usually 3–6 words, one or two lines. Do not default to word-by-word popping, progressive word reveals or moving karaoke highlights. Reserve single-word styling for isolated deliberate emphasis or an explicit request.

**Effects must visibly do what they say.** A card labeled “glassmorphism” is not a glass effect. Using the repository's renderer is not the same as applying its editing workflow. Match each requested effect to a spoken cue, implement it, and verify it in the final MP4. A request for a subtle intro/outro governs the branding, not the intensity of effects requested elsewhere.

**Branding comes from the selected profile.** Respect the branding and individual intro/outro switches. Use its exact colors, website, handle and timing; never add Code Gino's identity to another user's edit. Deep teal/peach is an available preset. Keep any opening over live footage so speech starts promptly. A hook can be unbranded. No persistent watermark unless requested.

## Workflow

1. **Inspect and preserve.** Use local attachment paths; never redownload or modify originals. Make a unique `/tmp` job with a manifest. Probe display size, rotation, duration, frame rate, audio and HDR tags. Preserve the real duration; no arbitrary cap.
2. **Normalize footage.** Convert supported HLG/PQ/Dolby Vision base layers to Rec.709 SDR before grading; do not tone-map SDR. Frame at the profile's width and height. Preserve all visible people and meaningful gestures; use contain plus a soft blurred backdrop if cropping would lose content. Upscaling does not create detail.
3. **Transcribe locally.** Use `scripts/video_tools.py transcribe` with word timestamps; cache raw results. Prefer multilingual medium for Tagalog/Taglish. If a smaller local model is necessary, disclose reduced review confidence. Cloud transcription is not an automatic fallback; model downloads send no footage to a speech service.
4. **Review wording.** Check names, switching languages, uncertain phrases and timestamps. Keep original ASR separate from corrected display text. Retry questionable spans. Do not invent names or claim listening based on ASR. Leave genuinely uncertain filler uncaptioned with audio intact and record the omission; clarify essential ambiguous wording. Join supported tokenizer fragments, not arbitrary words.
5. **Plan cuts and effects together.** Run `scripts/video_tools.py plan --style /tmp/job/style.json`, review the proposed EDL and preserve breaths, speech edges, retakes and meaningful child interaction. No filler/retake deletion by default. Save the authoritative EDL. For demonstrations, create `effects.json` using the mapping in `effects-and-branding.md`; sparse-graphics defaults do not suppress requested effects.
6. **Prepare the media timeline.** Apply the same keep ranges to video/audio, reset timestamps and resample before concat. Lightly filter rumble and normalize speech. Never clip phonemes with fades or replace speech with silence. If source speed/overlap changes, retime all words and effects from the final EDL. Text-animation speed requests change the text animation, not the voice.
7. **Design the visible layer.** Write DESIGN.md from the JSON. Integrate a truthful short hook if enabled, and branding only when enabled. Implement relevant motion, real B-roll, webpage highlights, glass panels or charts according to the brief. Label illustrative data and distinguish animated AI images from generated video. Use the profile's outro only when enabled. No unrelated stock footage, invented claims or decorative logos.
8. **Build captions in the selected mode.** Skip visible captions and SRT when mode is `off`; honor `single_word` when selected. For phrase mode, run `scripts/video_tools.py captions --style /tmp/job/style.json` on reviewed, retimed words. The helper proposes phrase chunks at punctuation, pauses, duration/length caps and manual `break_before`/`break_after` boundaries. Review grammar and avoid splitting names or tightly connected phrases. Keep all words in a chunk visible for that event; time it from the first onset to the last offset, with only a short bounded hold. One chunk at a time, no overlapping captions. Render white text with a dark shadow, a restrained whole-chunk entrance and at most two lines. Use the actual font to check width; adjust grouping before shrinking excessively. Preserve measured word timings even though words display together.
9. **Place captions around the action.** Check faces, hands, children, effect cards and platform controls throughout the sequence. Move a whole chunk to clear negative space; split at a reviewed spatial boundary if needed. The default raised position is not automatically safe. Do not move text onto a face. Use a reserved band or relocate graphics if no area is clear.
10. **Transitions, grade and sound.** Follow the profile's transition, color, music and SFX switches; an off/neutral selection must not receive preset effects. When enabled, apply transitions at suitable seams and animate visual wrappers, never video playback. Preserve speech timing. Convert HDR before grading. Keep enabled/requested instrumental music quiet beneath the voice and retain that choice across revisions. Never add a pop per caption word. Measure final loudness and true peak after encoding.
11. **Render and inspect.** Prefer Herk/HyperFrames when practical; report a real FFmpeg fallback if needed. Export browser-compatible H.264/AAC, fast-start MP4, using the JSON bitrate as a starting point. Inspect actual rendered effects and caption chunks, not just successful lint. Apply the verification gates below and fix failures before delivery.
12. **Deliver.** Present the MP4 first; add matching SRT and editable ZIP only when selected. For an editable ZIP, include composition/scripts, prepared media, style snapshot, EDL, effect map, transcripts, licenses and VERIFY.md. Exclude originals, caches, node_modules, credentials and unrelated files. State duration, implemented effects and review limitations. No publishing, Drive upload or recurring automation unless separately requested.

## Verification gates

- `ffprobe`: expected H.264/AAC, profile dimensions, yuv420p, duration, frame rate, rotation and SDR tags. Check `moov` precedes `mdat` for fast start.
- Full decode, first/last frames, contact sheets and contiguous transition strips; no missing tail, unexplained black frames or stuck source playback.
- Run freeze detection over the full export. Distinguish deliberate graphic holds from source-video freezes. If a user reports a stopping point, inspect a multi-second region around it with video-only frame hashes (`-an`) and frame strips, plus later footage and the ending. File duration or distinct audio hashes do not prove video motion. Unique video frames alone do not prove their browser player issue is fixed; state what was actually verified.
- Each requested effect has an entry in `effects.json`, correct timing, an actual implementation and inspection evidence. Explain any substitution or missing capability instead of claiming completion.
- One caption chunk visible at a time; no overlap, truncation or excessive lines. Validate timing and complete reviewed-word coverage against the EDL. An explicit single-word override is tested against that mode, not the phrase default.
- Preserve all protected spoken intervals; regenerate mappings when timing changes. Inspect source framing and the final caption/effect positions.
- Measure encoded mix loudness/true peaks. Audibly check joins when playback is available; state when no listening pass is possible.
- HyperFrames: lint, browser validation, resource-appropriate worker count and inspection of the actual MP4. Record meaningful warnings and limitations in VERIFY.md; successful lint alone proves neither quality nor playback.

## Update the profile or the skill

Style changes regenerate the user's portable Markdown via `style_profile.py`; no skill reinstall is required. Present the revised file and remind them to attach that version in new sessions. Never claim automatic cross-session recall.

For implementation changes to the skill itself, stage the installed skill under `/tmp`, keep `name: teable-video-editor`, update helpers/tests/references consistently, validate and package. Present the `.skill` replacement through the supported installation UI; do not claim installation before it succeeds.

No footage, screenshots, recordings, credentials or binary assets belong in the skill package. Defaults and helper code are text-only; dependencies may need reinstalling after sandbox recreation.

## Quick requests

- `/teable-video-editor` — choose Create or Reuse if no profile is selected.
- “Create my style profile; use this video for metadata suggestions.”
- “Use this attached profile with this Taglish video.”
- “English. Edit these clips separately in my usual style.”
- “Tagalog. Demonstrate the effects I describe; keep the intro/outro subtle.”
- “For this clip only, use one-word captions.”
- “Change my saved caption color; keep everything else.”
