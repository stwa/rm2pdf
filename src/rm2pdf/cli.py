from __future__ import annotations

import logging

from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
from pathlib import Path

from rm2pdf.render import render
from rm2pdf.templates import get_template_path, set_template_path


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
    parser = ArgumentParser(
        description="Convert remarkable files to PDF",
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--output",
        type=Path,
        default="output.pdf",
        help="Where to put the output",
    )
    parser.add_argument(
        "--template-path",
        type=Path,
        default=get_template_path(),
        help="Where are your remarkable templates stored",
    )
    parser.add_argument(
        "content",
        type=Path,
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
    set_template_path(args.template_path)

    render(args.content, args.output)
