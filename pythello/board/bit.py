from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, Tuple, Union

from pythello.board.board import Board

if TYPE_CHECKING:
    from pythello.utils.typing import Function, Position, PositionSet

MASK_WEST = 0x7F7F7F7F7F7F7F7F
MASK_EAST = 0xFEFEFEFEFEFEFEFE
MASK_FULL = 0xFFFFFFFFFFFFFFFF


class FunctionWrapper:
    """Mask a function as an Object"""

    def __init__(self, function: Function):
        self.function = function

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.function(*args, **kwargs)


class Shift(FunctionWrapper, Enum):
    NORTH = FunctionWrapper(lambda board: board << 8)
    SOUTH = FunctionWrapper(lambda board: board >> 8)
    WEST = FunctionWrapper(lambda board: (board & MASK_WEST) << 1)
    EAST = FunctionWrapper(lambda board: (board & MASK_EAST) >> 1)
    NORTHWEST = FunctionWrapper(lambda board: Shift.NORTH(Shift.WEST(board)))
    NORTHEAST = FunctionWrapper(lambda board: Shift.NORTH(Shift.EAST(board)))
    SOUTHWEST = FunctionWrapper(lambda board: Shift.SOUTH(Shift.WEST(board)))
    SOUTHEAST = FunctionWrapper(lambda board: Shift.SOUTH(Shift.EAST(board)))


class BitBoard(Board):
    def __init__(self, size: int = 8):
        super().__init__(size)
        self.players: Dict[int, int] = {}
        self.reset()

    def __hash__(self) -> int:
        return (self.players[1], self.players[-1]).__hash__()

    def __mul__(self, other: Union[Board, int]) -> Board:
        raise NotImplementedError('Multiply not yet implemented')

    def __captured(self, player: int, move: Position) -> Tuple[int, int, int]:
        current = self.players[player]
        opponent = self.players[-player]
        index = move[0] * self._size + move[1]
        mv = 2 ** (self._size ** 2 - index - 1)
        current |= mv
        captured_total = mv

        for shift in Shift:
            captured = shift(mv) & opponent

            for _ in range(self._size - 3):
                captured |= shift(captured) & opponent

            if (shift(captured) & current) != 0:
                current |= captured
                opponent &= ~captured
                captured_total |= captured

        return current, opponent, captured_total

    def captured(self, player: int, move: Position) -> PositionSet:
        _, _, captured = self.__captured(player, move)
        return self.__translate(captured)

    @property
    def is_full(self) -> bool:
        return (self.players[1] | self.players[-1]) == MASK_FULL

    @property
    def num_empty(self) -> int:
        return bin((self.players[1] | self.players[-1]) ^ MASK_FULL).count('1')

    def place_piece(self, piece: Position, player: int) -> None:
        current, opponent, _ = self.__captured(player, piece)
        self.players[player] = current
        self.players[-player] = opponent

    def player_pieces(self, player: int) -> PositionSet:
        return self.__translate(self.players[player])

    def player_score(self, player: int) -> int:
        return bin(self.players[player]).count('1')

    def reset(self) -> None:
        self.players[1] = 0x810000000
        self.players[-1] = 0x1008000000

    def __translate(self, moves: int) -> PositionSet:
        move_str = f'{moves:064b}'
        return {self.__translate_index(i) for i, c in enumerate(move_str) if c == '1'}

    def __translate_index(self, index: int) -> Tuple[int, int]:
        row = index // self._size
        return row, index - self._size * row

    def valid_moves(self, player: int) -> PositionSet:
        current = self.players[player]
        opponent = self.players[-player]
        empty = (current | opponent) ^ MASK_FULL
        moves = 0

        for shift in Shift:
            captured = shift(current) & opponent

            for _ in range(self._size - 3):
                captured |= shift(captured) & opponent

            moves |= shift(captured) & empty

        return self.__translate(moves)
