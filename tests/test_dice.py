"""Injectable dice: scripted determinism and random fallback."""
from __future__ import annotations

from hexarena.dice import Dice


def test_scripted_rolls_consumed_in_order() -> None:
    dice = Dice(scripted=[3, 1, 4, 1, 5])
    assert dice.roll_n(5) == [3, 1, 4, 1, 5]


def test_total_sums_dice() -> None:
    dice = Dice(scripted=[6, 6, 5])
    assert dice.total(3) == 17


def test_feed_appends_to_queue() -> None:
    dice = Dice(scripted=[2])
    dice.feed(4, 6)
    assert dice.roll_n(3) == [2, 4, 6]


def test_falls_back_to_seeded_random_when_unscripted() -> None:
    first = Dice(seed=42).roll_n(10)
    second = Dice(seed=42).roll_n(10)
    assert first == second
    assert all(1 <= value <= 6 for value in first)


def test_scripted_then_random() -> None:
    dice = Dice(seed=1, scripted=[6])
    assert dice.roll() == 6  # scripted first
    assert 1 <= dice.roll() <= 6  # then random
