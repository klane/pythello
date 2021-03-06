from typing import Any, Callable, Set, Tuple, Union

from pythello.ai.strategy import AI
from pythello.game import GridGame

Function = Callable[..., Any]
IntPredicate = Callable[[int], bool]
Player = Union[AI, str]
Position = Tuple[int, int]
PositionSet = Set[Position]
Scorer = Callable[[GridGame], float]
