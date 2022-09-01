from __future__ import annotations

from operator import lshift, rshift
from typing import TYPE_CHECKING, NamedTuple

from pythello.board.mask import full_mask, left_mask, right_mask
from pythello.utils.precondition import precondition

if TYPE_CHECKING:
    from collections.abc import Callable

    from pythello.utils.typing import IntPredicate, Position, PositionSet

SIZE_POSITIVE_EVEN: IntPredicate = lambda size: size > 0 and size % 2 == 0


class Shift(NamedTuple):
    operator: Callable[[int, int], int]
    nbits: int


@precondition(SIZE_POSITIVE_EVEN, 'Board size must be a positive even integer')
class Board:
    def __init__(self, size: int = 8) -> None:
        self._size = size
        self.players: dict[int, int] = {}

        _right_mask = right_mask(size)
        _left_mask = left_mask(size)
        self._full_mask = full_mask(size)

        self._masks = (
            _right_mask,  # right
            _right_mask >> size,  # down + right
            self._full_mask,  # down
            _left_mask >> size,  # down + left
            _left_mask,  # left
            (_left_mask << size) & self._full_mask,  # up + left
            self._full_mask,  # up
            (_right_mask << size) & self._full_mask,  # up + right
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
        return (self.players[1], self.players[-1]).__hash__()

    def _captured(self, player: int, move: Position) -> tuple[int, int, int]:
        current = self.players[player]
        opponent = self.players[-player]
        index = move[0] * self._size + move[1]
        mv = 1 << (self._size**2 - index - 1)
        captured = mv

        for shift, mask in zip(self._shifts, self._masks):
            current_mask = mask & current
            opponent_mask = mask & opponent
            x = shift.operator(mv, shift.nbits) & opponent_mask

            for _ in range(self._size - 3):
                x |= shift.operator(x, shift.nbits) & opponent_mask

            if (shift.operator(x, shift.nbits) & current_mask) != 0:
                captured |= x

        current |= captured
        opponent &= ~captured
        return current, opponent, captured

    def captured(self, player: int, move: Position) -> PositionSet:
        """Get all pieces captured for the given move by the specified player."""
        _, _, captured = self._captured(player, move)
        return self._translate(captured)

    @property
    def is_full(self) -> bool:
        """Check if the board is full."""
        return (self.players[1] | self.players[-1]) == self._full_mask

    @property
    def num_empty(self) -> int:
        """Return the number of empty spaces on the board."""
        return bin((self.players[1] | self.players[-1]) ^ self._full_mask).count('1')

    def place_piece(self, piece: Position, player: int, capture: bool = True) -> None:
        """Place a piece on the board for the specified player."""
        if capture:
            current, opponent, _ = self._captured(player, piece)
            self.players[player] = current
            self.players[-player] = opponent
        else:
            row, col = piece
            mask = 1 << (row * self._size + col)
            self.players[player] |= mask

    def player_pieces(self, player: int) -> PositionSet:
        """Get all pieces on the board for the specified player."""
        return self._translate(self.players[player])

    def player_score(self, player: int) -> int:
        """Return the number of pieces held by the specified player."""
        return bin(self.players[player]).count('1')

    def reset(self) -> None:
        """Reset the board to its initial state."""
        self.players = {1: 0, -1: 0}
        size_2 = self._size // 2

        self.place_piece((size_2 - 1, size_2), 1, False)
        self.place_piece((size_2, size_2 - 1), 1, False)
        self.place_piece((size_2 - 1, size_2 - 1), -1, False)
        self.place_piece((size_2, size_2), -1, False)

    def score(self) -> int:
        """Return the current score of the game."""
        return self.player_score(1) - self.player_score(-1)

    @property
    def size(self) -> int:
        return self._size

    def _translate(self, moves: int) -> PositionSet:
        s = f'{moves:b}'.zfill(self._size**2)
        return {(i // self._size, i % self._size) for i, c in enumerate(s) if c == '1'}

    def valid_moves(self, player: int) -> PositionSet:
        """Return the set of valid moves for the specified player."""
        current = self.players[player]
        opponent = self.players[-player]
        empty = (current | opponent) ^ self._full_mask
        moves = 0

        for shift, mask in zip(self._shifts, self._masks):
            opponent_mask = mask & opponent
            empty_mask = mask & empty
            x = shift.operator(current, shift.nbits) & opponent_mask

            for _ in range(self._size - 3):
                x |= shift.operator(x, shift.nbits) & opponent_mask

            moves |= shift.operator(x, shift.nbits) & empty_mask

        return self._translate(moves)
