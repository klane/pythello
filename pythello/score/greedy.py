from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pythello.board import Board
    from pythello.player import Color


def greedy_score(board: Board, player: Color) -> float:
    return board.score(player)
