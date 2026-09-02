"""hexarena -- game-agnostic hex-grid primitives shared across hex wargames.

Provides hex coordinate math for both offset (:mod:`hexarena.hex`) and axial
(:mod:`hexarena.axial`) grids, injectable dice (:mod:`hexarena.dice`),
generic Dijkstra reachability (:mod:`hexarena.pathfinding`), and pixel
geometry for rendering (:mod:`hexarena.layout`). It carries no game rules,
terrain, units, or facing -- those live in the games that depend on it
(orge, melee, battle).
"""

from __future__ import annotations

from .axial import (
    AXIAL_DIRECTIONS,
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
from .dice import Dice
from .hex import CUBE_DIRECTIONS, FLAT, POINTY, Hex, HexLayout
from .layout import HexGeom, axial_hex_center, hex_center, hex_corners, layout
from .pathfinding import Reach, reachable

__all__ = [
    "Dice",
    "Hex",
    "HexLayout",
    "CUBE_DIRECTIONS",
    "FLAT",
    "POINTY",
    "Reach",
    "reachable",
    "HexGeom",
    "hex_center",
    "hex_corners",
    "layout",
    "axial_hex_center",
    "AxialHex",
    "AXIAL_DIRECTIONS",
    "axial_add",
    "axial_neighbor",
    "axial_neighbors",
    "axial_distance",
    "axial_is_adjacent",
    "axial_direction_to",
    "axial_ring",
    "axial_line",
]
