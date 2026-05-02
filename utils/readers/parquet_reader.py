from collections.abc import Iterator
from pathlib import Path

import polars as pl

from utils.readers.base_reader import BaseReader


class ParquetReader(BaseReader):
    def __init__(self, file_path: Path):
        super().__init__(file_path)
        self._scan = pl.scan_parquet(self.file_path)
        self._columns = self._scan.collect_schema().names()
        self._total_rows = self._scan.select(pl.len()).collect().item()

    @property
    def columns(self) -> list[str]:
        return self._columns

    @property
    def total_rows(self) -> int:
        return self._total_rows

    def read(self) -> pl.DataFrame:
        return pl.read_parquet(self.file_path)

    def read_batches(self, batch_size: int = 100000) -> Iterator[pl.DataFrame]:
        if batch_size <= 0:
            raise ValueError("batch_size must be greater than 0")

        for offset in range(0, self._total_rows, batch_size):
            yield self._scan.slice(offset, batch_size).collect()
