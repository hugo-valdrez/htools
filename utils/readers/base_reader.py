from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Iterator

class BaseReader(ABC):
    def __init__(self, file_path: Path):
        self.file_path = file_path

        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {self.file_path}")
        
    @abstractmethod
    def iread(self) -> Iterator[Dict[str, Any]]:
        pass

    @abstractmethod
    def read(self) -> Dict[str, Any]:
        pass