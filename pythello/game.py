import numpy as np


class GridGame(object):

    DRAW = 'Draw'

    def __init__(self, player1, player2, board, verbose=False):
        self._players = (player2, GridGame.DRAW, player1)  # Player 1 last so a positive net score is a player 1 win
        self._board = board
        self._verbose = verbose
        self._score, self._valid, self._value, self._winner = [None] * 4
        self.reset()

    @property
    def board(self):
        return self._board

    def end_game(self):
        self._winner = self._players[np.sign(self._score[-1]) + 1]
        score = [self._board.player_score(1)]
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
            self._board.place_piece(piece, self._value)

        self._score.append(self._board.score())
        self.next_turn()
        return self

    def next_turn(self):
        self._value *= -1
        self._valid = self._board.valid_moves()

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
        self._board.reset()
        self._score = [0]
        self._valid = self._board.valid_moves()
        self._winner = None

    @property
    def score(self):
        return self._score

    @property
    def valid(self):
        return self._valid

    @property
    def value(self):
        return self._value

    @property
    def winner(self):
        return self._winner


class Othello(GridGame):

    DIRECTIONS = [np.array([i, j]) for i in [-1, 0, 1] for j in [-1, 0, 1] if (i != 0 or j != 0)]

    def __init__(self, player1, player2, board, verbose=False):
        super().__init__(player1, player2, board, verbose)

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
