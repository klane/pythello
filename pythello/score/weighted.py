from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pythello.board import Board
    from pythello.player import Color
    from pythello.utils.typing import Scorer


class WeightedScore:
    def __init__(self, scorers: dict[Scorer, float]) -> None:
        self.scorers = scorers.copy()

    def __call__(self, board: Board, player: Color) -> float:
        opponent = player.opponent
        return sum(
            (scorer(board, player) - scorer(board, opponent)) * weight
            for scorer, weight in self.scorers.items()
        )
