from collections import defaultdict

import numpy as np

from pythello.board.board import Board


class GridBoard(Board):

    DIRECTIONS = [(i, j) for i in [-1, 0, 1] for j in [-1, 0, 1] if (i != 0 or j != 0)]
    DIRECTIONS = [np.array([i, j]) for i, j in DIRECTIONS]

    def __init__(self, size=8, board=None):
        super().__init__(size)

        if board is None:
            self._board = np.zeros((self._size, self._size), dtype=np.int8)
            self.reset()
        else:
            self._board = board

    def __mul__(self, other):
        return GridBoard(board=self._board * other)

    def get_pieces(self, player):
        pieces = np.nonzero(self._board == player)
        return {(row, col) for row, col in zip(*pieces)}

    @property
    def num_empty(self):
        return np.count_nonzero(self._board == 0)

    def place_piece(self, piece, player):
        self._board[piece] = player

    def player_score(self, player):
        return np.count_nonzero(self._board == player)

    def reset(self):
        mid = int(self._size / 2)
        self._board.fill(0)
        self._board[mid, mid - 1] = 1
        self._board[mid - 1, mid] = 1
        self._board[mid, mid] = -1
        self._board[mid - 1, mid - 1] = -1

    def score(self):
        return self._board.sum()

    def valid_moves(self, player):
        valid = defaultdict(set)

        for pt in zip(*np.where(self._board == player)):
            for dir in GridBoard.DIRECTIONS:
                index = [x if d == 0 else slice(x, None, d) for x, d in zip(pt, dir)]
                line = self._board[tuple(index)]

                if len(line.shape) == 2:
                    line = line.diagonal()

                n = np.argmax(line == 0)

                if np.all(line[1:n] == -player) and n > 1:
                    pieces = [tuple(pt + i * dir) for i in range(1, n + 1)]
                    valid[pieces[-1]].update(pieces)

        return valid
