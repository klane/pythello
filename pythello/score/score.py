from __future__ import annotations

from collections.abc import Callable
from enum import Enum

from pythello.board import Board, Color
from pythello.score.weighted import WeightedScore

Scorer = Callable[[Board, Color], float]


class ScorerWrapper:
    def __init__(self, scorer: Scorer) -> None:
        self._scorer = scorer

    def __call__(self, board: Board, player: Color) -> float:
        return self._scorer(board, player)


class Score(ScorerWrapper, Enum):
    GREEDY = ScorerWrapper(lambda board, player: board.score(player))
    EDGE = WeightedScore(
        {
            Board.player_corners: 16,
            Board.player_edges: 4,
            lambda board, player: len(board.valid_moves(player)): 2,
            Board.player_interior: 1,
            Board.player_frontier: -1,
        }
    )
