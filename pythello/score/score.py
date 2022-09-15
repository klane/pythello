from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from pythello.board import Board
from pythello.score.greedy import greedy_score
from pythello.score.weighted import WeightedScore

if TYPE_CHECKING:
    from pythello.board import Color
    from pythello.utils.typing import Scorer


class ScorerWrapper:
    def __init__(self, scorer: Scorer) -> None:
        self._scorer = scorer

    def __call__(self, board: Board, player: Color) -> float:
        return self._scorer(board, player)


class Score(ScorerWrapper, Enum):
    GREEDY = ScorerWrapper(greedy_score)
    EDGE = WeightedScore(
        {
            Board.player_corners: 16,
            Board.player_edges: 4,
            lambda board, player: len(board.valid_moves(player)): 2,
            Board.player_interior: 1,
            Board.player_frontier: -1,
        }
    )
