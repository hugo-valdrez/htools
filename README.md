# htools

Small collection of personal tools exposed through `htools`.

- `weekly-meals`: generate a weekly meal plan from YAML configs.
- `file-converter`: convert parquet files to CSV. (can be expanded)
- `data-visualizer`: quickly inspect CSV and parquet files in a browser. (can be expanded)

Examples:

```bash
htools weekly-meals
htools file-converter dummy/sample.parquet --to-format csv
htools data-visualizer dummy/sample.parquet
```
