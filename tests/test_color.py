from pytest import raises

from rm2pdf.color import Color, RemarkableColorIndex


def test_color_factory_should_give_color_for_enum() -> None:
    index = RemarkableColorIndex.BLACK
    color = Color.from_remarkable_color(index)

    assert isinstance(color, Color)


def test_index_should_only_allow_existing_colors() -> None:
    index = 17

    with raises(
        ValueError,
        match=f"{index} is not a valid {RemarkableColorIndex.__name__}",
    ):
        RemarkableColorIndex(index)
