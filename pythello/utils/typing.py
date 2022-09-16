from __future__ import annotations

from collections.abc import Callable
from typing import Union

from pythello.game import Game

Position = int
PositionSet = set[Position]
AIPlayer = Callable[[Game], Position]
Player = Union[AIPlayer, str]
Scorer = Callable[[Game], float]
