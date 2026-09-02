"""Axial hex coordinate math: distance, adjacency, rings, lines, reachability."""

from __future__ import annotations

from hexarena.axial import (
    AxialHex,
    axial_add,
    axial_direction_to,
    axial_distance,
    axial_is_adjacent,
    axial_line,
    axial_neighbor,
    axial_neighbors,
    axial_ring,
)
from hexarena.layout import axial_hex_center
from hexarena.pathfinding import reachable

ORIGIN = AxialHex(0, 0)


def test_distance_to_self_is_zero() -> None:
    assert axial_distance(ORIGIN, ORIGIN) == 0


def test_neighbors_are_distance_one_and_mutual() -> None:
    center = AxialHex(2, -3)
    neighbors = axial_neighbors(center)
    assert len(set(neighbors)) == 6
    for neighbor in neighbors:
        assert axial_distance(center, neighbor) == 1
        assert axial_is_adjacent(center, neighbor)
        assert center in axial_neighbors(neighbor)


def test_add_and_neighbor_agree() -> None:
    center = AxialHex(1, 1)
    for direction in range(6):
        assert axial_add(center, direction) == axial_neighbor(center, direction)
    # direction wraps modulo 6
    assert axial_add(center, 6) == axial_add(center, 0)


def test_direction_to_is_inverse_of_neighbor() -> None:
    center = AxialHex(4, -2)
    for index in range(6):
        neighbor = axial_neighbor(center, index)
        assert axial_direction_to(center, neighbor) == index


def test_direction_to_self_is_zero() -> None:
    assert axial_direction_to(ORIGIN, ORIGIN) == 0


def test_direction_to_picks_the_closest_reducing_step() -> None:
    # (3, 0) is two steps east of the origin along direction 0.
    direction = axial_direction_to(ORIGIN, AxialHex(3, 0))
    assert axial_distance(axial_add(ORIGIN, direction), AxialHex(3, 0)) == 2


def test_ring_zero_is_just_center() -> None:
    assert axial_ring(ORIGIN, 0) == [ORIGIN]


def test_ring_hexes_are_all_at_the_given_distance() -> None:
    radius = 3
    ring = axial_ring(ORIGIN, radius)
    assert len(ring) == 6 * radius
    assert len(set(ring)) == 6 * radius
    for hex_position in ring:
        assert axial_distance(ORIGIN, hex_position) == radius


def test_line_endpoints_and_length() -> None:
    start, end = AxialHex(0, 0), AxialHex(4, -1)
    drawn = axial_line(start, end)
    assert drawn[0] == start
    assert drawn[-1] == end
    assert len(drawn) == axial_distance(start, end) + 1
    for earlier, later in zip(drawn, drawn[1:]):
        assert axial_distance(earlier, later) == 1


def test_line_to_self_is_a_single_hex() -> None:
    assert axial_line(ORIGIN, ORIGIN) == [ORIGIN]


def test_axial_hex_center_matches_pointy_top_formula() -> None:
    # Standard pointy-top axial-to-pixel conversion (redblobgames), the same
    # formula battle's static/js/battle.js axialToPixel() computes client-side.
    import math

    size = 10.0
    sqrt3 = math.sqrt(3.0)
    x, y = axial_hex_center(2, -1, size=size)
    assert round(x, 6) == round(size * (sqrt3 * 2 + (sqrt3 / 2) * -1), 6)
    assert round(y, 6) == round(size * 1.5 * -1, 6)


def test_axial_hex_center_of_origin_is_pixel_origin() -> None:
    assert axial_hex_center(0, 0, size=10.0) == (0.0, 0.0)


def test_reachable_works_with_axial_hexes() -> None:
    # hexarena.pathfinding.reachable() is generic over any hashable node, so
    # it works directly with AxialHex -- no offset conversion required.
    def uniform_cost(_from: AxialHex, _to: AxialHex) -> int:
        return 1

    reach = reachable(ORIGIN, axial_neighbors, uniform_cost, budget=2)
    expected = set(axial_ring(ORIGIN, 1)) | set(axial_ring(ORIGIN, 2))
    assert set(reach.reachable_hexes()) == expected


def test_reachable_respects_blockers_with_axial_hexes() -> None:
    def uniform_cost(_from: AxialHex, _to: AxialHex) -> int:
        return 1

    blocked = set(axial_neighbors(ORIGIN))
    reach = reachable(ORIGIN, axial_neighbors, uniform_cost, budget=3, blocked=blocked)
    assert reach.reachable_hexes() == []  # fully walled in by its own neighbors
