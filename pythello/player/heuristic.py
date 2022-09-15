from __future__ import annotations

import random
from collections import defaultdict
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pythello.game import Game
    from pythello.utils.typing import Position, Scorer


class Heuristic:
    def __init__(self, scorer: Scorer) -> None:
        self.scorer = scorer

    def __call__(self, game: Game) -> Position:
        scores = defaultdict(list)

        for move in game.valid:
            board = game.peek(move)
            scores[self.scorer(board, game.current_player)].append(move)

        return random.choice(scores[max(scores.keys())])
