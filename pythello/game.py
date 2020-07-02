from __future__ import annotations

from typing import TYPE_CHECKING, List, NamedTuple, Optional, Tuple

from pythello.ai.strategy import AI

if TYPE_CHECKING:
    from pythello.board.board import Board
    from pythello.utils.typing import Player, Position, PositionSet


class AssignedPlayer(NamedTuple):
    player: Player
    value: int


class GridGame:
    def __init__(
        self, player1: Player, player2: Player, board: Board, verbose: bool = False
    ):
        self._players = (AssignedPlayer(player1, 1), AssignedPlayer(player2, -1))
        self._board = board
        self._verbose = verbose
        self._index = 0
        self._valid = self._board.valid_moves(self.value)
        self._score = [0]

    @property
    def board(self) -> Board:
        return self._board

    def captured(self, move: Position) -> PositionSet:
        return self._board.captured(self.value, move)

    @property
    def has_move(self) -> bool:
        return len(self._valid) > 0

    @property
    def is_over(self) -> bool:
        if self._board.is_full:
            return True

        if not self.has_move:
            next_player = self._players[self._index ^ 1].value
            return len(self._board.valid_moves(next_player)) == 0

        return False

    def move(self, move: Optional[Position] = None) -> GridGame:
        if move is None:
            if isinstance(self.player, AI):
                move = self.player.move(self)
            else:
                raise ValueError('Must provide move if current player is not an AI')

        if move not in self._valid:
            raise ValueError(f'Invalid move: {move}')

        self._board.place_piece(move, self.value)
        self._score.append(self._board.score())
        self.next_turn()
        return self

    def next_turn(self) -> GridGame:
        self._index ^= 1
        self._valid = self._board.valid_moves(self.value)
        return self

    @property
    def player(self) -> Player:
        return self._players[self._index].player

    @property
    def players(self) -> Tuple[Player, Player]:
        return self._players[0].player, self._players[1].player

    def print_results(self) -> None:
        score = [self._board.player_score(p.value) for p in self._players]
        n_turns = len(self._score) - 1

        if self._verbose:
            print('Game over!')
            print(self._players[0].player, 'score:', score[0])
            print(self._players[1].player, 'score:', score[1])

        if self.winner is None:
            print('Draw')
        elif self._verbose:
            print(self.winner, 'in', n_turns, 'turns')
        else:
            print(f'{self.winner} {max(score)}-{min(score)} in {n_turns} turns')

    def reset(self) -> GridGame:
        self._index = 0
        self._board.reset()
        self._score = [0]
        self._valid = self._board.valid_moves(self.value)
        return self

    @property
    def score(self) -> List[int]:
        return self._score

    @property
    def valid(self) -> PositionSet:
        return self._valid

    @property
    def value(self) -> int:
        return self._players[self._index].value

    @property
    def winner(self) -> Optional[Player]:
        score = self._score[-1]

        if not self.is_over or score == 0:
            return None

        sign = bool(score > 0) - bool(score < 0)
        return next(p.player for p in self._players if p.value == sign)


class Othello(GridGame):
    def move_with_pass(self, move: Optional[Position] = None) -> GridGame:
        self.move(move)

        if not self.has_move and not self.is_over:
            if self._verbose:
                print(f'Passing {self.player}')

            self.next_turn()

        return self
