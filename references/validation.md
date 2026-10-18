# Validation record — portable profiles (version 3)

Updated 2026-10-18.

## Completed checks

- **39 deterministic tests passed:** 21 existing media-helper tests plus 18 portable-profile tests.
- Profile tests cover Markdown/settings round-trip for vertical, landscape and square, independent-process CLI reuse, no inherited Code Gino identity for new users, explicit preset reuse, rotated phone footage, HDR/audio/fps metadata, invalid and incomplete profiles, unknown answer fields, invalid colors and dimensions, single-word captions, captions off, pause preservation, audio/color switches, and per-job changes that leave the original settings untouched.
- Skill frontmatter validation passed.
- The CLI now requires explicit `--style` for cut planning/caption generation. An omitted profile fails instead of silently applying another person's preset.
- Instruction review covers first-use Create/Reuse routing, skipping setup when a profile is attached, no-video setup, metadata-only use of footage, conditional brand/reference questions, assisted import of ordinary Markdown, and user-edited prose conflicting with machine settings.

## Changed behavior

The durable deliverable is a portable Markdown profile. Its readable preferences and complete, versioned settings travel together. New sessions import the attachment; no hidden user store, account identity or persistent memory is required. The bundled Code Gino JSON remains an explicitly selected example preset. Existing preferences are carried into a Code Gino Markdown profile, not forced onto new users.

Orientation updates the canvas and caption layout starting points. Caption mode `off` omits caption events; `keep_all` disables actual silence cuts. Rendering instructions honor profile switches for branding, hooks, graphics, transitions, grading, music and delivery. Fine visual/layout preferences still require the editing agent to implement and inspect them.

## Limits

- No new full video was rendered during this update. Passing profile tests does not establish visual quality, transcription accuracy, reference-style similarity or browser playback quality.
- Conversational scenarios were reviewed as instructions, not executed as autonomous agent benchmarks. Named-style references must be supplied/inspected before claiming a match.
- The importer validates machine settings, not agreement with human-edited prose. The agent must read both and resolve conflicts.
- Output settings and media dependencies are portable; this is not a locked renderer or a promise of identical creative edits across runs.
- The replacement `.skill` must be installed through the supported UI before it becomes the active installed version. A profile update alone does not require reinstalling the skill.
