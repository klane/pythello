import numpy as np
from collections import defaultdict
from easyAI import TwoPlayersGame


class GridGame(TwoPlayersGame):

    DRAW = 'Draw'

    def __init__(self, players, size, verbose=False):
        if size % 2 != 0 or size <= 0:
            raise ValueError('Enter a positive even number board dimension')

        self.player1 = players[0]
        self.player1.number = 1
        self.player1.value = -1
        self.player1.opponent = players[1]

        self.player2 = players[1]
        self.player2.number = 2
        self.player2.value = 1
        self.player2.opponent = players[0]

        self.players = (self.player1, self.player2)
        self.nplayer = 1
        self.player_lookup = {self.player1.value: self.player1, 0: GridGame.DRAW, self.player2.value: self.player2}

        self.size = size
        self.board = np.zeros((size, size), dtype=np.int8)

        self.score = [0]
        self.winner = None
        self.valid = {}
        self.verbose = verbose
        self.print_player = lambda p, *args: print(p, p.number, *args)

    def is_over(self):
        return self.winner is not None

    def make_move(self, move):
        if move not in self.valid:
            raise ValueError('Invalid move')

        pieces_turned = self.valid[move]

        for p in pieces_turned:
            self.board[p] = self.player.value

        self.score.append(self.board.sum())
        self.valid = self.valid_moves(self.board, self.opponent)

    def possible_moves(self):
        return list(self.valid.keys())

    def reset(self):
        self.board = np.zeros((self.size, self.size), dtype=np.int8)
        self.nplayer = 1
        self.score = [0]
        self.winner = None

    def valid_moves(self, board, player):
        pass

BOARD_SCORE = np.array([[9, 3, 3, 3, 3, 3, 3, 9],
                        [3, 1, 1, 1, 1, 1, 1, 3],
                        [3, 1, 1, 1, 1, 1, 1, 3],
                        [3, 1, 1, 1, 1, 1, 1, 3],
                        [3, 1, 1, 1, 1, 1, 1, 3],
                        [3, 1, 1, 1, 1, 1, 1, 3],
                        [3, 1, 1, 1, 1, 1, 1, 3],
                        [9, 3, 3, 3, 3, 3, 3, 9]])


class Othello(GridGame):
    def __init__(self, players, size=8, verbose=False):
        super().__init__(players, size, verbose)
        self.reset()

    def make_move(self, move):
        super().make_move(move)

        if len(self.valid) == 0:
            if self.verbose:
                self.print_player(self.opponent, 'has no valid moves')
                print(self.board)

            self.valid = self.valid_moves(self.board, self.player)

            if len(self.valid) == 0:
                if self.verbose:
                    self.print_player(self.player, 'has no valid moves')

                self.winner = self.player_lookup[np.sign(self.score[-1])]
                player1_score = np.count_nonzero(self.board == self.player1.value)

                print('Game over!')
                self.print_player(self.player1, 'score:', player1_score)
                self.print_player(self.player2, 'score:', player1_score + self.score[-1])

                if self.winner is GridGame.DRAW:
                    print(self.winner, 'in', len(self.score)-1, 'turns\n')
                else:
                    self.print_player(self.winner, 'in', len(self.score)-1, 'turns\n')
            elif self.verbose:
                self.print_player(self.player, 'has valid moves')
                self.switch_player()

    def reset(self):
        super().reset()
        self.board[int(self.size/2), int(self.size/2-1)] = self.player1.value
        self.board[int(self.size/2-1), int(self.size/2)] = self.player1.value
        self.board[int(self.size/2), int(self.size/2)] = self.player2.value
        self.board[int(self.size/2-1), int(self.size/2-1)] = self.player2.value
        self.valid = self.valid_moves(self.board, self.player)

    def scoring(self):
        if np.sum(self.board == 0) > 32:  # less than half the board is full
            player = self.board == self.nplayer
            opponent = self.board == self.nopponent
            return ((player - opponent) * BOARD_SCORE).sum()
        else:
            npieces_player = np.sum(self.board == self.nplayer)
            npieces_opponent = np.sum(self.board == self.nopponent)
            return npieces_player - npieces_opponent

    def valid_moves(self, board, player):
        moves = defaultdict(set)

        for point in zip(*np.where(board == player.value)):
            for direction in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
                line = board[[x if d == 0 else slice(x, None, d) for x, d in zip(point, direction)]]

                if len(line.shape) == 2:
                    line = line.diagonal()

                n = np.argmax(line == 0)

                if np.all(line[1:n] == player.opponent.value) and n > 1:
                    (rows, cols) = [[x]*n if d == 0 else range(x+d, x + d*(n+1), d) for x, d in zip(point, direction)]
                    moves[tuple(point + n*np.array(direction))].update((r, c) for r, c in zip(rows, cols))

        return moves
