from __future__ import annotations

from collections.abc import Callable
from typing import Any, Union

from pythello.board import Board, Color
from pythello.game import Game

Function = Callable[..., Any]
Predicate = Callable[..., bool]
IntPredicate = Callable[[int], bool]
Position = int
PositionSet = set[Position]
AIPlayer = Callable[[Game], Position]
Player = Union[AIPlayer, str]
Scorer = Callable[[Board, Color], float]
