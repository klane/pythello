import numpy as np


class EdgeScore(object):
    def __init__(self, size):
        self.board_score = np.ones((size, size), dtype=np.int8)
        self.board_score[0, :] = 3
        self.board_score[:, 0] = 3
        self.board_score[size-1, :] = 3
        self.board_score[:, size-1] = 3
        self.board_score[[0, 0, size-1, size-1], [0, size-1, 0, size-1]] = 9

    def __call__(self, game):
        if np.count_nonzero(game.board == 0) > game.board.size ** 2 / 2:
            return (game.board * game.value * self.board_score).sum()
        else:
            return greedy_score(game)


def greedy_score(game):
    return game.board.score() * game.value
