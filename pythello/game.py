from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, NamedTuple

from pythello.board import Color

if TYPE_CHECKING:
    from pythello.board import Board, Position, PositionSet
    from pythello.player import Player


class AssignedPlayer(NamedTuple):
    player: Player
    color: Color

    def __repr__(self) -> str:
        return f'{self.player} ({self.color.name.lower()})'


class Result(Enum):
    WIN = 1
    LOSS = 2
    DRAW = 3


class Game:
    def __init__(
        self,
        board: Board,
        player1: Player = 'Player 1',
        player2: Player = 'Player 2',
        verbose: bool = False,
    ) -> None:
        self._board = board
        self._players = (
            AssignedPlayer(player1, Color.BLACK),
            AssignedPlayer(player2, Color.WHITE),
        )
        self._current_player = Color.BLACK
        self._verbose = verbose
        self._valid = self._board.valid_moves(self._current_player)
        self._score = [0]

    @property
    def board(self) -> Board:
        return self._board

    def captured(self, move: Position) -> PositionSet:
        return self._board.captured(self._current_player, move)

    @property
    def current_player(self) -> Color:
        return self._current_player

    @property
    def has_move(self) -> bool:
        return len(self._valid) > 0

    @property
    def is_over(self) -> bool:
        if self._board.is_full:
            return True

        if not self.has_move:
            next_player = self._current_player.opponent
            return len(self._board.valid_moves(next_player)) == 0

        return False

    def move(self, move: Position | None = None) -> Game:
        if move is None:
            if callable(self.player):
                move = self.player(self)
            else:
                raise ValueError('Must provide move if current player is not an AI')

        if move not in self._valid:
            raise ValueError(f'Invalid move: {move}')

        self._board.place_piece(move, self._current_player)
        self._score.append(self._board.score())
        self.next_turn()

        if not self.has_move and not self.is_over:
            if self._verbose:
                print(f'Passing {self.player}')

            self.next_turn()

        return self

    def next_turn(self) -> Game:
        self._current_player = self._current_player.opponent
        self._valid = self._board.valid_moves(self._current_player)
        return self

    @property
    def player(self) -> Player:
        return self._players[self._current_player].player

    @property
    def players(self) -> tuple[Player, Player]:
        return (player.player for player in self._players)

    def print_results(self) -> None:
        score = [self._board.player_score(player.color) for player in self._players]
        n_turns = len(self._score) - 1

        if self._verbose:
            print('Game over!')

            for player, player_score in zip(self._players, score):
                print(f'{player} score: {player_score}')

        if self.winner is None:
            print('Draw')
        elif self._verbose:
            print(f'{self.winner} in {n_turns} turns')
        else:
            print(f'{self.winner} {max(score)}-{min(score)} in {n_turns} turns')

    def reset(self) -> Game:
        self._current_player = Color.BLACK
        self._board.reset()
        self._score = [0]
        self._valid = self._board.valid_moves(self._current_player)
        return self

    def result(self, player: Color) -> Result | None:
        if not self.is_over:
            return None

        winner = self.winner

        if winner is None:
            return Result.DRAW

        return Result.WIN if player is winner else Result.LOSS

    @property
    def score(self) -> list[int]:
        return self._score

    @property
    def valid(self) -> PositionSet:
        return self._valid

    @property
    def winner(self) -> AssignedPlayer | None:
        score = self._score[-1]

        if not self.is_over or score == 0:
            return None

        return self._players[Color.BLACK if score > 0 else Color.WHITE]
