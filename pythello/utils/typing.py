from typing import Any, Callable, Dict, Set, Tuple, Union

from pythello.ai.strategy import AI
from pythello.game import GridGame

Function = Callable[..., Any]
Move = Tuple[int, int]
Player = Union[AI, str]
Scorer = Callable[[GridGame], float]
ValidMoves = Dict[Move, Set[Move]]
