# OpenToolbox

Simple desktop GUI for useful open-source media/document command-line tools.

## v0.4.0

- New `queuectl.py` controls the same persistent queue from the command line
- Run pending jobs headlessly while the GUI is closed
- Retry all failed jobs or selected job IDs
- Queue statistics: status counts, success rate, average duration and job-type totals
- Queue retention with `prune --keep N`
- `clear-done` removes completed history without touching pending/failed jobs
- Export queue history plus computed statistics to JSON
- Existing desktop queue, ffprobe inspector, video trim, batch naming templates and media/document actions remain available

```bash
python queuectl.py stats
python queuectl.py list
python queuectl.py retry                  # all failed
python queuectl.py retry 123456789        # selected job
python queuectl.py run-pending --limit 5
python queuectl.py prune --keep 100
python queuectl.py export queue-report.json
```

The controller uses `~/.opentoolbox/queue.json`, the same file used by the GUI. Commands stored in the queue are executed directly as argument arrays; only run queue files you trust.
