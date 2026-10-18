# Contributing

This skill targets Teable's AI chat, sandbox tools, attachments and skill installation flow. End users need a
Teable account; the commands below are for maintaining the repository.

## Design

The skill is a thin layer over [Herk Edit Kit](https://github.com/nateherkai/herk-edit-kit), modeled on
[free247editor](https://github.com/riecodes/free247editor):

- `scripts/setup.mjs` clones the engine at a pinned commit into `<workspace>/engine` and runs `npm ci`.
- `scripts/transcribe.py` replaces the engine's ElevenLabs step with local faster-whisper, writing the engine's
  `{audio_duration_secs, words: [{text, start, end}]}` transcript shape.
- `SKILL.md` covers setup, the style questionnaire, which engine skill to follow, and turning notes into rules.
  Editing technique lives in the engine; do not re-specify it here.
- The user's profile is plain Markdown they keep and reattach. `examples/code-gino.md` is an example only.

Bump `ENGINE_COMMIT` in `setup.mjs` deliberately, after an edit on the new revision.

## Package

```sh
node --check scripts/setup.mjs
python -m py_compile scripts/transcribe.py
python tools/package_skill.py
```

Commit the refreshed `dist/teable-video-editor.skill` alongside source changes. The package builder uses an
explicit file allowlist; update it when adding skill files.

Do not commit real recordings, transcripts, screenshots, credentials or private profiles. Keep
`name: teable-video-editor` stable so an update can replace an existing installation.
