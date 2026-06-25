"""Pixel geometry for rendering."""
from __future__ import annotations

import math

from hexarena.hex import FLAT, POINTY, Hex
from hexarena.layout import hex_center, hex_corners, layout

SQRT3 = math.sqrt(3.0)


def test_flat_center_matches_ogre_reference() -> None:
    # Original orge board.hexgeometry.hex_center, size=24 margin=8.
    cx, cy = hex_center(1, 1, size=24.0, margin=8.0, orientation=FLAT, odd=True)
    assert round(cx, 2) == 32.0
    assert round(cy, 2) == round(8.0 + (SQRT3 / 2.0) * 24.0, 2)
    # odd column (col=2) is shoved down half a hex
    _, cy2 = hex_center(2, 1, size=24.0, margin=8.0, orientation=FLAT, odd=True)
    assert cy2 > cy


def test_flat_has_six_distinct_corners() -> None:
    corners = hex_corners(100.0, 100.0, 24.0, FLAT)
    assert len(corners) == 6
    assert len({(round(x, 3), round(y, 3)) for x, y in corners}) == 6


def test_pointy_center_shoves_odd_rows_right() -> None:
    cx1, _ = hex_center(1, 1, size=24.0, margin=8.0, orientation=POINTY, odd=True)
    cx2, _ = hex_center(1, 2, size=24.0, margin=8.0, orientation=POINTY, odd=True)
    assert cx2 > cx1  # odd row pushed right


def test_layout_dict_shape() -> None:
    hexes = [Hex(c, r) for c in range(1, 4) for r in range(1, 4)]
    result = layout(hexes, size=24.0, margin=8.0)
    assert set(result) == {"width", "height", "size", "hexes"}
    assert len(result["hexes"]) == 9
    sample = result["hexes"][(1, 1)]
    assert len(sample["points"]) == 6
    assert result["width"] > 0 and result["height"] > 0
