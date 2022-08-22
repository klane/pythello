from __future__ import annotations

from typing import Any, Callable, Union

from pythello.ai.strategy import AI
from pythello.game import GridGame

Function = Callable[..., Any]
IntPredicate = Callable[[int], bool]
Player = Union[AI, str]
Position = tuple[int, int]
PositionSet = set[Position]
Scorer = Callable[[GridGame], float]
