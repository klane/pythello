from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from pythello.game import GridGame


class EdgeScore:
    def __init__(self, size: int) -> None:
        self.board_score = np.ones((size, size), dtype=np.int8)
        self.board_score[0, :] = 3
        self.board_score[:, 0] = 3
        self.board_score[size - 1, :] = 3
        self.board_score[:, size - 1] = 3
        self.board_score[[0, 0, size - 1, size - 1], [0, size - 1, 0, size - 1]] = 9

    def __call__(self, game: GridGame) -> float:
        if game.board.num_empty > game.board.size**2 / 2:
            return int((game.board * self.board_score).score()) * game.value
        else:
            return greedy_score(game)


def greedy_score(game: GridGame) -> float:
    return game.board.score() * game.value
