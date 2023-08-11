from __future__ import annotations

import json
import logging

from itertools import pairwise
from typing import TYPE_CHECKING, Any, Literal, NamedTuple

from reportlab.graphics import renderPDF
from reportlab.pdfgen.canvas import Canvas
from rmscene import Block, RootTextBlock, SceneLineItemBlock, read_blocks
from svglib.svglib import Drawing, svg2rlg

from rm2pdf.pen import Pen
from rm2pdf.templates import get_template


if TYPE_CHECKING:
    from pathlib import Path


DISPLAY_WIDTH = 1404
DISPLAY_HEIGHT = 1872
DISPLAY_DPI = 226
DISPLAY_DELTA_X = round(DISPLAY_WIDTH / 2.0)
DISPLAY_DELTA_Y = 0

PDF_PT_PER_PX = 72 / DISPLAY_DPI
PDF_WIDTH = DISPLAY_WIDTH * PDF_PT_PER_PX
PDF_HEIGHT = DISPLAY_HEIGHT * PDF_PT_PER_PX

_log = logging.getLogger(__name__)

FileType = Literal["pdf", "notebook"]


class Page(NamedTuple):
    id: str  # noqa: A003
    blocks: list[Block]
    dimensions: PageDimensions
    template: str | None
    vertical_scroll: int


class PageDimensions(NamedTuple):
    height: int
    width: int
    delta_x: int
    delta_y: int


def render(content_path: Path, output_path: Path) -> None:
    rm_path = content_path.with_suffix("")
    with content_path.open(encoding="utf-8") as content_file:
        data = json.load(content_file)
        pages = [
            _get_page(page_data, rm_path)
            for page_data in data.get("cPages", {}).get("pages", [])
        ]

    canvas = Canvas(str(output_path), (PDF_WIDTH, PDF_HEIGHT))
    for page in pages:
        if page.template and page.template != "Blank":
            _render_template(get_template(page.template), canvas)
        _render_page(page, canvas)
    canvas.save()


def _get_page(page_data: dict[str, Any], rm_path: Path) -> Page:
    page_id = page_data["id"]
    page_path = rm_path.joinpath(f"{page_id}.rm")
    page_blocks = _get_page_blocks(page_path)
    return Page(
        id=page_id,
        blocks=page_blocks,
        dimensions=_get_page_dimensions(page_blocks),
        template=page_data.get("template", {}).get("value", None),
        vertical_scroll=page_data.get("vertical_scroll", {}).get("value", 0),
    )


def _get_page_blocks(page_path: Path) -> list[Block]:
    with page_path.open("rb") as infile:
        return list(read_blocks(infile))


def _get_page_dimensions(blocks: list[Block]) -> PageDimensions:  # noqa: ARG001
    width = DISPLAY_WIDTH
    height = DISPLAY_HEIGHT
    xpos_delta = DISPLAY_DELTA_X
    ypos_delta = 0

    return PageDimensions(
        height=height, width=width, delta_x=xpos_delta, delta_y=ypos_delta
    )


def _render_template(template_path: Path, canvas: Canvas) -> None:
    if template_path.exists():
        background = svg2rlg(template_path)

        assert isinstance(background, Drawing)

        background.scale(
            PDF_WIDTH / background.width, PDF_WIDTH / background.width
        )
        renderPDF.draw(background, canvas, 0, 0)


def _render_page(page: Page, canvas: Canvas) -> None:
    canvas.saveState()
    canvas.translate(0, PDF_HEIGHT)
    canvas.scale(PDF_PT_PER_PX, -PDF_PT_PER_PX)
    for block in page.blocks:
        if isinstance(block, SceneLineItemBlock):
            _draw_scene_line_item(page, block, canvas)
        elif isinstance(block, RootTextBlock):
            _draw_root_text(page, block, canvas)
        else:
            _log.warning("not converting block: %s", block.__class__)
    canvas.restoreState()
    canvas.showPage()


def _draw_scene_line_item(
    page: Page, block: SceneLineItemBlock, canvas: Canvas
) -> None:
    if block.item.value is None:
        _log.warning("Ignoring empty block: %s", block.item.item_id)
        return

    _log.debug(
        "rendering block: %s | attr?: %s", block.item, hasattr(block, "value")
    )

    pen = Pen.create(
        block.item.value.tool.value,
        block.item.value.color.value,
        block.item.value.thickness_scale,
    )

    for pair in pairwise(block.item.value.points):
        pen.draw(
            pair,
            canvas,
            page.dimensions.delta_x,
            page.dimensions.delta_y,
        )


def _draw_root_text(
    page: Page, block: RootTextBlock, canvas: Canvas  # noqa: ARG001
) -> None:
    _log.debug("text")
