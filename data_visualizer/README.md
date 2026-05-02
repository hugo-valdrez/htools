# data_visualizer

Small browser-based viewer for data files.

It is meant for quickly checking what is inside a file without loading everything into a giant UI.

Supported formats:
- csv
- parquet

Run it with:

```bash
htools data-visualizer dummy/sample.parquet
```

Or with CSV:

```bash
htools data-visualizer dummy/sample.csv
```

Notes:
- it opens a local browser page by default
- it loads 50 rows at a time
- going forward fetches the next page lazily
- previous pages stay cached in the browser so going back is fast
- use `--no-browser` if you only want the local server URL
