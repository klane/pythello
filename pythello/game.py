from __future__ import annotations

from typing import TYPE_CHECKING

from pythello.board import Color

if TYPE_CHECKING:
    from pythello.board import Board, Position, PositionSet
    from pythello.player import Player


class Game:
    def __init__(
        self, player1: Player, player2: Player, board: Board, verbose: bool = False
    ) -> None:
        self._players = (player1, player2)
        self._current_player = Color.BLACK
        self._board = board
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
        return self

    def move_with_pass(self, move: Position | None = None) -> Game:
        self.move(move)

        if not self.has_move and not self.is_over:
            if self._verbose:
                print(f'Passing {self.player}')

            self.next_turn()

        return self

    def next_turn(self) -> Game:
        self._current_player = self._current_player.opponent
        self._valid = self._board.valid_moves(self._current_player)
        return self

    def peek(self, move: Position) -> Board:
        board = self._board.copy()
        board.place_piece(move, self._current_player)
        return board

    @property
    def player(self) -> Player:
        return self._players[self._current_player]

    @property
    def players(self) -> tuple[Player, Player]:
        return self._players

    def print_results(self) -> None:
        score = [self._board.player_score(color) for color in Color]
        n_turns = len(self._score) - 1

        if self._verbose:
            print('Game over!')

            for player, player_color, player_score in zip(self._players, Color, score):
                print(f'{player} ({player_color.name.lower()}) score: {player_score}')

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

    @property
    def score(self) -> list[int]:
        return self._score

    @property
    def valid(self) -> PositionSet:
        return self._valid

    @property
    def winner(self) -> Player | None:
        score = self._score[-1]

        if not self.is_over or score == 0:
            return None

        return self._players[Color.BLACK if score > 0 else Color.WHITE]
