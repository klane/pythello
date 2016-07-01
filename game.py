import abc
import numpy as np
from collections import defaultdict


class GridGame(object):

    DRAW = 'Draw'

    def __init__(self, player1, player2, size, verbose=False):
        if size % 2 != 0 or size <= 0:
            raise ValueError('Enter a positive even number board dimension')

        self._players = [player2, GridGame.DRAW, player1]  # Player 1 last so a positive net score is a player 1 win
        self._size = size
        self._verbose = verbose
        self._board, self._score, self._valid, self._value, self._winner = [None] * 5
        self.reset()

    @property
    def board(self):
        return self._board

    def end_game(self):
        self._winner = self._players[np.sign(self._score[-1]) + 1]
        score = [np.count_nonzero(self._board == 1)]
        score += [score[0] - self._score[-1]]

        if self._verbose:
            print('Game over!')
            print(self._players[2], 'score:', score[0])
            print(self._players[0], 'score:', score[1])

        if self._winner is GridGame.DRAW:
            print(self._winner)
        elif self._verbose:
            print(self._winner, 'in', len(self._score) - 1, 'turns')
        else:
            print(self._winner, '%d-%d in %d turns' % (max(score), min(score), len(self._score) - 1))

    def is_over(self):
        return self._winner is not None

    def move(self, move):
        if move not in self._valid:
            raise ValueError('Invalid move')

        for piece in self._valid[move]:
            self._board[piece] = self._value

        self._score.append(self._board.sum())
        self.next_turn()

        return self

    def next_turn(self):
        self._value *= -1
        self._valid = self.valid_moves()

    def play(self):
        while not self.is_over():
            self.move(self.player.move(self))

    @property
    def player(self):
        return self._players[self._value + 1]

    @property
    def players(self):
        return self._players[2], self._players[0]

    def reset(self):
        self._value = 1
        self._board = self.starting_board()
        self._score = [0]
        self._valid = self.valid_moves()
        self._winner = None

    @property
    def score(self):
        return self._score

    @property
    def size(self):
        return self._size

    @abc.abstractmethod
    def starting_board(self):
        """Return the starting board configuration as a 2D NumPy array."""

    @property
    def valid(self):
        return self._valid

    @abc.abstractmethod
    def valid_moves(self):
        """Return a dictionary that maps valid moves to the pieces gained by the current player."""

    @property
    def value(self):
        return self._value

    @property
    def winner(self):
        return self._winner


class Othello(GridGame):

    DIRECTIONS = [np.array([i, j]) for i in [-1, 0, 1] for j in [-1, 0, 1] if (i != 0 or j != 0)]

    def __init__(self, player1, player2, size=8, verbose=False):
        super().__init__(player1, player2, size, verbose)

    def is_over(self):
        if len(self._valid) == 0:
            if self._verbose:
                print(self.player, 'has no valid moves')
                print(self._board)

            self.next_turn()

            if len(self._valid) == 0:
                if self._verbose:
                    print(self.player, 'has no valid moves')

                self.end_game()
            elif self._verbose:
                print(self.player, 'has valid moves')

        return super().is_over()

    def starting_board(self):
        board = np.zeros((self._size, self._size), dtype=np.int8)
        board[int(self._size / 2), int(self._size / 2 - 1)] = self._value
        board[int(self._size / 2 - 1), int(self._size / 2)] = self._value
        board[int(self._size / 2), int(self._size / 2)] = -self._value
        board[int(self._size / 2 - 1), int(self._size / 2 - 1)] = -self._value
        return board

    def valid_moves(self):
        valid = defaultdict(set)

        for point in zip(*np.where(self._board == self._value)):
            for direction in Othello.DIRECTIONS:
                line = self._board[[x if d == 0 else slice(x, None, d) for x, d in zip(point, direction)]]

                if len(line.shape) == 2:
                    line = line.diagonal()

                n = np.argmax(line == 0)

                if np.all(line[1:n] == -self._value) and n > 1:
                    (rows, cols) = [[x]*n if d == 0 else range(x+d, x + d*(n+1), d) for x, d in zip(point, direction)]
                    valid[tuple(point + n*direction)].update((r, c) for r, c in zip(rows, cols))

        return valid
