from pathlib import Path

from utils.readers.base_reader import BaseReader
from utils.readers.yaml_reader import YAMLReader


class ReaderFactory:
    _readers = {
        ".yaml": YAMLReader,
        ".yml": YAMLReader,
    }

    @classmethod
    def create_reader(cls, file_path: Path) -> BaseReader:
        extension = file_path.suffix.lower()

        if extension not in cls._readers:
            raise ValueError(
                f"Unsupported file extension: {extension}.\n"
                f"Supported file extensions: {', '.join(cls._readers.keys())}"
            )

        reader_class = cls._readers[extension]
        return reader_class(file_path)
