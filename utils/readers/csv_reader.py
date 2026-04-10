import csv
from pathlib import Path
from typing import Any, Dict, Iterator

from utils.readers.base_reader import BaseReader

class CSVReader(BaseReader):
    def __init__(self, file_path: Path):
        super().__init__(file_path)

    def read(self) -> Iterator[Dict[str, Any]]:
        with open(self.file_path, mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row in reader:
                yield row

    def read(self) -> Iterator[Dict[str, Any]]:
        with open(self.file_path, mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            return reader