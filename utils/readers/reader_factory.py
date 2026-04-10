from pathlib import Path

from utils.readers.csv_reader import CSVReader
from utils.readers.base_reader import BaseReader

class ReaderFactory:
    _readers = {
        ".csv": CSVReader,
    }

    @classmethod
    def create_reader(cls, file_path: Path) -> BaseReader:
        extension = file_path.suffix.lower()

        if extension not in cls._readers:
            raise ValueError(
                f"Unsupported file extension: {extension}\n"
                f"Supported file extensions: {', '.join(cls._readers.keys())}"
            )
        
        reader_class = cls._readers[extension]
        return reader_class(file_path)