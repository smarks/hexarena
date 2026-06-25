"""
Hexagonal grid coordinates and math, shared across hex-based games.

This module is deliberately game-agnostic: it knows nothing about terrain,
units, facing, or rendering. It provides a value type for a hex identified by
its 1-based ``(col, row)`` offset position, and a :class:`HexLayout` that
converts that offset position to cube coordinates so distance and adjacency
math is clean and exact.

Two orientations are supported:

* ``FLAT`` -- flat-top hexes whose vertices point left/right; columns are the
  offset axis (each column is shoved up/down half a hex). This is the layout
  the Ogre maps use.
* ``POINTY`` -- pointy-top hexes whose vertices point up/down; rows are the
  offset axis.

``odd=True`` pushes odd offset lines half a hex (the "odd-q"/"odd-r" schemes
from the redblobgames hexagon guide); ``odd=False`` pushes the even lines.

Distance and adjacency are layout-consistent regardless of orientation, so a
game can pick whichever matches its printed map and trust the math.
"""
from __future__ import annotations

from dataclasses import dataclass

FLAT = "flat"
POINTY = "pointy"

# The six cube-coordinate steps. For a FLAT layout these read, in order,
# N, NE, SE, S, SW, NW. For a POINTY layout the same indices read
# NE, E, SE, SW, W, NW. The order is stable so callers can treat the index as
# a compass/facing direction.
CUBE_DIRECTIONS: tuple[tuple[int, int, int], ...] = (
    (0, +1, -1),   # 0
    (+1, 0, -1),   # 1
    (+1, -1, 0),   # 2
    (0, -1, +1),   # 3
    (-1, 0, +1),   # 4
    (-1, +1, 0),   # 5
)


@dataclass(frozen=True, order=True)
class Hex:
    """A hex identified by its 1-based ``(col, row)`` offset position.

    The type is intentionally label-free; games that need a printed hex label
    (the Ogre CCRR scheme, say) wrap or subclass this and add their own.
    """

    col: int
    row: int


@dataclass(frozen=True)
class HexLayout:
    """Offset <-> cube conversion and the math built on top of it.

    Args:
        orientation: :data:`FLAT` or :data:`POINTY`.
        odd: ``True`` shoves odd offset lines half a hex, ``False`` the even.
    """

    orientation: str = FLAT
    odd: bool = True

    def __post_init__(self) -> None:
        if self.orientation not in (FLAT, POINTY):
            raise ValueError(f"orientation must be {FLAT!r} or {POINTY!r}")

    # ---- offset <-> cube ----
    def to_cube(self, hex_position: Hex) -> tuple[int, int, int]:
        """Convert a 1-based offset hex to 0-based cube coordinates."""
        col = hex_position.col - 1
        row = hex_position.row - 1
        if self.orientation == FLAT:
            parity = (col & 1) if self.odd else -(col & 1)
            cube_x = col
            cube_z = row - (col - parity) // 2
        else:  # POINTY
            parity = (row & 1) if self.odd else -(row & 1)
            cube_x = col - (row - parity) // 2
            cube_z = row
        cube_y = -cube_x - cube_z
        return cube_x, cube_y, cube_z

    def from_cube(self, cube_x: int, cube_y: int, cube_z: int) -> Hex:
        """Convert 0-based cube coordinates back to a 1-based offset hex."""
        if self.orientation == FLAT:
            parity = (cube_x & 1) if self.odd else -(cube_x & 1)
            col = cube_x
            row = cube_z + (cube_x - parity) // 2
        else:  # POINTY
            parity = (cube_z & 1) if self.odd else -(cube_z & 1)
            col = cube_x + (cube_z - parity) // 2
            row = cube_z
        return Hex(col + 1, row + 1)

    # ---- distance / adjacency ----
    def distance(self, start: Hex, end: Hex) -> int:
        """Number of hexes between two hexes (the firing/movement yardstick)."""
        start_x, start_y, start_z = self.to_cube(start)
        end_x, end_y, end_z = self.to_cube(end)
        return (
            abs(start_x - end_x) + abs(start_y - end_y) + abs(start_z - end_z)
        ) // 2

    def neighbor(self, hex_position: Hex, direction_index: int) -> Hex:
        """The adjacent hex in ``direction_index`` (0-5). No bounds-checking."""
        cube_x, cube_y, cube_z = self.to_cube(hex_position)
        step_x, step_y, step_z = CUBE_DIRECTIONS[direction_index % 6]
        return self.from_cube(cube_x + step_x, cube_y + step_y, cube_z + step_z)

    def neighbors(self, hex_position: Hex) -> list[Hex]:
        """All six adjacent hexes, ordered by direction index. No bounds-check."""
        return [self.neighbor(hex_position, index) for index in range(6)]

    def direction_to(self, start: Hex, end: Hex) -> int | None:
        """Direction index 0-5 if ``end`` is adjacent to ``start``, else ``None``."""
        for index in range(6):
            if self.neighbor(start, index) == end:
                return index
        return None

    def line(self, start: Hex, end: Hex) -> list[Hex]:
        """The hexes a straight line from ``start`` to ``end`` passes through.

        Inclusive of both endpoints. Used for line-of-flight / line-of-sight.
        Ties (a line grazing exactly between two hexes) are nudged with a tiny
        epsilon so the result is deterministic.
        """
        steps = self.distance(start, end)
        if steps == 0:
            return [start]
        start_cube = self.to_cube(start)
        end_cube = self.to_cube(end)
        result: list[Hex] = []
        for step in range(steps + 1):
            fraction = step / steps
            result.append(self._cube_round(start_cube, end_cube, fraction))
        return result

    def _cube_round(
        self,
        start_cube: tuple[int, int, int],
        end_cube: tuple[int, int, int],
        fraction: float,
    ) -> Hex:
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
        return self.from_cube(rounded_x, rounded_y, rounded_z)
