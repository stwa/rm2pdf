from __future__ import annotations

import math

remarkable_palette = {
    # BLACK = 0
    0: (0, 0, 0),
    # GRAY = 1
    1: (125, 125, 125),
    # WHITE = 2
    2: (255, 255, 255),
    # YELLOW = 3
    3: (255, 255, 0),
    # GREEN = 4
    4: (0, 255, 0),
    # PINK = 5
    5: (255, 0, 255),
    # BLUE = 6
    6: (0, 0, 255),
    # RED = 7
    7: (255, 0, 0),
    # GRAY_OVERLAP = 8
    8: (125, 125, 125),
}

Degree = float
Radian = float

# pylint: disable=unused-argument


class Pen:
    def __init__(self, base_width: float, base_color_id: int) -> None:
        self.base_width = base_width
        self.base_color = remarkable_palette[base_color_id]
        self.segment_length = 1000
        self.base_opacity = 1.0
        self.name = "Basic Pen"
        # initial stroke values
        self.stroke_linecap = "round"
        self.stroke_width = base_width
        self.stroke_color = base_color_id

    @classmethod
    def direction_to_tilt(cls, direction: Degree) -> Radian:
        return math.radians(direction)

    def get_segment_width(
        self,
        speed: float,
        direction: Degree,
        width: float,
        pressure: float,
    ) -> float:
        return self.base_width

    def get_segment_color(
        self,
        speed: float,
        direction: Degree,
        width: float,
        pressure: float,
    ) -> tuple[float, float, float]:
        return (
            self.base_color[0] / 255,
            self.base_color[1] / 255,
            self.base_color[2] / 255,
        )

    def get_segment_opacity(
        self,
        speed: float,
        direction: Degree,
        width: float,
        pressure: float,
    ) -> float:
        return self.base_opacity

    def cutoff(self, value: float) -> float:
        return max(0, min(1, value))

    @classmethod
    def create(cls, pen_id: int, color_id: int, width: float) -> Pen:
        pens = {
            0: Brush,
            1: Pencil,
            2: Ballpoint,
            3: Marker,
            4: Fineliner,
            5: Highlighter,
            6: Eraser,
            7: MechanicalPencil,
            8: EraseArea,
            12: Brush,
            13: MechanicalPencil,
            14: Pencil,
            15: Ballpoint,
            16: Marker,
            17: Fineliner,
            18: Highlighter,
            21: Caligraphy,
        }

        if pen_id in [5, 18]:
            width = 15.0

        pen_class: type[Pen] = pens[pen_id]
        return pen_class(width, color_id)


class Fineliner(Pen):
    def __init__(self, base_width: float, base_color_id: int) -> None:
        super().__init__(base_width, base_color_id)
        self.base_width = base_width * 1.5
        self.name = "Fineliner"


class Ballpoint(Pen):
    def __init__(self, base_width: float, base_color_id: int) -> None:
        super().__init__(base_width, base_color_id)
        self.segment_length = 5
        self.name = "Ballpoint"

    def get_segment_width(
        self,
        speed: float,
        direction: Degree,
        width: float,
        pressure: float,
    ) -> float:
        return pressure / 255 + 0.175 * width - 0.125 * speed / 50

    def get_segment_opacity(
        self,
        speed: float,
        direction: Degree,
        width: float,
        pressure: float,
    ) -> float:
        intensity = (0.1 * -((speed / 4) / 35)) + (1.2 * pressure / 255) + 0.5
        return self.cutoff(intensity)


class Marker(Pen):
    def __init__(self, base_width: float, base_color_id: int) -> None:
        super().__init__(base_width, base_color_id)
        self.segment_length = 3
        self.name = "Marker"

    def get_segment_width(
        self,
        speed: float,
        direction: Degree,
        width: float,
        pressure: float,
    ) -> float:
        return 0.2 * width - 0.4 * self.direction_to_tilt(direction)


class Pencil(Pen):
    def __init__(self, base_width: float, base_color_id: int) -> None:
        super().__init__(base_width, base_color_id)
        self.segment_length = 2
        self.name = "Pencil"

    def get_segment_width(
        self,
        speed: float,
        direction: Degree,
        width: float,
        pressure: float,
    ) -> float:
        segment_width = 0.06 * self.base_width * width
        return min(segment_width, self.base_width * 10)

    def get_segment_opacity(
        self,
        speed: float,
        direction: Degree,
        width: float,
        pressure: float,
    ) -> float:
        segment_opacity = (0.1 * -((speed / 4) / 35)) + pressure / 255
        return self.cutoff(segment_opacity)


class MechanicalPencil(Pen):
    def __init__(self, base_width: float, base_color_id: int) -> None:
        super().__init__(base_width, base_color_id)
        self.base_width = self.base_width**2
        self.base_opacity = 0.7
        self.name = "Mechanical Pencil"


class Brush(Pen):
    def __init__(self, base_width: float, base_color_id: int) -> None:
        super().__init__(base_width, base_color_id)
        self.segment_length = 2
        self.stroke_linecap = "round"
        self.opacity = 1
        self.name = "Brush"

    def get_segment_width(
        self,
        speed: float,
        direction: Degree,
        width: float,
        pressure: float,
    ) -> float:
        return 0.1 * width * (1 + (pressure / 255))

    def get_segment_opacity(
        self,
        speed: float,
        direction: Degree,
        width: float,
        pressure: float,
    ) -> float:
        intensity = ((pressure / 255) ** 1.5 - 0.2 * (speed / 50)) * 1.5
        return self.cutoff(intensity)


class Highlighter(Pen):
    def __init__(self, base_width: float, base_color_id: int) -> None:
        super().__init__(base_width, base_color_id)
        self.stroke_linecap = "square"
        self.base_width = self.base_width * 1.8
        self.base_opacity = 0.2
        self.name = "Highlighter"


class Eraser(Pen):
    def __init__(self, base_width: float, base_color_id: int) -> None:
        super().__init__(base_width, base_color_id)
        self.stroke_linecap = "square"
        self.base_width = self.base_width * 2
        self.name = "Eraser"


class EraseArea(Pen):
    def __init__(self, base_width: float, base_color_id: int) -> None:
        super().__init__(base_width, base_color_id)
        self.stroke_linecap = "square"
        self.base_opacity = 0
        self.name = "Erase Area"


class Caligraphy(Pen):
    def __init__(self, base_width: float, base_color_id: int) -> None:
        super().__init__(base_width, base_color_id)
        self.segment_length = 2
        self.name = "Calligraphy"

    def get_segment_width(
        self,
        speed: float,
        direction: Degree,
        width: float,
        pressure: float,
    ) -> float:
        return 0.3 * width - 0.3 * self.direction_to_tilt(direction)
