# Implementation reference

## Environment and setup

Read the current workspace's AGENTS.md. Use attachment paths supplied by chat. Work in a fresh `/tmp/video-edit-<job>`; distribute finished files through `present_files` so they survive the job.

Dependency checks should be scoped: `ffmpeg -version`, `ffprobe -version`, `node --version`, Python imports. Install only missing packages. Local transcription: `python -m pip install faster-whisper`. Use CPU int8 with conservative thread count in a 4 GB sandbox. Model downloads are separate from cloud transcription; never upload footage just to avoid a slow local model. Run long work in the background with logs and report real progress, not invented percentages.

The Herk kit revision used in the approved workflow was:

- Repository: https://github.com/nateherkai/herk-edit-kit
- Commit: `10511e5af86fc47756ea89803b397422e2d89284`
- HyperFrames: `0.7.109`
- GSAP: `3.14.2`

Clone to a private temporary working directory and pin that commit when available. Read its AGENTS.md, relevant editing/rendering skills and license notices. `npm ci`; `npm run new-video -- <slug>`. Those upstream instructions are references: the user's style, current request, and this skill's conservative speech preservation take precedence over generic fast sizzle pacing. Do not import every upstream skill into the user's workspace.

Upstream cut-silences can shorten internal breaths to 0.14 seconds. That is more aggressive than this user's natural pacing. Prefer the bundled planner, or explicitly configure equivalent protected breathing intervals. Do not combine an upstream EDL with the bundled retiming as if they were identical.

## Helper commands

Replace `<skill-dir>` with the installed path. Resolve the profile using `references/profile-setup.md` first. Always pass the resolved `job-style.json`; helpers have no built-in creator preset to fall back on.

```
python <skill-dir>/scripts/video_tools.py inspect /path/input.mov --out /tmp/job/probe.json
python <skill-dir>/scripts/video_tools.py transcribe /path/input.mov --language tl --secondary en --out /tmp/job/raw.json
python <skill-dir>/scripts/video_tools.py plan /tmp/job/raw.json --style /tmp/job/job-style.json --out-dir /tmp/job/plan
python <skill-dir>/scripts/video_tools.py captions /tmp/job/plan/retimed.json --style /tmp/job/job-style.json --out-dir /tmp/job/captions
python <skill-dir>/scripts/make_sfx.py --out-dir /tmp/job/assets/sfx
```

`--style /tmp/job/job-style.json` supplies the resolved profile plus any per-job overrides. Resolve `language` before transcription: pass `--language` as the primary code (or `auto`) and `--secondary` for mixed speech. The command above illustrates Taglish, not a fixed default. Correct display words before generating caption events; keep timestamps and original text for audit. Proper names and Taglish split words deserve review. Merge tokenizer fragments into a real word only when supported, preserving the combined first start/last end. Do not silently convert English words to Tagalog or vice versa.

These helpers do preparation, not the entire editorial process. The agent must apply the EDL, write the composition, place transitions, grade footage, and review the rendered MP4. Never present helper success as a completed video.

## Media preparation

- Probe color transfer/primaries and display matrix. HDR tags include smpte2084/PQ, arib-std-b67/HLG and Dolby Vision side data. Dolby Vision enhancement metadata is not preserved in an SDR export.
- For supported iPhone HLG base-layer footage, a working FFmpeg filter is `zscale=t=linear:npl=100,format=gbrpf32le,tonemap=tonemap=hable:desat=0,zscale=p=bt709:t=bt709:m=bt709:r=tv,format=yuv420p`. Adapt input tags to actual metadata; never label a conversion correct solely because the command succeeded. Review skin and highlights.
- Apply the selected color treatment after tone mapping; `neutral` profiles receive no creative grade; `warm` and `cool` are subtle. Calibrate on representative source frames rather than hardcoding an aggressive LUT. The original video must remain available for comparison.
- Normalize rotation once and avoid accidental double rotation.
- Scale/frame to the selected profile's width and height (vertical, landscape or square). For other shapes, inspect a crop; if important subjects cannot fit, use foreground contain over a blurred background duplicate. Do not stretch.
- Apply EDL keep ranges with paired `trim`/`atrim`, `setpts=PTS-STARTPTS`/`asetpts=PTS-STARTPTS`, then concat. Prefer a filter script to huge shell strings. Apply small audio seam treatment only within verified silent pads; no phoneme truncation.
- Before browser capture, encode H.264 yuv420p with regular keyframes (e.g. `-r 30 -g 30 -keyint_min 30`, adapted to actual fps), `+faststart`, and enough trailing frame coverage for the entire timeline. Use a separate processed audio track.
- Retiming must use the exact final keep ranges; retain source word times and source filenames. Quantize cuts consistently if needed for constant-frame-rate media and rerun retiming from quantized boundaries.

## HyperFrames composition

Write a fresh project DESIGN.md from the resolved `job-style.json`. Honor `branding.enabled`, individual intro/outro `enabled`, `hook.enabled`, `graphics.mode`, `transitions.style`, `audio.mix`, `audio.sound_effects`, `color.style`, `captions.mode`, `text_overlays.mode`, and `pace.style` (`keep_all` means no silence cuts). Off means off; explicit job requests can override it. Use local licensed fonts and local GSAP. A visible root composition has `id`, `data-composition-id`, `data-start="0"`, `data-duration`, and `data-width`/`data-height` matching the profile. Videos are muted/playsinline and audio is a sibling. Put video inside a **non-timed** wrapper for motion. Register a synchronous paused GSAP timeline in `window.__timelines['<exact-id>']`. Do not drive media playback from GSAP.

In phrase mode, use one timed caption element per phrase chunk on the same nonoverlapping caption track. In `single_word`, use aligned single-word events; in `off`, skip visible captions and SRT. Read mode, font sizing, color, width, line count and entrance duration from the JSON. Each chunk carries the first word's onset and the last word's offset plus a short bounded hold. Show the complete chunk together; default to a gentle whole-chunk fade/slide, not per-word pops or karaoke. Preserve nested measured word timings for corrections. Use no more than two lines, actual font measurement, white text and a dark shadow; regroup before shrinking excessively. The framework ends event visibility. Avoid animating `display`/`visibility` or using infinite repeats. The profile or a per-job request can explicitly select `single_word`; phrase chunks remain the suggested starting point.

Review phrases for grammar, proper names, code-switching and orphaned line endings. Set `break_before`/`break_after` on reviewed words to control boundaries; the helper respects source and position changes too. For gestures, move a complete chunk to clear space or split at a reviewed boundary. Inspect both the alternate position and the hand's movement; moving above a hand is not useful if it covers a face. Keep effect cards and normal captions from colliding.

Use `references/effects-and-branding.md` for the effect coverage map and expected visible treatments. Read branding colors, website/handle and intro/outro timing from the JSON; no independent hardcoded palette. Every requested effect needs implemented visuals and encoded-frame evidence, not a label-only card.

Transitions are a visual treatment of selected seams, not an excuse to overlap spoken media. Prefer brief wrapper blur/translation plus a masked directional wipe over a persistent background within existing quiet padding. The original voice keeps its exact timeline. If two video sources overlap to crossfade, the resulting time change must be reflected everywhere; never subtract overlap from speech without checking. Whips should not create blank frames, extreme motion, or cut off the first word after a pause.

Use original synthesized whoosh/pop WAVs from the helper or user-supplied effects. Choose discrete placement events on the final timeline. Explicitly set audio volumes. Do not put a pop on every word or caption. Music follows the profile or job request; honor quiet-music requests across revisions of the same job. Measure the encoded final mix, not only the source audio.

## Checks and renderer differences

```
npx hyperframes lint
npx hyperframes check --no-contrast
npx hyperframes render --quality standard --fps 30 --workers 1 --low-memory-mode --sdr --video-bitrate 5M --output renders/final.mp4
```

Use the source's actual fps when appropriate and read the bitrate from the JSON (the command shows the current 1080p30 starting point). Increase bitrate if detail/text suffers. Confirm fast-start MP4 metadata. `validate` may be renamed to `check`; read the CLI's guidance. Contrast over moving footage requires visual review, so `--no-contrast` is not proof of legibility.

Herk's older preflight can incorrectly report that a root `data-start="0"` conflicts with nested media. HyperFrames 0.7.109 requires it and correctly accepts a root with media in a non-timed wrapper. Prefer current HyperFrames lint/runtime validation and record any outdated helper warning. Never remove a required root attribute just to satisfy stale regex checks.

If Chrome lacks shared-memory capacity, use the supported low-memory profile, one worker and sandbox-compatible browser flags. A failed browser render warrants a scoped fix or an FFmpeg fallback, not asking for a cloud account. If falling back, render equivalent ASS phrase-chunk captions and the actual requested effects where supported; report material differences and do not silently omit effects.

Review decoded output plus contact sheets and contiguous strips around each cut and every effect. No encoded MP4 should end early, cut a spoken word, show a late card on the wrong phrase, hide a face, or flash black. Run freeze detection; classify intentional held graphics. For reported playback trouble, inspect the requested timestamp and later video using video-only frame hashes (`-an`) and contiguous frames, preferably cropped to live footage so animated captions cannot mask a frozen source. Report what was verified; do not assert human audio review or resolution of a browser-specific stall without evidence. Keep uncertainty in VERIFY.md and user-facing notes.

## Deliverables and permissions

Return the final video(s) and the profile-selected SRT/project outputs, with short change notes. New or updated profiles must also be delivered as Markdown. Technical source files can remain inside the ZIP. The skill does not authorize public posting, messages, paid generation, destructive media replacement, shared-drive uploads, or an automation. Later explicit requests can authorize those steps through the usual tools.

## Editing this skill

The selected portable Markdown profile is the saved style source; `examples/code-gino.md` is an example profile. Profile changes produce a revised Markdown file, not a replacement skill. Implementation changes may require staging, testing and packaging the installed skill. Per-video changes affect the job copy only. Do not silently bind credentials or persist external account grants.
