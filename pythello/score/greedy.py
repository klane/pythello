from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pythello.game import Game


def greedy_score(game: Game) -> float:
    return game.board.score(game.current_player)
