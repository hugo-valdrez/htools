from utils.writers.csv_writer import CSVWriter
from utils.writers.base_writer import BaseWriter

class WriterFactory:
    _writers = {
        ".csv": CSVWriter
    }

    @classmethod
    def create_writer(cls, file_format: str, file_name: str) -> BaseWriter:
        file_format = file_format.lower()

        if file_format not in cls._writers:
            raise ValueError(
                f"Unsupported file extension: {file_format}.\n"
                f"Supported file extensions: {', '.join(cls._writers.keys())}"
            )
        
        writer_class = cls._writers[file_format]
        return writer_class(file_name)