"""Generic Dijkstra reachability over a hex grid."""
from __future__ import annotations

from hexarena.hex import FLAT, Hex, HexLayout
from hexarena.pathfinding import reachable

LAYOUT = HexLayout(orientation=FLAT, odd=True)


def bounded_neighbors(size: int):
    def neighbors(hex_position: Hex):
        return [
            neighbor
            for neighbor in LAYOUT.neighbors(hex_position)
            if 1 <= neighbor.col <= size and 1 <= neighbor.row <= size
        ]

    return neighbors


def uniform_cost(_from: Hex, _to: Hex) -> int:
    return 1


def test_budget_one_reaches_exactly_the_neighbors() -> None:
    start = Hex(5, 5)
    reach = reachable(start, bounded_neighbors(11), uniform_cost, budget=1)
    assert set(reach.reachable_hexes()) == set(LAYOUT.neighbors(start))


def test_blocked_hexes_are_not_entered() -> None:
    start = Hex(5, 5)
    blocked = set(LAYOUT.neighbors(start))
    reach = reachable(
        start, bounded_neighbors(11), uniform_cost, budget=3, blocked=blocked
    )
    assert reach.reachable_hexes() == []  # fully walled in


def test_impassable_cost_skips_neighbor() -> None:
    start = Hex(5, 5)
    wall = LAYOUT.neighbor(start, 0)

    def cost(_from: Hex, to: Hex):
        return None if to == wall else 1

    reach = reachable(start, bounded_neighbors(11), cost, budget=1)
    assert wall not in reach.reachable_hexes()


def test_must_stop_halts_expansion_past_a_hex() -> None:
    start = Hex(1, 1)
    swamp = Hex(2, 1)

    def must_stop(hex_position: Hex) -> bool:
        return hex_position == swamp

    reach = reachable(
        start,
        bounded_neighbors(11),
        uniform_cost,
        budget=5,
        must_stop_fn=must_stop,
    )
    # swamp is reachable, but nothing is routed *through* it
    assert swamp in reach.cost
    for hex_position, parent in reach.came_from.items():
        if parent == swamp:
            raise AssertionError("expansion continued past a must-stop hex")


def test_path_reconstruction() -> None:
    start = Hex(1, 1)
    reach = reachable(start, bounded_neighbors(11), uniform_cost, budget=10)
    target = Hex(4, 4)
    path = reach.path_to(target)
    assert path is not None
    assert path[-1] == target
    assert len(path) == reach.cost[target]
