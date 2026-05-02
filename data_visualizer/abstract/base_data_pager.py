from abc import ABC, abstractmethod
from pathlib import Path

import polars as pl


class BaseDataPager(ABC):
    def __init__(self, file_path: Path):
        self.file_path = Path(file_path)

        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {self.file_path}")
        if not self.file_path.is_file():
            raise ValueError(f"Path is not a file: {self.file_path}")

    @property
    def format_name(self) -> str:
        return self.file_path.suffix.lower().lstrip(".")

    @abstractmethod
    def columns(self) -> list[str]:
        pass

    @abstractmethod
    def total_rows(self) -> int:
        pass

    @abstractmethod
    def page(self, index: int, page_size: int) -> pl.DataFrame:
        pass
