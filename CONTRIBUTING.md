# Contributing

This skill targets Teable's AI chat, sandbox tools, attachments and skill installation flow. End users need a Teable account; the commands below are for maintaining the repository, not using the skill.

## Profile behavior

Keep `SKILL.md`, `references/profile-setup.md`, profile helpers and tests consistent. A selected portable Markdown profile supplies the user's preferences. `references/my-style.json` is the explicitly selected Code Gino example preset, not every new user's identity.

Preserve Create/Reuse routing, setup without video, metadata-assisted defaults, portable profile import, and temporary per-video overrides. Never silently apply Code Gino's branding to a new user.

## Test and package

Helper tests and packaging use Python 3.10+ and the standard library:

```sh
python -m unittest discover -s scripts -p 'test_*.py'
python scripts/style_profile.py build --answers examples/profile-answers.synthetic.json --out /tmp/my-video-style.md
python scripts/style_profile.py import /tmp/my-video-style.md --out /tmp/my-video-style.json
python scripts/video_tools.py captions examples/transcript.synthetic.json --style /tmp/my-video-style.json --out-dir /tmp/caption-demo
python tools/package_skill.py
```

Commit the refreshed `dist/teable-video-editor.skill` alongside source changes. The package builder uses an explicit file allowlist; update it when adding skill resources. GitHub Actions is configured to run tests on Python 3.10–3.12 and compare repeated package builds.

These tests cover helper behavior and portable settings, not visual quality or a complete rendered edit. For actual media work, follow [the editing workflow](references/editing-workflow.md). FFmpeg/ffprobe, optional faster-whisper transcription, and rendering dependencies run in the editing environment; they are not bundled in the repository. See `requirements-transcription.txt` for the optional transcription dependency.

## Review guidelines

For caption changes, preserve aligned word timing and verify phrase boundaries, complete reviewed-word coverage and nonoverlapping events. For rendering guidance, distinguish structural checks from visual inspection and human listening. A label or renderer command does not prove an effect was implemented.

Use synthetic fixtures. Do not commit real recordings, transcripts, screenshots, credentials or private profiles. Keep job assets and their provenance outside this repository. Report unavailable verification honestly.

Keep `name: teable-video-editor` stable so the updated skill can replace an existing installation. (Renamed from `my-video-editor`; existing installs under the old name must be replaced manually. Profiles with the legacy marker still import.)
