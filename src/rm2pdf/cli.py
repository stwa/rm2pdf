from argparse import ArgumentParser
from pathlib import Path

from rm2pdf.render import render


def run() -> None:
    parser = ArgumentParser(description="Convert remarkable files to PDF")
    parser.add_argument(
        "--output",
        type=str,
        default="output.pdf",
        help="Where to put the output",
    )
    parser.add_argument(
        "content",
        type=str,
        help="The content file of the remarkable document",
    )
    args = parser.parse_args()

    content_path = Path(args.content)
    output_path = Path(args.output)

    render(content_path, output_path)
