import numpy as np

direction = ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1))


class GridGame(object):

    DRAW = 'Draw'

    def __init__(self, size, player1, player2, verbose=False):
        if size % 2 != 0 or size <= 0:
            raise ValueError('Enter a positive even number board dimension')

        player1.number = 1
        player1.value = -1
        player1.opponent = player2

        player2.number = 2
        player2.value = 1
        player2.opponent = player1

        self.players = (player1, GridGame.DRAW, player2)
        self.current_player = player1

        self.size = size
        self.board = np.zeros((size, size), dtype=np.int8)

        self.moves = 0
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
        self.next_turn()

    def next_turn(self):
        self.current_player = self.current_player.opponent
        self.valid = self.valid_moves(self.board, self.current_player)

    def play(self):
        while not self.game_over():
            self.move(self.current_player)

    def reset(self):
        self.board = np.zeros((self.size, self.size), dtype=np.int8)
        self.current_player = self.players[0]
        self.moves = 0
        self.winner = None

    def valid_moves(self, board, player):
        pass


class Othello(GridGame):
    def __init__(self, size, player1, player2, verbose=False):
        super().__init__(size, player1, player2, verbose)
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

                net_score = np.sum(self.board)
                self.winner = self.players[np.sign(net_score)+1]
                player1_score = np.count_nonzero(self.board == self.players[0].value)

                print('Game over!')
                self.print_player(self.players[0], 'score:', player1_score)
                self.print_player(self.players[2], 'score:', player1_score+net_score)

                if self.winner is GridGame.DRAW:
                    print(self.winner, 'in', self.moves, 'turns\n')
                else:
                    self.print_player(self.winner, 'in', self.moves, 'turns\n')
            elif self.verbose:
                self.print_player(self.current_player, 'has valid moves')

    def pieces_turned(self, board, player, point):
        final = [tuple(point)]

        for d in direction:
            temp = point + d
            if min(temp) >= 0 and max(temp) < self.size and board[temp[0], temp[1]] == player.opponent.value:
                points = [tuple(temp)]

                while board[points[-1]] == player.opponent.value:
                    temp = (points[-1][0]+d[0], points[-1][1]+d[1])
                    if min(temp) < 0 or max(temp) >= self.size:
                        break
                    points.append(temp)

                if board[points[-1][0], points[-1][1]] == player.value:
                    for p in points[0:-1]:
                        final.append(p)

        return final

    def reset(self):
        super().reset()
        self.board[int(self.size/2), int(self.size/2-1)] = self.players[0].value
        self.board[int(self.size/2-1), int(self.size/2)] = self.players[0].value
        self.board[int(self.size/2), int(self.size/2)] = self.players[2].value
        self.board[int(self.size/2-1), int(self.size/2-1)] = self.players[2].value
        self.valid = self.valid_moves(self.board, self.current_player)

    def valid_moves(self, board, player):
        index = np.where(board == player.opponent.value)
        moves = {}

        for r, c in zip(index[0], index[1]):
            for d in direction:
                point = np.array([r, c]) + d
                if min(point) >= 0 and max(point) < self.size and board[tuple(point)] == 0:
                    final = self.pieces_turned(board, player, point)

                    if len(final) > 1:
                        if tuple(point) in moves.keys():
                            for p in final:
                                if p not in moves[tuple(point)]:
                                    moves[tuple(point)].append(p)
                        else:
                            moves[tuple(point)] = final

        return moves
