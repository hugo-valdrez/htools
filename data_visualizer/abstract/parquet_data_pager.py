from pathlib import Path

import polars as pl

from data_visualizer.abstract.base_data_pager import BaseDataPager
from utils.readers.reader_factory import ReaderFactory


class ParquetDataPager(BaseDataPager):
    def __init__(self, file_path: Path):
        super().__init__(file_path)
        ReaderFactory.create_reader(file_path)
        self._scan = pl.scan_parquet(file_path)
        self._columns = self._scan.collect_schema().names()
        self._total_rows = self._scan.select(pl.len()).collect().item()

    def columns(self) -> list[str]:
        return self._columns

    def total_rows(self) -> int:
        return self._total_rows

    def page(self, index: int, page_size: int) -> pl.DataFrame:
        offset = index * page_size
        return self._scan.slice(offset, page_size).collect()
