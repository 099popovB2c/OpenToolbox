# OpenToolbox

A small desktop GUI that puts proven command-line tools behind simple buttons.

## Supported tools

- FFmpeg: compress video, extract audio
- ImageMagick: convert images
- ExifTool: remove metadata
- yt-dlp: download a media URL
- Pandoc: convert documents

The app detects which tools are installed and only enables compatible operations.

## Run

```bash
python opentoolbox.py
```

No telemetry, no account and no backend. External tools are not bundled; install them separately using your OS package manager.
