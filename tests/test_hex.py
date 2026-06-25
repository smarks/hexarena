"""Hex coordinate math: distance, adjacency, round-tripping, lines."""
from __future__ import annotations

import pytest

from hexarena.hex import FLAT, POINTY, Hex, HexLayout

FLAT_ODD_Q = HexLayout(orientation=FLAT, odd=True)
POINTY_ODD_R = HexLayout(orientation=POINTY, odd=True)


@pytest.mark.parametrize("layout", [FLAT_ODD_Q, POINTY_ODD_R])
def test_offset_cube_roundtrip(layout: HexLayout) -> None:
    for col in range(1, 12):
        for row in range(1, 12):
            original = Hex(col, row)
            assert layout.from_cube(*layout.to_cube(original)) == original


@pytest.mark.parametrize("layout", [FLAT_ODD_Q, POINTY_ODD_R])
def test_neighbors_are_distance_one_and_mutual(layout: HexLayout) -> None:
    center = Hex(5, 5)
    neighbors = layout.neighbors(center)
    assert len(set(neighbors)) == 6
    for neighbor in neighbors:
        assert layout.distance(center, neighbor) == 1
        # adjacency is symmetric
        assert center in layout.neighbors(neighbor)


def test_distance_to_self_is_zero() -> None:
    assert FLAT_ODD_Q.distance(Hex(3, 4), Hex(3, 4)) == 0


def test_flat_odd_q_cube_matches_ogre_reference() -> None:
    # Values produced by the original orge engine.hexmap._to_cube (flat, odd-q).
    assert FLAT_ODD_Q.to_cube(Hex(1, 1)) == (0, 0, 0)
    assert FLAT_ODD_Q.to_cube(Hex(2, 1)) == (1, -1, 0)
    assert FLAT_ODD_Q.to_cube(Hex(3, 2)) == (2, -2, 0)
    # A known distance on the Ogre grid.
    assert FLAT_ODD_Q.distance(Hex(11, 17), Hex(11, 1)) == 16


def test_direction_to_is_inverse_of_neighbor() -> None:
    center = Hex(6, 6)
    for index in range(6):
        neighbor = FLAT_ODD_Q.neighbor(center, index)
        assert FLAT_ODD_Q.direction_to(center, neighbor) == index
    assert FLAT_ODD_Q.direction_to(center, Hex(99, 99)) is None


def test_line_endpoints_and_length() -> None:
    start, end = Hex(2, 2), Hex(6, 2)
    drawn = FLAT_ODD_Q.line(start, end)
    assert drawn[0] == start
    assert drawn[-1] == end
    assert len(drawn) == FLAT_ODD_Q.distance(start, end) + 1
    # consecutive hexes on the line are adjacent
    for earlier, later in zip(drawn, drawn[1:]):
        assert FLAT_ODD_Q.distance(earlier, later) == 1


def test_invalid_orientation_rejected() -> None:
    with pytest.raises(ValueError):
        HexLayout(orientation="sideways")
