from __future__ import annotations

from typing import Any, Callable

from pythello.ai.strategy import AI
from pythello.game import GridGame

Function = Callable[..., Any]
IntPredicate = Callable[[int], bool]
Player = AI | str
Position = tuple[int, int]
PositionSet = set[Position]
Scorer = Callable[[GridGame], float]
