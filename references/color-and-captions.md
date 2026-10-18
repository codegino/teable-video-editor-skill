# Preserve footage color and keep captions readable

Read this before preparing HDR footage, or when a user reports that an edit changed the picture's color or made captions gray. Branding and footage color are separate controls: a green palette does not authorize green skin, a brighter picture, or a new grade.

## Inspect the source first

Keep the original file unchanged. Probe it before choosing an intermediate or export format:

```sh
ffprobe -v error -select_streams v:0 \
  -show_entries stream=codec_name,pix_fmt,color_space,color_transfer,color_primaries:stream_side_data \
  -of json original.mov
```

- `arib-std-b67` identifies HLG; `smpte2084` identifies PQ. BT.2020 primaries and a 10-bit pixel format often accompany HDR, but primaries alone do not identify the transfer function.
- Check for Dolby Vision side data. Do not assume every Dolby Vision file has an HLG-compatible base layer.
- Preserve rotation and the intended framing as well as color. Transcription can read the original source; it does not require an 8-bit MP4 conversion.

A generic H.264 conversion or browser screenshot path can discard HDR information or reinterpret its values. A `--sdr` flag is not proof of a faithful HDR-to-SDR conversion. Keep an SDR preview separate from the master, and label it as a tone-mapped derivative when one is needed. If SDR delivery is required, use an explicit, reviewed tone map rather than merely changing metadata.

## Preserve the source and transform only the graphics

Use a verified HDR-capable renderer. If a browser composition changes the source appearance, export the caption/graphic layer with transparency and composite it locally onto the original HDR frames. Apply the same edit-decision map to the source video, audio, and caption timings. A color-verified clean HDR cut can be reused for caption-only revisions.

For a BT.2020 HLG source, retain 10-bit video, HLG transfer, and BT.2020 matrix/primaries. An HEVC MP4 with `hvc1` tagging is one delivery option. This preserves the HLG base layer, not necessarily Dolby Vision dynamic metadata; do not describe it as a full Dolby Vision round trip. Do not apply the HLG settings below to PQ or SDR sources.

White graphics need a deliberate HDR reference level. A low mapping can make CSS white appear gray even when the footage looks correct. Start with 300-nit caption white for the Code Gino HLG profile and inspect a five-second sample in the intended player. This is a starting point, not a universal brightness guarantee. Adjust the graphic layer, font weight, or backing rather than changing the footage exposure.

Keep alpha separate while converting RGB graphics. A color/range conversion can change transparent values and leave a haze over the whole picture. For example, this FFmpeg filter fragment assumes input 0 is the HLG source and input 1 is a timed sRGB RGBA caption layer already aligned to the edit:

```text
[1:v]split[rgb][rgba];
[rgba]alphaextract[mask];
[rgb]format=gbrpf32le,
 zscale=pin=bt709:tin=iec61966-2-1:min=gbr:rin=full:p=bt709:t=linear:m=gbr:r=full:npl=100,
 zscale=pin=bt709:tin=linear:min=gbr:rin=full:p=bt2020:t=arib-std-b67:m=bt2020nc:r=limited:npl=300,
 format=yuv420p10le[color];
[color][mask]alphamerge[caption];
[0:v][caption]overlay=format=yuv420p10[outv]
```

The color transform applies only to input 1. Encode `[outv]` in a compatible 10-bit format and retain the source's HLG/BT.2020 tags. Keep caption white configurable. For another transfer function, build and verify its own transform rather than relabeling the result.

## Verify the encoded sample, then the complete draft

1. Compare matching source/output frames outside the overlay area, using the actual frame-aligned edit map. Look for systematic brightness or hue shifts; normal lossy-encoding differences are not a grade. Pixel-value comparisons supplement visual review, not replace it.
2. Probe the exported bit depth and color tags. Metadata alone is not proof that the pixels were converted correctly.
3. Check every caption for readable size, contrast, overflow, and face clearance. CSS color values and browser contrast scores alone do not prove HDR playback legibility.
4. Compare the original and result in the same HDR-capable player. An SDR screenshot or a different player can display HDR differently; disclose when that playback check is unavailable.
5. When the user approves the footage but says the text is dim, retain the approved footage treatment and revise only the graphics. Save the preference in their profile.

Keep recordings, screenshots, transcripts, and per-video QA evidence in the private editing project, not in the reusable skill repository.
