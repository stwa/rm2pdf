from __future__ import annotations

from enum import Enum
from typing import Final, NamedTuple

MAX_COLOR_VALUE: Final = 255


class RemarkableColorIndex(Enum):
    BLACK = 0
    GRAY = 1
    WHITE = 2
    YELLOW = 3
    GREEN = 4
    PINK = 5
    BLUE = 6
    RED = 7
    GRAY_OVERLAP = 8


class Color(NamedTuple):
    red: int
    green: int
    blue: int

    def normalize(self) -> tuple[float, float, float]:
        return (
            self.red / MAX_COLOR_VALUE,
            self.green / MAX_COLOR_VALUE,
            self.blue / MAX_COLOR_VALUE,
        )

    @staticmethod
    def from_remarkable_color(index: RemarkableColorIndex) -> Color:
        return color_mapping[index]


color_mapping: dict[RemarkableColorIndex, Color] = {
    RemarkableColorIndex.BLACK: Color(0, 0, 0),
    RemarkableColorIndex.GRAY: Color(125, 125, 125),
    RemarkableColorIndex.WHITE: Color(255, 255, 255),
    RemarkableColorIndex.YELLOW: Color(255, 255, 0),
    RemarkableColorIndex.GREEN: Color(0, 255, 0),
    RemarkableColorIndex.PINK: Color(255, 0, 255),
    RemarkableColorIndex.BLUE: Color(0, 0, 255),
    RemarkableColorIndex.RED: Color(255, 0, 0),
    RemarkableColorIndex.GRAY_OVERLAP: Color(125, 125, 125),
}
