# OpenToolbox

A small desktop GUI that puts proven command-line tools behind simple, reviewable actions.

## v0.2.0

- FFmpeg video compression presets: High quality / Balanced / Smaller file
- Extract MP3
- Single and batch ImageMagick conversion to WebP
- Batch ExifTool metadata removal
- yt-dlp video or audio-only download
- Pandoc document conversion
- Tool/version diagnostics
- Exact command preview in the log
- Cancel the current job

```bash
python opentoolbox.py
```

External tools are detected from PATH and are not bundled. No telemetry, account or backend is used.
