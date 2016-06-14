import numpy as np
from collections import defaultdict


class GridGame(object):

    DRAW = 'Draw'

    def __init__(self, player1, player2, size, verbose=False):
        if size % 2 != 0 or size <= 0:
            raise ValueError('Enter a positive even number board dimension')

        self.player1 = player1
        self.player1.number = 1
        self.player1.value = -1
        self.player1.opponent = player2

        self.player2 = player2
        self.player2.number = 2
        self.player2.value = 1
        self.player2.opponent = player1

        self.players = {self.player1.value: self.player1, 0: GridGame.DRAW, self.player2.value: self.player2}
        self.current_player = self.player1

        self.size = size
        self.board = np.zeros((size, size), dtype=np.int8)

        self.moves = 0
        self.score = [0]
        self.winner = None
        self.valid = []
        self.verbose = verbose
        self.print_player = lambda p, *args: print(p, p.number, *args)

    def game_over(self):
        return self.winner is not None

    def move(self, player, move=None):
        if player is not self.current_player:
            raise ValueError('Wrong player')

        if move is None:
            move = player.move(self.valid)

        if move not in self.valid:
            raise ValueError('Invalid move')

        pieces_turned = self.valid[move]

        for p in pieces_turned:
            self.board[p] = self.current_player.value

        self.moves += 1
        self.score.append(self.board.sum())
        self.next_turn()

    def next_turn(self):
        self.current_player = self.current_player.opponent
        self.valid = self.valid_moves(self.board, self.current_player)

    def play(self):
        while not self.game_over():
            self.move(self.current_player)

    def reset(self):
        self.board = np.zeros((self.size, self.size), dtype=np.int8)
        self.current_player = self.player1
        self.moves = 0
        self.score = [0]
        self.winner = None

    def valid_moves(self, board, player):
        pass


class Othello(GridGame):
    def __init__(self, player1, player2, size=8, verbose=False):
        super().__init__(player1, player2, size, verbose)
        self.reset()

    def move(self, player, move=None):
        super().move(player, move)

        if len(self.valid) == 0:
            if self.verbose:
                self.print_player(self.current_player, 'has no valid moves')
                print(self.board)

            self.next_turn()

            if len(self.valid) == 0:
                if self.verbose:
                    self.print_player(self.current_player, 'has no valid moves')

                self.winner = self.players[np.sign(self.score[-1])]
                player1_score = np.count_nonzero(self.board == self.player1.value)

                print('Game over!')
                self.print_player(self.player1, 'score:', player1_score)
                self.print_player(self.player2, 'score:', player1_score+self.score[-1])

                if self.winner is GridGame.DRAW:
                    print(self.winner, 'in', self.moves, 'turns\n')
                else:
                    self.print_player(self.winner, 'in', self.moves, 'turns\n')
            elif self.verbose:
                self.print_player(self.current_player, 'has valid moves')

    def reset(self):
        super().reset()
        self.board[int(self.size/2), int(self.size/2-1)] = self.player1.value
        self.board[int(self.size/2-1), int(self.size/2)] = self.player1.value
        self.board[int(self.size/2), int(self.size/2)] = self.player2.value
        self.board[int(self.size/2-1), int(self.size/2-1)] = self.player2.value
        self.valid = self.valid_moves(self.board, self.current_player)

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
