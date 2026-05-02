# file_converter

Tiny file converter for quick format changes.

Right now it only supports:
- parquet -> csv

Run it with:

```bash
htools file-converter dummy/sample.parquet --to-format csv
```

You can also pick the output path:

```bash
htools file-converter dummy/sample.parquet --to-format csv --output-file dummy/out.csv
```

Notes:
- current scope is intentionally small
- conversion is done in one go, not in batches
