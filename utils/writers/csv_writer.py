from __future__ import annotations

from typing import Optional

import polars as pl

from utils.writers.base_writer import BaseWriter


class CSVWriter(BaseWriter):
    def __init__(self, file_name: str):
        super().__init__(file_name)
        self._header_written = False
        self._file = None

    def _write_frame(
        self, frame: pl.DataFrame, *, append: bool, include_header: bool
    ) -> None:
        if frame.is_empty():
            return

        if not append and self._file is not None:
            self._file.close()
            self._file = None

        if self._file is None:
            mode = "a" if append else "w"
            self._file = open(self.file_name, mode, encoding="utf-8", newline="")

        frame.write_csv(self._file, include_header=include_header)
        self._file.flush()

        self._header_written = True

    def write(self, data: pl.DataFrame) -> None:
        self._write_frame(data, append=False, include_header=True)

    def write_batch(self, batch: pl.DataFrame) -> None:
        self._write_frame(
            batch, append=self._header_written, include_header=not self._header_written
        )

    def close(self) -> None:
        if self._file is not None:
            self._file.close()
            self._file = None
