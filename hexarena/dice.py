"""Injectable six-sided dice, shared across games.

A single :class:`Dice` instance is the only source of randomness an engine
should touch, so combat can be made fully deterministic in tests by feeding a
scripted sequence of rolls. When the scripted queue is empty it falls back to a
seeded ``random.Random``.

Different games consume dice differently -- Ogre reads single d6 results off a
Combat Results Table, while Melee sums three dice for a roll-under-DX check and
rolls weapon damage as ``Nd6 + modifier`` -- so this exposes both single-die and
multi-die helpers.
"""
from __future__ import annotations

import random
from collections import deque
from typing import Iterable


class Dice:
    """A d6 source. Pass ``scripted`` rolls for deterministic tests."""

    def __init__(
        self,
        seed: int | None = None,
        scripted: Iterable[int] | None = None,
    ) -> None:
        self._rng = random.Random(seed)
        self._scripted: deque[int] = deque(scripted or [])

    def roll(self) -> int:
        """One d6: the next scripted value, or a fresh random 1-6."""
        if self._scripted:
            return self._scripted.popleft()
        return self._rng.randint(1, 6)

    def roll_n(self, count: int) -> list[int]:
        """A list of ``count`` individual d6 results."""
        return [self.roll() for _ in range(count)]

    def total(self, count: int) -> int:
        """The summed total of ``count`` d6 (e.g. a 3d6 roll-under check)."""
        return sum(self.roll_n(count))

    def feed(self, *rolls: int) -> None:
        """Append scripted rolls to the queue (consumed before random)."""
        self._scripted.extend(rolls)
