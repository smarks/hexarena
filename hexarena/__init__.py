"""hexarena -- game-agnostic hex-grid primitives shared across hex wargames.

Provides hex coordinate math (:mod:`hexarena.hex`), injectable dice
(:mod:`hexarena.dice`), generic Dijkstra reachability
(:mod:`hexarena.pathfinding`), and pixel geometry for rendering
(:mod:`hexarena.layout`). It carries no game rules, terrain, units, or facing --
those live in the games that depend on it (orge, melee).
"""
from __future__ import annotations

from .dice import Dice
from .hex import CUBE_DIRECTIONS, FLAT, POINTY, Hex, HexLayout
from .layout import HexGeom, hex_center, hex_corners, layout
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
]
