from abc import ABC, abstractmethod

import polars as pl


class BaseWriter(ABC):
    def __init__(self, file_name: str):
        self.file_name = file_name

    @abstractmethod
    def write(self, data: pl.DataFrame) -> None:
        pass

    @abstractmethod
    def write_batch(self, batch: pl.DataFrame) -> None:
        pass

    @abstractmethod
    def close(self) -> None:
        pass
