from __future__ import annotations

import json
from itertools import pairwise
from pathlib import Path
from typing import Any, NamedTuple

from reportlab.graphics import renderPDF
from reportlab.pdfgen.canvas import Canvas
from rmscene import Block, RootTextBlock, SceneLineItemBlock, read_blocks
from svglib.svglib import Drawing, svg2rlg
from xdg import xdg_data_home

from rm2pdf.pen import Pen

DISPLAY_WIDTH = 1404
DISPLAY_HEIGHT = 1872
DISPLAY_DPI = 226
DISPLAY_DELTA_X = round(DISPLAY_WIDTH / 2.0)
DISPLAY_DELTA_Y = 0

PDF_PT_PER_PX = 72 / DISPLAY_DPI
PDF_WIDTH = DISPLAY_WIDTH * PDF_PT_PER_PX
PDF_HEIGHT = DISPLAY_HEIGHT * PDF_PT_PER_PX

TEMPLATE_PATH = xdg_data_home().joinpath("rmrl", "templates")


class Page(NamedTuple):
    id: str
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
    rm_path = content_path.parent.joinpath(
        content_path.name.removesuffix(".content")
    )
    with open(content_path, encoding="utf-8") as content_file:
        data = json.load(content_file)
        pages = [
            _get_page(page_data, rm_path)
            for page_data in data.get("cPages", {}).get("pages", [])
        ]

    canvas = Canvas(str(output_path), (PDF_WIDTH, PDF_HEIGHT))
    for page in pages:
        if page.template and page.template != "Blank":
            template_path = TEMPLATE_PATH.joinpath(f"{page.template}.svg")
            _render_template(template_path, canvas)
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
    with open(page_path, "rb") as infile:
        return list(read_blocks(infile))


def _get_page_dimensions(blocks: list[Block]) -> PageDimensions:
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
            print(f"warning: not converting block: {block.__class__}")
    canvas.restoreState()
    canvas.showPage()


def _get_linecap(linecap: str) -> int:
    return ["butt", "round", "square"].index(linecap)


def _draw_scene_line_item(
    page: Page, block: SceneLineItemBlock, canvas: Canvas
) -> None:
    if block.value is None:
        return

    pen: Pen = Pen.create(
        block.value.tool.value,
        block.value.color.value,
        block.value.thickness_scale,
    )

    for point1, point2 in pairwise(block.value.points):
        segment_color = pen.get_segment_color(
            point2.speed,
            point2.direction,
            point2.width,
            point2.pressure,
        )
        segment_width = pen.get_segment_width(
            point2.speed,
            point2.direction,
            point2.width,
            point2.pressure,
        )
        segment_opacity = pen.get_segment_opacity(
            point2.speed,
            point2.direction,
            point2.width,
            point2.pressure,
        )

        canvas.saveState()
        canvas.setLineCap(_get_linecap(pen.stroke_linecap))
        canvas.setLineJoin(1)
        canvas.setStrokeColor(segment_color, max(segment_opacity, 0))
        canvas.setLineWidth(segment_width)

        canvas.line(
            point1.x + page.dimensions.delta_x,
            point1.y + page.dimensions.delta_y,
            point2.x + page.dimensions.delta_x,
            point2.y + page.dimensions.delta_y,
        )
        canvas.restoreState()


def _draw_root_text(page: Page, block: RootTextBlock, canvas: Canvas) -> None:
    print("text")
