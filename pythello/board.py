from __future__ import annotations

from operator import lshift, rshift
from typing import TYPE_CHECKING, Callable, Dict, NamedTuple, Tuple, Union

from pythello.utils.validate import Condition, check

if TYPE_CHECKING:
    from pythello.utils.typing import IntPredicate, Position, PositionSet


class Shift(NamedTuple):
    operator: Callable[[int, int], int]
    nbits: int


class Board:
    SIZE_POSITIVE_EVEN: IntPredicate = lambda size: size > 0 and size % 2 == 0

    @check(Condition(SIZE_POSITIVE_EVEN, 'Board size must be a positive even integer'))
    def __init__(self, size: int = 8):
        self._size = size
        self.players: Dict[int, int] = {}

        mask_right = int(('0' + '1' * (size - 1)) * size, 2)
        mask_left = int(('1' * (size - 1) + '0') * size, 2)
        self.mask_full = int('1' * size ** 2, 2)

        self.masks = (
            mask_right,                             # right
            mask_right >> size,                     # down + right
            self.mask_full,                         # down
            mask_left >> size,                      # down + left
            mask_left,                              # left
            (mask_left << size) & self.mask_full,   # up + left
            self.mask_full,                         # up
            (mask_right << size) & self.mask_full,  # up + right
        )

        self.shifts = (
            Shift(rshift, 1),         # right
            Shift(rshift, size + 1),  # down + right
            Shift(rshift, size),      # down
            Shift(rshift, size - 1),  # down + left
            Shift(lshift, 1),         # left
            Shift(lshift, size + 1),  # up + left
            Shift(lshift, size),      # up
            Shift(lshift, size - 1),  # up + right
        )

        self.reset()

    def __hash__(self) -> int:
        return (self.players[1], self.players[-1]).__hash__()

    def __mul__(self, other: Union[Board, int]) -> Board:
        raise NotImplementedError('Multiply not yet implemented')

    def _captured(self, player: int, move: Position) -> Tuple[int, int, int]:
        current = self.players[player]
        opponent = self.players[-player]
        index = move[0] * self._size + move[1]
        mv = 1 << (self._size ** 2 - index - 1)
        captured = mv

        for shift, mask in zip(self.shifts, self.masks):
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
        _, _, captured = self._captured(player, move)
        return self._translate(captured)

    @property
    def is_full(self) -> bool:
        return (self.players[1] | self.players[-1]) == self.mask_full

    @property
    def num_empty(self) -> int:
        return bin((self.players[1] | self.players[-1]) ^ self.mask_full).count('1')

    def place_piece(self, piece: Position, player: int, capture: bool = True) -> None:
        if capture:
            current, opponent, _ = self._captured(player, piece)
            self.players[player] = current
            self.players[-player] = opponent
        else:
            row, col = piece
            mask = 1 << (row * self._size + col)
            self.players[player] |= mask

    def player_pieces(self, player: int) -> PositionSet:
        return self._translate(self.players[player])

    def player_score(self, player: int) -> int:
        return bin(self.players[player]).count('1')

    def reset(self) -> None:
        self.players = {1: 0, -1: 0}
        size_2 = self._size // 2

        self.place_piece((size_2 - 1, size_2), 1, False)
        self.place_piece((size_2, size_2 - 1), 1, False)
        self.place_piece((size_2 - 1, size_2 - 1), -1, False)
        self.place_piece((size_2, size_2), -1, False)

    def _translate(self, moves: int) -> PositionSet:
        s = f'{moves:b}'.zfill(self._size ** 2)
        return {(i // self._size, i % self._size) for i, c in enumerate(s) if c == '1'}

    def valid_moves(self, player: int) -> PositionSet:
        current = self.players[player]
        opponent = self.players[-player]
        empty = (current | opponent) ^ self.mask_full
        moves = 0

        for shift, mask in zip(self.shifts, self.masks):
            opponent_mask = mask & opponent
            empty_mask = mask & empty
            x = shift.operator(current, shift.nbits) & opponent_mask

            for _ in range(self._size - 3):
                x |= shift.operator(x, shift.nbits) & opponent_mask

            moves |= shift.operator(x, shift.nbits) & empty_mask

        return self._translate(moves)
