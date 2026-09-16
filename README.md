# OpenToolbox

Simple desktop GUI for useful open-source media/document command-line tools.

## v0.3.0

- Persistent job queue stored under `~/.opentoolbox/queue.json`
- Running jobs recover as pending after an interrupted app session
- Retry all failed jobs
- ffprobe media inspector for format, duration, bitrate and stream codecs
- Lossless-style stream-copy video trim helper
- Batch output naming templates such as `{stem}-small.webp`
- Existing FFmpeg presets, MP3 extraction, ImageMagick batch conversion, ExifTool cleanup, yt-dlp and Pandoc actions retained

The GUI shows every command before execution. External tools remain separate executables and are never bundled silently.
