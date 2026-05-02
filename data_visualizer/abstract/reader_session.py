from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import polars as pl

from utils.readers.reader_factory import ReaderFactory


class ReaderSession:
    def __init__(self, file_path: Path, page_size: int):
        self.reader = ReaderFactory.create_reader(file_path)
        self.file_path = file_path
        self.page_size = page_size
        self._page_cache: dict[int, pl.DataFrame] = {}
        self._loaded_until = -1
        self._batch_iterator: Iterator[pl.DataFrame] = self.reader.read_batches(
            page_size
        )

    @property
    def format_name(self) -> str:
        return self.file_path.suffix.lower().lstrip(".")

    @property
    def columns(self) -> list[str]:
        return self.reader.columns

    @property
    def total_rows(self) -> int:
        return self.reader.total_rows

    def get_page(self, index: int) -> pl.DataFrame:
        if index < 0:
            index = 0

        if index in self._page_cache:
            return self._page_cache[index]

        while self._loaded_until < index:
            try:
                frame = next(self._batch_iterator)
            except StopIteration:
                break

            self._loaded_until += 1
            self._page_cache[self._loaded_until] = frame

        return self._page_cache.get(index, pl.DataFrame(schema=self.columns))
