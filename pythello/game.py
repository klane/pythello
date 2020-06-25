from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional, Tuple

from pythello.ai.strategy import AI

if TYPE_CHECKING:
    from pythello.board.board import Board
    from pythello.utils.typing import Move, Player, ValidMoves

DRAW = 'Draw'


class GridGame:
    def __init__(
        self, player1: Player, player2: Player, board: Board, verbose: bool = False
    ):
        # player 1 last so a positive net score is a player 1 win
        self._players = (player2, DRAW, player1)
        self._board = board
        self._verbose = verbose
        self._value = 1
        self._valid = self._board.valid_moves(self._value)
        self._score = [0]

    @property
    def board(self) -> Board:
        return self._board

    def end_game(self) -> None:
        score = [self._board.player_score(1)]
        score += [score[0] - self._score[-1]]
        n_turns = len(self._score) - 1

        if self._verbose:
            print('Game over!')
            print(self._players[2], 'score:', score[0])
            print(self._players[0], 'score:', score[1])

        if self.winner is DRAW:
            print(self.winner)
        elif self._verbose:
            print(self.winner, 'in', n_turns, 'turns')
        else:
            print(f'{self.winner} {max(score)}-{min(score)} in {n_turns} turns')

    @property
    def is_over(self) -> bool:
        return len(self._valid) == 0

    def move(self, move: Optional[Move] = None) -> GridGame:
        if move is None:
            if isinstance(self.player, AI):
                move = self.player.move(self)
            else:
                raise ValueError('Must provide move if current player is not an AI')

        if move not in self._valid:
            raise ValueError(f'Invalid move: {move}')

        for piece in self._valid[move]:
            self._board.place_piece(piece, self._value)

        self._score.append(self._board.score())
        self.next_turn()
        return self

    def next_turn(self) -> None:
        self._value *= -1
        self._valid = self._board.valid_moves(self._value)

    @property
    def player(self) -> Player:
        return self._players[self._value + 1]

    @property
    def players(self) -> Tuple[Player, Player]:
        return self._players[2], self._players[0]

    def reset(self) -> None:
        self._value = 1
        self._board.reset()
        self._score = [0]
        self._valid = self._board.valid_moves(self._value)

    @property
    def score(self) -> List[int]:
        return self._score

    @property
    def valid(self) -> ValidMoves:
        return self._valid

    @property
    def value(self) -> int:
        return self._value

    @property
    def winner(self) -> Optional[Player]:
        if not self.is_over:
            return None

        score = self._score[-1]
        sign = bool(score > 0) - bool(score < 0)
        return self._players[sign + 1]


class Othello(GridGame):
    def next_turn(self) -> None:
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
