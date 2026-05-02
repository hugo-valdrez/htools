from pathlib import Path

from data_visualizer.abstract.reader_session import ReaderSession

SUPPORTED_FORMATS = {".csv", ".parquet"}


def create_session(file_path: Path, page_size: int) -> ReaderSession:
    suffix = file_path.suffix.lower()
    if suffix in SUPPORTED_FORMATS:
        return ReaderSession(file_path, page_size)

    supported = ", ".join(sorted(SUPPORTED_FORMATS))
    raise ValueError(f"Unsupported file format: {suffix}. Supported: {supported}")
