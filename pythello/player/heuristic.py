from __future__ import annotations

import random
from collections import defaultdict
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pythello.board import Position
    from pythello.game import Game
    from pythello.score import Scorer


class Heuristic:
    def __init__(self, scorer: Scorer) -> None:
        self.scorer = scorer

    def __call__(self, game: Game) -> Position:
        scores = defaultdict(list)
        player = game.current_player.color

        for move in game.valid:
            board = game.board.peek(move, player)
            scores[self.scorer(board, player)].append(move)

        return random.choice(scores[max(scores.keys())])
