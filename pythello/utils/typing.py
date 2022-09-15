from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar, Union

from pythello.game import Game

T = TypeVar('T')

Function = Callable[..., T]
Predicate = Function[bool]
Position = int
PositionSet = set[Position]
AIPlayer = Callable[[Game], Position]
Player = Union[AIPlayer, str]
Scorer = Callable[[Game], float]
