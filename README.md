# OpenToolbox

OpenToolbox is a **desktop-friendly wrapper around powerful open-source command-line tools**. Its goal is to let normal users perform common media/document operations without memorizing FFmpeg, ImageMagick, ExifTool, yt-dlp or Pandoc commands.

It combines a GUI-oriented workflow with a persistent job queue and a headless queue controller for automation.

## What it does

Depending on which external tools are installed, OpenToolbox can provide workflows such as:

- video conversion/compression
- video trimming
- audio extraction
- image conversion (for example WebP)
- metadata cleanup
- media inspection with ffprobe
- yt-dlp download jobs
- document conversion through Pandoc
- batch processing
- output naming templates
- persistent queue/history
- retry of failed jobs
- headless processing while the GUI is closed

OpenToolbox does not reimplement FFmpeg or the other utilities. It builds safer/easier workflows around them.

## How it works

```text
Choose an action in OpenToolbox
          ↓
Validate inputs / build command arguments
          ↓
Add work to persistent queue
          ↓
Run external open-source tool
          ↓
Store job status/history
          ↓
Review / retry / export statistics
```

The queue is shared by the GUI and `queuectl.py`.

## External tools

OpenToolbox can integrate with tools such as:

- **FFmpeg / ffprobe** — video/audio processing and inspection
- **ImageMagick** — image conversion/processing
- **ExifTool** — metadata operations
- **yt-dlp** — supported media downloads
- **Pandoc** — document conversion

These utilities are separate projects with their own licenses, supported formats and installation requirements.

OpenToolbox should report missing dependencies rather than pretending an unavailable tool can run.

## Typical workflows

### Video compression / conversion

Select one or more input files, choose the relevant preset/action and send the jobs to the queue.

### Extract audio

A video input can be converted into an audio-oriented output using the available FFmpeg workflow.

### Trim video

v0.3+ includes video trim support so users can define a section instead of manually writing FFmpeg timestamps/arguments.

### Inspect media

The ffprobe-based inspector can surface technical information about a file before processing it.

### Batch image conversion

Batch workflows can process multiple image files with consistent settings and naming rules.

### Remove metadata

Where ExifTool is available, OpenToolbox can create metadata-cleaning jobs. Always keep originals/backups when metadata matters.

### yt-dlp jobs

OpenToolbox can wrap yt-dlp for supported downloads. Users remain responsible for following the source site's terms and applicable law.

## Persistent queue

Jobs are persisted in:

```text
~/.opentoolbox/queue.json
```

This means queue state can survive a GUI restart.

A queue entry can move through states such as pending, running, completed or failed, allowing failed work to be reviewed instead of disappearing.

## Headless queue controller

v0.4.0 adds `queuectl.py`, which operates on the same queue as the GUI.

Show statistics:

```bash
python queuectl.py stats
```

List jobs:

```bash
python queuectl.py list
```

Retry all failed jobs:

```bash
python queuectl.py retry
```

Retry one selected job:

```bash
python queuectl.py retry 123456789
```

Run pending work without opening the GUI:

```bash
python queuectl.py run-pending --limit 5
```

Prune old queue history:

```bash
python queuectl.py prune --keep 100
```

Clear completed history while keeping pending/failed work:

```bash
python queuectl.py clear-done
```

Export history and computed statistics:

```bash
python queuectl.py export queue-report.json
```

## Queue statistics

The queue controller can summarize:

- counts by status
- success/failure rate
- average duration
- totals by job type

This makes OpenToolbox useful for both interactive desktop work and small repeatable automation workflows.

## Batch naming

Batch jobs can use naming templates so output files follow a predictable pattern instead of requiring manual rename work afterward.

Before running a large batch, test the naming pattern on a small sample to avoid unintended overwrites or confusing filenames.

## Safety model

OpenToolbox executes external command-line tools on local files. That is powerful, so several rules matter:

- keep backups of important originals
- inspect output settings before large batches
- only use queue files you trust
- avoid manually editing queue commands unless you understand the arguments
- confirm available disk space before large conversions
- review downloaded content/source permissions when using yt-dlp

Commands stored in the queue are executed directly as argument arrays. A maliciously modified queue file can therefore be dangerous.

## Privacy

The core processing workflow is local:

- no OpenToolbox account
- no analytics requirement
- media conversion happens through local command-line tools
- queue/history stays on the local machine

Network access can occur for workflows whose underlying tool inherently uses the network, such as yt-dlp.

## Current limitations

OpenToolbox is an orchestration layer, so capabilities depend on installed external utilities.

Current limitations include:

- not every FFmpeg/ImageMagick/ExifTool feature is exposed
- external tool versions can behave differently
- no universal automatic dependency installer yet
- queue execution assumes trusted local configuration
- long-running jobs do not guarantee recovery from power loss/tool crashes
- platform-specific executable discovery may vary
- download features depend on yt-dlp/site compatibility

## Roadmap

Possible next steps:

- richer progress/ETA reporting
- saved user presets
- subtitle merge/extract tools
- playlist selection UI
- pause/resume where the underlying tool supports it
- folder-watch automation
- safer dependency diagnostics/install guidance
- plugin-style action architecture
- Windows packaged executable / Winget distribution
- Linux packaging

## Version

Current release: **v0.4.0**

## Security

See [SECURITY.md](SECURITY.md).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT
