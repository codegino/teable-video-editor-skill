# Teable Video Editor

Edit your talking-head videos through [Teable](https://app.teable.ai) chat. Create your own style, add captions and effects, and reuse that style on your next video.

**You only need a Teable account.** This skill is built around Teable's AI tools and editing environment, so you don't need to set up video software or run code on your computer.

You can try it on Teable's **free plan**, with limited usage. What you can complete depends on the credits and features available to your account.

## Get started

1. Open Teable AI chat.
2. Ask:

   > Install the teable-video-editor skill from this GitHub repository: https://github.com/codegino/teable-video-editor-skill

3. Run `/teable-video-editor` and choose **Create a profile** or **Reuse a profile**.

A ready-to-install [skill file](dist/teable-video-editor.skill) is also included.

## Create your style once

The skill asks about your video format, language, captions, branding, pacing, effects and sound. If you attach a video, its metadata helps suggest technical defaults. You can also set up a profile without a video.

You'll receive a **Markdown style profile**. Save it. In a fresh chat, attach the profile with your next recording and say:

> Use this profile to edit my video.

An attached profile skips setup. To change it, say “Update my profile.” For a temporary change, say “For this video only.”

## What to expect

- Tagalog, English or Taglish, with your original voice preserved.
- Vertical, landscape or square videos.
- Captions, branding and effects based on your preferences.
- An edited MP4, with subtitles and an editable project when selected.

Review the result before sharing. The skill does not automatically publish your videos. Your profile keeps preferences consistent; individual creative edits can still vary.

## Credits

Created by [Code Gino](https://carlogino.com), inspired by [Nate Herk's Herk Edit Kit](https://github.com/nateherkai/herk-edit-kit).

[MIT license](LICENSE) · [Third-party notices](THIRD_PARTY_NOTICES.md) · [Contributor guide](CONTRIBUTING.md)
