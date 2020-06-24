class GridGame:

    DRAW = 'Draw'

    def __init__(self, player1, player2, board, verbose=False):
        # player 1 last so a positive net score is a player 1 win
        self._players = (player2, GridGame.DRAW, player1)
        self._board = board
        self._verbose = verbose
        self._value = 1
        self._valid = self._board.valid_moves(self._value)
        self._score = [0]

    @property
    def board(self):
        return self._board

    def end_game(self):
        score = [self._board.player_score(1)]
        score += [score[0] - self._score[-1]]
        n_turns = len(self._score) - 1

        if self._verbose:
            print('Game over!')
            print(self._players[2], 'score:', score[0])
            print(self._players[0], 'score:', score[1])

        if self.winner is GridGame.DRAW:
            print(self.winner)
        elif self._verbose:
            print(self.winner, 'in', n_turns, 'turns')
        else:
            print(f'{self.winner} {max(score)}-{min(score)} in {n_turns} turns')

    def is_over(self):
        return len(self._valid) == 0

    def move(self, move):
        if move not in self._valid:
            raise ValueError(f'Invalid move: {move}')

        for piece in self._valid[move]:
            self._board.place_piece(piece, self._value)

        self._score.append(self._board.score())
        self.next_turn()
        return self

    def next_turn(self):
        self._value *= -1
        self._valid = self._board.valid_moves(self._value)

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
        self._valid = self._board.valid_moves(self._value)

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
        if not self.is_over():
            return None

        score = self._score[-1]
        sign = bool(score > 0) - bool(score < 0)
        return self._players[sign + 1]


class Othello(GridGame):
    def __init__(self, player1, player2, board, verbose=False):
        super().__init__(player1, player2, board, verbose)

    def next_turn(self):
        super().next_turn()

        if len(self._valid) == 0:
            if self._verbose:
                print(self.player, 'has no valid moves')
                print(self._board)

            super().next_turn()

            if len(self._valid) == 0:
                if self._verbose:
                    print(self.player, 'has no valid moves')

                self.end_game()
            elif self._verbose:
                print(self.player, 'has valid moves')
