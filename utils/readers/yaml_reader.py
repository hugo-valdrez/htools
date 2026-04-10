import yaml
from pathlib import Path
from typing import Any

from utils.readers.base_reader import BaseReader

class YAMLReader(BaseReader):
    def __init__(self, file_path: Path):
        super().__init__(file_path)

    def read(self) -> Any:
        with self.file_path.open("r", encoding="utf-8") as file:
            return yaml.safe_load(file)