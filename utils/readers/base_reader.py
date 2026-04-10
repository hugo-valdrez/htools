from abc import ABC, abstractmethod
from pathlib import Path


class BaseReader(ABC):
    def __init__(self, file_path: Path):
        self.file_path = Path(file_path)

        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {self.file_path}")
        if not self.file_path.is_file():
            raise ValueError(f"Path is not a file: {self.file_path}")
        
    @abstractmethod
    def read(self):
        pass