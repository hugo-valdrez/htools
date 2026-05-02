from collections.abc import Iterator
from pathlib import Path

import polars as pl

from utils.readers.base_reader import BaseReader


class ParquetReader(BaseReader):
    def __init__(self, file_path: Path):
        super().__init__(file_path)

    def read(self) -> pl.DataFrame:
        return pl.read_parquet(self.file_path)

    def read_batches(self, batch_size: int = 100000) -> Iterator[pl.DataFrame]:
        if batch_size <= 0:
            raise ValueError("batch_size must be greater than 0")

        scan = pl.scan_parquet(self.file_path)
        total_rows = scan.select(pl.len()).collect().item()

        for offset in range(0, total_rows, batch_size):
            yield scan.slice(offset, batch_size).collect()
