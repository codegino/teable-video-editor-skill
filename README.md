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

The skill asks a few short rounds of questions about format, language, captions, pacing, effects, sound, color
and branding. If you attach a video, it can show you a short caption sample on your own footage.

You'll receive a **Markdown style profile** (`my-video-style.md`): plain bullets you can read and edit. Save it.
In a fresh chat, attach it with your next recording and say:

> Edit this.

For a one-off change, say “For this video only.”

## How it edits

On first use in a chat, the skill installs the editing engine,
[Herk Edit Kit](https://github.com/nateherkai/herk-edit-kit), into the sandbox and lets its own editing skills do
the work. Your profile overrides its house style:

| | |
| --- | --- |
| Cuts | Removes dead air, breaths, false starts and retakes |
| Hook | Big text in the first 3 seconds |
| Motion graphics | Animated cards and overlays, plus zoom-ins that keep your face clear |
| Captions | Natural phrases, word by word, key words, subtitles or none, in your position and colors |
| Color | Natural, warm, cool, black and white, or orange and teal |
| Sound | Light sound effects and a quiet music bed from music you attach |

Speech is transcribed inside the sandbox; your footage is not sent to a transcription service.

## Notes become rules

Watch the draft and give notes in plain words (English, Tagalog, Taglish). Lasting notes (“always…”, “never…”) are
saved in your profile under **My rules** and applied to every future edit. Attach the updated profile next time.

## What to expect

- Tagalog, English or Taglish, with your original voice preserved.
- Vertical, landscape or square videos.
- Drafts as MP4 (`v1`, `v2`, …), then a final MP4, with subtitles and an editable project if your profile asks for them.

Review the result before sharing. The skill does not publish your videos.

## Credits

Created by [Code Gino](https://carlogino.com), inspired by [Nate Herk's Herk Edit Kit](https://github.com/nateherkai/herk-edit-kit).

[MIT license](LICENSE) · [Third-party notices](THIRD_PARTY_NOTICES.md) · [Contributor guide](CONTRIBUTING.md)
