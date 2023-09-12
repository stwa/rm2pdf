from __future__ import annotations

from pathlib import Path

from xdg.BaseDirectory import xdg_cache_home


_template_path: Path = Path(xdg_cache_home) / "remarkable-templates"


def get_template_path() -> Path:
    return _template_path


def get_template(page_template: str) -> Path:
    return _template_path / f"{page_template}.svg"


def set_template_path(new_path: Path) -> None:
    global _template_path  # noqa: PLW0603

    _template_path = new_path
