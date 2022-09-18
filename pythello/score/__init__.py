from collections.abc import Callable

from pythello.game import Game

from .edge import EdgeScore
from .greedy import greedy_score
from .score import Score
from .weighted import WeightedScore

Scorer = Callable[[Game], float]

__all__ = ['EdgeScore', 'Score', 'Scorer', 'WeightedScore', 'greedy_score']
