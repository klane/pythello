from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from pythello.score.greedy import greedy_score
from pythello.score.weighted import WeightedScore

if TYPE_CHECKING:
    from pythello.board import Board
    from pythello.player import Color
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
            lambda board, player: board.player_corners(player): 16,
            lambda board, player: board.player_edges(player): 4,
            lambda board, player: len(board.valid_moves(player)): 2,
            lambda board, player: board.player_interior(player): 1,
            lambda board, player: board.player_frontier(player): -1,
        }
    )
