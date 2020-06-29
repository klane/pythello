from typing import Any, Callable, Set, Tuple, Union

from pythello.ai.strategy import AI
from pythello.game import GridGame

Function = Callable[..., Any]
IntPredicate = Callable[[int], bool]
Move = Tuple[int, int]
Player = Union[AI, str]
Scorer = Callable[[GridGame], float]
ValidMoves = Set[Move]
