# Effects coverage and approved branding

## Turn an effects brief into visible demonstrations

Read the transcript before designing. For an explicit effects demo, map every requested effect to the actual spoken cue. Add one entry per demonstration to `effects.json`:

```json
{
  "id": "glass-demo",
  "requested_effect": "glassmorphism cards",
  "anchor_text": "glassmorphism cards",
  "source_start": 45.2,
  "timeline_start": 45.2,
  "timeline_end": 48.0,
  "implementation": "Translucent panel, real background blur, bright edge and moving light behind it",
  "asset_provenance": "Original composition; no stock footage",
  "status": "planned",
  "verification": null
}
```

The example times illustrate the schema, not a default schedule. Derive all timings from the current footage and final EDL. Update status and verification only after inspecting the encoded result. A full brief can justify more effects than the ordinary sparse-graphics default.

| Requested effect | Visible implementation | Insufficient substitute |
|---|---|---|
| B-roll | Relevant supplementary footage, screen capture or animated still with disclosed provenance | A card that only says “B-roll” |
| AI video insert | A generated video where supported, or an honestly described animated AI image when that meets the request | Claiming a panned still is generated live-action footage |
| Bouncing text | Obvious vertical motion/easing on the actual emphasis text | Barely perceptible caption entrance |
| Slower/faster motion | Change the period/rate of the referenced object with a visible difference | A speed label with unchanged animation |
| Section card | A readable section takeover and designed transition | Tiny label in the corner |
| Lower third | Positioned name/context panel with an entrance | Center-screen title or face-covering graphic |
| Data chart | Axes/labels and animated data marks as appropriate | Unlabeled bars or invented business results |
| Webpage highlight | Actual relevant screenshot/capture, crop/zoom and animated focus marker | Generic webpage mockup mislabeled as the user's site |
| Glassmorphism | Translucency, actual backdrop blur/frost, border/reflection and content behind the panel | An opaque rectangle labeled “glassmorphism” |
| Full-screen vs inset | Show a visual full-screen, then as a smaller inset over live footage | Two labels without the framing change |

Use nearby speech to resolve the target of speed changes. If the speaker talks about text bouncing, demonstrate slow/fast text motion with the original voice unchanged. If they explicitly request source-video speed changes, adjust video/audio together, retain every spoken interval and regenerate all timings. Do not reinterpret an explicit request to preserve speech speed.

Use relevant existing/user assets first. Generate or source assets when authorized and available, respecting the environment's permission rules. If the requested medium cannot be delivered, explain the limitation; an image with a zoom is not secretly an equivalent video-generation result. Do not upload private footage to a new external service without authorization.

## Herk workflow means more than a renderer

Read the repository's relevant `hyperframes-video-beats`, `hyperframes`, transition and editing instructions. Use transcript anchors, a beat coverage map, actual animation, purpose-specific layouts and rendered-frame review. Do not count installed dependencies or a HyperFrames render command as proof that an effect was implemented. Current user preferences override generic house-style rules, including rapid pacing, aggressive cuts or word-by-word captions.

Keep a persistent source layer or explicit source continuation underneath timed effects. Use non-timed visual wrappers, synchronous paused timelines and finite animation durations. Keep tracks and source offsets correct for live insets. Never animate media playback with GSAP. Source/audio transitions must not delete words or create timing drift.

## Branding the user approved

Read colors, identity and timing from `branding` in the resolved `job-style.json`. If branding is disabled, omit branded intro/outro; respect their individual switches too. The Code Gino example profile must not supply another user's website, handle or palette. Follow the user's selected profile palette.

- Opening: brief truthful hook and handle over live footage, gentle entrance, speech starts immediately. Use the palette for accents/shadow/treatment; avoid an opaque intro slate delaying the recording.
- Outro, when enabled: short card using the profile's palette, website and handle; omit blank identity fields. Hold long enough to read through the final frame. No long blank fade or unnecessary extra CTA.
- A short intro/outro request does not reduce requested demonstrations elsewhere. Ordinary clips can remain restrained; effects-demo footage must show the named effects.
- Keep captions independent of branding: white readable phrases, actual measured timing, no forced one-word treatment.

## Natural caption editing

This section applies to `phrase_chunks`; use aligned single-word events when selected and omit captions entirely when `off`. The helper groups aligned words heuristically. Review the output in context; it cannot identify every Tagalog or English phrase boundary. Prefer natural thought units, generally 3–6 words, over a rigid word count. Short clauses can be shorter; a single long word can exceed the duration/character target and must be reviewed, not dropped or split arbitrarily.

Add `break_before` or `break_after` to reviewed words for clause, speaker, effect or placement boundaries. Keep names and short expressions together when possible. The helper also breaks on source/position changes. Set word positions before grouping if a gesture requires a new caption location. Check two-line layout with the real font; avoid orphaned one-word second lines when a different chunk split fits naturally. All words in each chunk appear together. A whole-chunk fade/slide is enough; emphasis graphics and normal captions serve different purposes.

## Playback evidence

For a reported stall, decode several seconds around it and later footage. Hash **video frames only**, not mixed audio/video output. Inspect a real frame strip: changing hashes can still be caused only by captions moving over frozen footage, so sample the source-video area separately where possible. Check full-file decoding, audio continuity, frame rate, duration and fast-start metadata. Distinguish held graphics from source playback. Lower bitrate can improve streaming but does not establish why a user's player stopped. State that limit honestly.
