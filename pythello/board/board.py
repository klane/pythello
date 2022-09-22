from __future__ import annotations

from operator import lshift, rshift
from typing import TYPE_CHECKING, NamedTuple

from pythello.board import mask as board_mask
from pythello.board.color import Color
from pythello.board.position import split_position

if TYPE_CHECKING:
    from collections.abc import Callable

    from pythello.board.position import Position, PositionSet


class Shift(NamedTuple):
    operator: Callable[[int, int], int]
    bits: int


class Board:
    def __init__(self, size: int = 8) -> None:
        if size <= 0 or size % 2 != 0:
            raise ValueError('Board size must be a positive even integer')

        self._size = size
        self.players: list[int] = []

        right_mask = board_mask.right_mask(size)
        left_mask = board_mask.left_mask(size)
        self._corner_mask = board_mask.corner_mask(size)
        self._edge_mask = board_mask.edge_mask(size, remove_corners=True)
        self._full_mask = board_mask.full_mask(size)
        self._interior_mask = board_mask.interior_mask(size)

        self._masks = (
            right_mask,  # right
            right_mask >> size,  # down + right
            self._full_mask,  # down
            left_mask >> size,  # down + left
            left_mask,  # left
            (left_mask << size) & self._full_mask,  # up + left
            self._full_mask,  # up
            (right_mask << size) & self._full_mask,  # up + right
        )

        self._shifts = (
            Shift(rshift, 1),  # right
            Shift(rshift, size + 1),  # down + right
            Shift(rshift, size),  # down
            Shift(rshift, size - 1),  # down + left
            Shift(lshift, 1),  # left
            Shift(lshift, size + 1),  # up + left
            Shift(lshift, size),  # up
            Shift(lshift, size - 1),  # up + right
        )

        self.reset()

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Board):
            return self.players == other.players

        return False

    def __hash__(self) -> int:
        """Get board hash code"""
        return hash(tuple(self.players))

    def _captured(self, player: Color, move: Position) -> tuple[int, int, int]:
        current = self.players[player]
        opponent = self.players[player.opponent]
        captured = move

        for shift, mask in zip(self._shifts, self._masks):
            current_mask = mask & current
            opponent_mask = mask & opponent
            x = shift.operator(move, shift.bits) & opponent_mask

            for _ in range(self._size - 3):
                x |= shift.operator(x, shift.bits) & opponent_mask

            if (shift.operator(x, shift.bits) & current_mask) != 0:
                captured |= x

        current |= captured
        opponent &= ~captured
        return current, opponent, captured

    def captured(self, player: Color, move: Position) -> PositionSet:
        """Get all pieces captured for the given move by the specified player."""
        _, _, captured = self._captured(player, move)
        return split_position(captured)

    def copy(self) -> Board:
        board = Board(self._size)
        board.players = self.players.copy()
        return board

    @property
    def filled(self) -> int:
        return self.players[Color.BLACK] | self.players[Color.WHITE]

    @property
    def is_full(self) -> bool:
        """Check if the board is full."""
        return self.filled == self._full_mask

    @property
    def num_empty(self) -> int:
        """Return the number of empty spaces on the board."""
        return (self.filled ^ self._full_mask).bit_count()

    def peek(self, move: Position, player: Color) -> Board:
        board = self.copy()
        board.place_piece(move, player)
        return board

    def place_piece(self, piece: Position, player: Color) -> None:
        """Place a piece on the board for the specified player."""
        current, opponent, _ = self._captured(player, piece)
        self.players[player] = current
        self.players[player.opponent] = opponent

    def player_corners(self, player: Color) -> int:
        return (self.players[player] & self._corner_mask).bit_count()

    def player_edges(self, player: Color) -> int:
        return (self.players[player] & self._edge_mask).bit_count()

    def player_frontier(self, player: Color) -> int:
        current = self.players[player]
        opponent = self.players[player.opponent]
        empty = (current | opponent) ^ self._full_mask
        frontier = 0

        for shift, mask in zip(self._shifts, self._masks):
            x = shift.operator(empty, shift.bits) & mask
            frontier |= x & current

        frontier &= ~self._corner_mask
        return frontier.bit_count()

    def player_interior(self, player: Color) -> int:
        return (self.players[player] & self._interior_mask).bit_count()

    def player_pieces(self, player: Color) -> PositionSet:
        """Get all pieces on the board for the specified player."""
        return split_position(self.players[player])

    def player_score(self, player: Color) -> int:
        """Return the number of pieces held by the specified player."""
        return self.players[player].bit_count()

    def reset(self) -> None:
        """Reset the board to its initial state."""
        mid = self._size**2 // 2
        size_2 = self._size // 2

        self.players = [0, 0]
        self.players[Color.BLACK] |= 1 << (mid - size_2)
        self.players[Color.BLACK] |= 1 << (mid + size_2 - 1)
        self.players[Color.WHITE] |= 1 << (mid - size_2 - 1)
        self.players[Color.WHITE] |= 1 << (mid + size_2)

    def score(self, player: Color = Color.BLACK) -> int:
        """Return the current score of the game."""
        return self.player_score(player) - self.player_score(player.opponent)

    @property
    def size(self) -> int:
        return self._size

    def valid_moves(self, player: Color) -> PositionSet:
        """Return the set of valid moves for the specified player."""
        current = self.players[player]
        opponent = self.players[player.opponent]
        empty = (current | opponent) ^ self._full_mask
        moves = 0

        for shift, mask in zip(self._shifts, self._masks):
            opponent_mask = mask & opponent
            empty_mask = mask & empty
            x = shift.operator(current, shift.bits) & opponent_mask

            for _ in range(self._size - 3):
                x |= shift.operator(x, shift.bits) & opponent_mask

            moves |= shift.operator(x, shift.bits) & empty_mask

        return split_position(moves)
