"""
Pixel geometry for rendering a hex grid (presentation helper).

This is the single source of truth for turning a 1-based ``(col, row)`` hex
into screen coordinates, so a SVG/Canvas renderer never re-derives the trig and
can't drift from the engine's adjacency. Both orientations from
:mod:`hexarena.hex` are supported; the offset parity (``odd``) must match the
:class:`~hexarena.hex.HexLayout` the engine uses so on-screen adjacency equals
game adjacency.

``size`` is the distance from a hex centre to a vertex.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from .hex import FLAT, POINTY, Hex

SQRT3 = math.sqrt(3.0)


@dataclass(frozen=True)
class HexGeom:
    col: int
    row: int
    cx: float
    cy: float
    points: list[tuple[float, float]]


def hex_center(
    col: int,
    row: int,
    *,
    size: float,
    margin: float,
    orientation: str = FLAT,
    odd: bool = True,
) -> tuple[float, float]:
    """Pixel centre of the hex at 1-based ``(col, row)``."""
    zero_col = col - 1
    zero_row = row - 1
    if orientation == FLAT:
        shove = 0.5 if odd else -0.5
        center_x = margin + size + 1.5 * size * zero_col
        center_y = (
            margin
            + (SQRT3 * size) * (zero_row + shove * (zero_col & 1))
            + (SQRT3 / 2.0) * size
        )
    elif orientation == POINTY:
        shove = 0.5 if odd else -0.5
        center_x = (
            margin
            + (SQRT3 * size) * (zero_col + shove * (zero_row & 1))
            + (SQRT3 / 2.0) * size
        )
        center_y = margin + size + 1.5 * size * zero_row
    else:
        raise ValueError(f"orientation must be {FLAT!r} or {POINTY!r}")
    return center_x, center_y


def hex_corners(
    center_x: float,
    center_y: float,
    size: float,
    orientation: str = FLAT,
) -> list[tuple[float, float]]:
    """The six vertices of a hex centred at ``(center_x, center_y)``."""
    # Flat-top vertices sit at 0,60,120...; pointy-top are rotated 30 degrees.
    angle_offset = 0.0 if orientation == FLAT else -30.0
    corners = []
    for corner_index in range(6):
        angle = math.radians(60 * corner_index + angle_offset)
        corners.append(
            (center_x + size * math.cos(angle), center_y + size * math.sin(angle))
        )
    return corners


def layout(
    hexes,
    *,
    size: float = 24.0,
    margin: float = 8.0,
    orientation: str = FLAT,
    odd: bool = True,
) -> dict:
    """Geometry for an iterable of :class:`~hexarena.hex.Hex`.

    Returns ``{'width', 'height', 'size', 'hexes': {(col,row): HexGeom-dict}}``.
    Callers that key geometry by a printed label can re-map the inner dict.
    """
    geom: dict[tuple[int, int], dict] = {}
    max_x = max_y = 0.0
    for hex_position in hexes:
        center_x, center_y = hex_center(
            hex_position.col,
            hex_position.row,
            size=size,
            margin=margin,
            orientation=orientation,
            odd=odd,
        )
        points = hex_corners(center_x, center_y, size, orientation)
        geom[(hex_position.col, hex_position.row)] = {
            "col": hex_position.col,
            "row": hex_position.row,
            "cx": round(center_x, 2),
            "cy": round(center_y, 2),
            "points": [[round(x, 2), round(y, 2)] for x, y in points],
        }
        max_x = max(max_x, center_x + size)
        max_y = max(max_y, center_y + size)
    return {
        "width": round(max_x + margin, 2),
        "height": round(max_y + margin, 2),
        "size": size,
        "hexes": geom,
    }
