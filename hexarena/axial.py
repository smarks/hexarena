"""
Axial hex-grid coordinates, shared across hex-based games.

Axial coordinates ``(q, r)`` address a hex directly in cube space (``x=q``,
``z=r``, ``y=-x-z``) -- there is no printed column/row grid to reconcile,
unlike :mod:`hexarena.hex`'s offset-based :class:`~hexarena.hex.Hex` /
:class:`~hexarena.hex.HexLayout`, which convert a 1-based ``(col, row)`` grid
to cube coordinates before doing distance/adjacency math. A game whose native
board is already axial -- a hex graph radiating outward from an origin hex,
rather than a printed rectangle of columns and rows -- works with this module
directly instead of going through an offset conversion it has no use for.

This module is deliberately game-agnostic, matching :mod:`hexarena.hex`: no
terrain, units, or facing. The six direction indices double as a
facing/compass value for callers that need one, exactly as
:data:`hexarena.hex.CUBE_DIRECTIONS` does for the offset grid -- but the two
modules' direction orderings are independent of one another (they are built
from unrelated coordinate systems), so a game picks one module's ordering and
uses it consistently rather than mixing the two.
"""

from __future__ import annotations

from dataclasses import dataclass

# The six axial direction vectors, index 0-5. A step in direction ``d`` is
# ``(dq, dr)``; the index doubles as a facing for callers that want one.
AXIAL_DIRECTIONS: tuple[tuple[int, int], ...] = (
    (1, 0),
    (1, -1),
    (0, -1),
    (-1, 0),
    (-1, 1),
    (0, 1),
)


@dataclass(frozen=True, order=True)
class AxialHex:
    """A hex identified by its axial ``(q, r)`` coordinate, origin ``(0, 0)``."""

    q: int
    r: int

    def to_cube(self) -> tuple[int, int, int]:
        """Cube coordinates ``(x, y, z)``: ``x=q``, ``z=r``, ``y=-x-z``."""
        return self.q, -self.q - self.r, self.r


def axial_add(position: AxialHex, direction: int) -> AxialHex:
    """The hex one step from ``position`` in ``direction`` (0-5)."""
    delta_q, delta_r = AXIAL_DIRECTIONS[direction % 6]
    return AxialHex(position.q + delta_q, position.r + delta_r)


def axial_neighbor(position: AxialHex, direction: int) -> AxialHex:
    """The adjacent hex in ``direction`` (0-5). Alias for :func:`axial_add`
    matching :meth:`~hexarena.hex.HexLayout.neighbor`'s name."""
    return axial_add(position, direction)


def axial_neighbors(position: AxialHex) -> list[AxialHex]:
    """The six adjacent hexes, ordered by direction index."""
    return [axial_add(position, direction) for direction in range(6)]


def axial_distance(a: AxialHex, b: AxialHex) -> int:
    """Hex distance between two axial coordinates."""
    delta_q = a.q - b.q
    delta_r = a.r - b.r
    return (abs(delta_q) + abs(delta_r) + abs(delta_q + delta_r)) // 2


def axial_is_adjacent(a: AxialHex, b: AxialHex) -> bool:
    """Are two hexes exactly one step apart?"""
    return axial_distance(a, b) == 1


def axial_direction_to(start: AxialHex, target: AxialHex) -> int:
    """The direction index (0-5) that best points from ``start`` at ``target``.

    Chosen as the neighbour direction whose step most reduces the distance to
    the target (ties broken by lowest index, so the choice is deterministic).
    For ``start == target`` the answer is direction 0.
    """
    if start == target:
        return 0
    best_direction = 0
    best_distance: int | None = None
    for direction in range(6):
        stepped = axial_distance(axial_add(start, direction), target)
        if best_distance is None or stepped < best_distance:
            best_distance = stepped
            best_direction = direction
    return best_direction


def axial_ring(center: AxialHex, radius: int) -> list[AxialHex]:
    """The hexes exactly ``radius`` steps from ``center``, walked in order.

    ``radius`` 0 is just ``center``.
    """
    if radius == 0:
        return [center]
    hexes_on_ring: list[AxialHex] = []
    delta_q, delta_r = AXIAL_DIRECTIONS[4]
    position = AxialHex(center.q + delta_q * radius, center.r + delta_r * radius)
    for direction in range(6):
        for _step in range(radius):
            hexes_on_ring.append(position)
            position = axial_add(position, direction)
    return hexes_on_ring


def axial_line(start: AxialHex, end: AxialHex) -> list[AxialHex]:
    """The hexes a straight line from ``start`` to ``end`` passes through.

    Inclusive of both endpoints. Used for line-of-flight / line-of-sight.
    Ties (a line grazing exactly between two hexes) are nudged with a tiny
    epsilon so the result is deterministic -- the same construction as
    :meth:`hexarena.hex.HexLayout.line`, worked in cube space directly since
    axial coordinates carry no offset/parity to convert.
    """
    steps = axial_distance(start, end)
    if steps == 0:
        return [start]
    start_cube = start.to_cube()
    end_cube = end.to_cube()
    result: list[AxialHex] = []
    for step in range(steps + 1):
        fraction = step / steps
        result.append(_cube_round(start_cube, end_cube, fraction))
    return result


def _cube_round(
    start_cube: tuple[int, int, int],
    end_cube: tuple[int, int, int],
    fraction: float,
) -> AxialHex:
    # Nudge to keep grazing lines deterministic (redblobgames trick).
    epsilon = 1e-6
    x = start_cube[0] + (end_cube[0] - start_cube[0]) * fraction + epsilon
    y = start_cube[1] + (end_cube[1] - start_cube[1]) * fraction + 2 * epsilon
    z = start_cube[2] + (end_cube[2] - start_cube[2]) * fraction - 3 * epsilon
    rounded_x = round(x)
    rounded_y = round(y)
    rounded_z = round(z)
    diff_x = abs(rounded_x - x)
    diff_y = abs(rounded_y - y)
    diff_z = abs(rounded_z - z)
    if diff_x > diff_y and diff_x > diff_z:
        rounded_x = -rounded_y - rounded_z
    elif diff_y > diff_z:
        rounded_y = -rounded_x - rounded_z
    else:
        rounded_z = -rounded_x - rounded_y
    return AxialHex(rounded_x, rounded_z)
