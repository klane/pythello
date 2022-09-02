from __future__ import annotations

from collections.abc import Callable
from typing import Any, Union

from pythello.game import Game

Function = Callable[..., Any]
Predicate = Callable[..., bool]
IntPredicate = Callable[[int], bool]
Position = tuple[int, int]
PositionSet = set[Position]
AI = Callable[[Game], Position]
Player = Union[AI, str]
Scorer = Callable[[Game], float]
