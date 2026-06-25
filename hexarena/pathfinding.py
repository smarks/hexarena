"""
Generic terrain-aware reachability over a hex grid (Dijkstra).

The algorithm itself is game-agnostic. The caller injects the grid's behaviour
through callbacks:

* ``neighbors_fn(hex) -> iterable[Hex]`` -- the bounds-checked adjacency.
* ``cost_fn(from_hex, to_hex) -> int | None`` -- movement-point cost to enter
  ``to_hex`` from ``from_hex``; ``None`` means impassable.
* ``must_stop_fn(hex) -> bool`` -- optional; if a hex stops further movement
  this phase (e.g. Ogre forest/swamp), expansion does not continue past it.

This is the single implementation both Ogre's terrain movement and Melee's
movement-allowance reachability build on.
"""
from __future__ import annotations

import heapq
import itertools
from dataclasses import dataclass, field
from typing import Callable, Hashable, Iterable, Optional

Node = Hashable
NeighborsFn = Callable[[Node], Iterable[Node]]
CostFn = Callable[[Node, Node], Optional[int]]
MustStopFn = Callable[[Node], bool]


@dataclass
class Reach:
    """Result of a reachability search: cost to, and parent of, each hex."""

    cost: dict[Node, int]
    came_from: dict[Node, Node] = field(default_factory=dict)

    def reachable_hexes(self) -> list[Node]:
        return list(self.cost.keys())

    def path_to(self, target: Node) -> list[Node] | None:
        """Reconstruct the step list (excluding the start) to ``target``."""
        if target not in self.cost:
            return None
        path: list[Node] = []
        current = target
        while current in self.came_from:
            path.append(current)
            current = self.came_from[current]
        path.reverse()
        return path


def reachable(
    start: Node,
    neighbors_fn: NeighborsFn,
    cost_fn: CostFn,
    budget: int,
    *,
    must_stop_fn: MustStopFn | None = None,
    blocked: set[Node] | None = None,
) -> Reach:
    """Every hex reachable from ``start`` within ``budget`` movement points.

    Args:
        start: the origin hex.
        neighbors_fn: bounds-checked adjacency for a hex.
        cost_fn: entry cost from one hex to an adjacent hex; ``None`` = blocked.
        budget: movement points available.
        must_stop_fn: hexes that may be entered but not moved past this phase.
        blocked: hexes that may not be entered at all (e.g. occupied).

    Returns:
        A :class:`Reach`; the start hex is not included as a destination.
    """
    blocked = blocked or set()
    must_stop_fn = must_stop_fn or (lambda _hex: False)
    cost: dict[Node, int] = {start: 0}
    came_from: dict[Node, Node] = {}
    must_stop_at: set[Node] = set()
    counter = itertools.count()
    frontier: list[tuple[int, int, Node]] = [(0, next(counter), start)]

    while frontier:
        current_cost, _, current = heapq.heappop(frontier)
        if current_cost > cost.get(current, 1 << 30):
            continue
        if current in must_stop_at:
            continue  # entered, but cannot continue this phase
        for neighbor in neighbors_fn(current):
            if neighbor in blocked:
                continue
            step_cost = cost_fn(current, neighbor)
            if step_cost is None:
                continue
            new_cost = current_cost + step_cost
            if new_cost > budget:
                continue
            if new_cost < cost.get(neighbor, 1 << 30):
                cost[neighbor] = new_cost
                came_from[neighbor] = current
                if must_stop_fn(neighbor):
                    must_stop_at.add(neighbor)
                heapq.heappush(frontier, (new_cost, next(counter), neighbor))

    cost.pop(start, None)  # the start hex is not itself a "move"
    return Reach(cost=cost, came_from=came_from)
