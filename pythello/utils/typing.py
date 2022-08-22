from __future__ import annotations

from collections.abc import Callable
from typing import Any

from pythello.ai.strategy import AI
from pythello.game import GridGame

Function = Callable[..., Any]
IntPredicate = Callable[[int], bool]
Player = AI | str
Position = tuple[int, int]
PositionSet = set[Position]
Scorer = Callable[[GridGame], float]
