import numpy as np
from collections import defaultdict
from pythello.board.board import Board


class GridBoard(Board):

    DIRECTIONS = [np.array([i, j]) for i in [-1, 0, 1] for j in [-1, 0, 1] if (i != 0 or j != 0)]

    def __init__(self, size=8):
        super().__init__(size)
        self._board = np.zeros((self._size, self._size), dtype=np.int8)

    def get_pieces(self, player):
        return np.nonzero(self._board == player)

    def place_piece(self, piece, player):
        self._board[piece] = player

    def player_score(self, player):
        return np.count_nonzero(self._board == player)

    def reset(self):
        mid = int(self._size / 2)
        self._board.fill(0)
        self._board[mid, mid-1] = 1
        self._board[mid-1, mid] = 1
        self._board[mid, mid] = -1
        self._board[mid-1, mid-1] = -1

    def score(self):
        return self._board.sum()

    def valid_moves(self, player):
        valid = defaultdict(set)

        for point in zip(*np.where(self._board == player)):
            for direction in GridBoard.DIRECTIONS:
                line = self._board[tuple([x if d == 0 else slice(x, None, d) for x, d in zip(point, direction)])]

                if len(line.shape) == 2:
                    line = line.diagonal()

                n = np.argmax(line == 0)

                if np.all(line[1:n] == -player) and n > 1:
                    (rows, cols) = [[x]*n if d == 0 else range(x+d, x + d*(n+1), d) for x, d in zip(point, direction)]
                    valid[tuple(point + n*direction)].update((r, c) for r, c in zip(rows, cols))

        return valid
