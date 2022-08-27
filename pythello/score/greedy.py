from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pythello.game import GridGame


def greedy_score(game: GridGame) -> float:
    return game.board.score() * game.value
