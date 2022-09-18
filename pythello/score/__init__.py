from collections.abc import Callable

from pythello.game import Game

from .edge import EdgeScore
from .greedy import greedy_score

Scorer = Callable[[Game], float]

__all__ = ['EdgeScore', 'Scorer', 'greedy_score']
