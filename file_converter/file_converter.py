from argparse import ArgumentParser
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from utils.readers.reader_factory import ReaderFactory
from utils.writers.writer_factory import WriterFactory

SUPPORTED_INPUT_FORMATS = {".parquet"}
SUPPORTED_OUTPUT_FORMATS = {"csv"}
OUTPUT_SUFFIXES = {"csv": ".csv"}


def build_parser() -> ArgumentParser:
    parser = ArgumentParser(description="Convert parquet files to csv.")
    parser.add_argument("input_file", type=Path, help="Path to the input parquet file.")
    parser.add_argument(
        "--to-format",
        required=True,
        choices=sorted(SUPPORTED_OUTPUT_FORMATS),
        help="Output format.",
    )
    parser.add_argument(
        "--output-file",
        type=Path,
        help="Optional output file path. Defaults to the input file with a .csv suffix.",
    )
    return parser


def convert_file(input_file: Path, output_file: Path) -> None:
    reader = ReaderFactory.create_reader(input_file)
    writer = WriterFactory.create_writer(".csv", str(output_file))

    try:
        writer.write(reader.read())
    finally:
        writer.close()


def main(argv=None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    input_format = args.input_file.suffix.lower()
    if input_format not in SUPPORTED_INPUT_FORMATS:
        supported = ", ".join(sorted(SUPPORTED_INPUT_FORMATS))
        raise ValueError(
            f"Unsupported input file format: {input_format}. Supported: {supported}"
        )

    output_suffix = OUTPUT_SUFFIXES[args.to_format]
    output_file = args.output_file or args.input_file.with_suffix(output_suffix)
    convert_file(args.input_file, output_file)


if __name__ == "__main__":
    main()
