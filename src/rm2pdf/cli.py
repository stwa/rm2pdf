from __future__ import annotations

import logging

from argparse import ArgumentParser
from pathlib import Path

from rm2pdf.render import render


def _configure_logging(*, verbose: bool = False, quiet: bool = False) -> None:
    if not verbose and not quiet:
        return

    if quiet:
        logging.disable(logging.CRITICAL)
        return

    logging.basicConfig(
        format="%(name)s | %(levelname)s | %(message)s",
        level=logging.DEBUG if verbose else logging.INFO,
    )


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
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable debug output also of libraries",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Disable any output but the super critical",
    )
    args = parser.parse_args()

    _configure_logging(verbose=args.verbose, quiet=args.quiet)

    content_path = Path(args.content)
    output_path = Path(args.output)

    render(content_path, output_path)
