from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Set, Union

from pythello.utils.validate import Condition, check

if TYPE_CHECKING:
    from pythello.utils.typing import IntPredicate, Move, ValidMoves


class Board(ABC):
    SIZE_POSITIVE_EVEN: IntPredicate = lambda size: size > 0 and size % 2 == 0

    @check(Condition(SIZE_POSITIVE_EVEN, 'Board size must be a positive even integer'))
    def __init__(self, size: int):
        self._size = size

    @abstractmethod
    def __mul__(self, other: Union[Board, int]) -> Board:
        """Multiply board by another board or a constant"""

    @abstractmethod
    def captured(self, player: int, move: Move) -> Set[Move]:
        """Get all pieces captured for the given move by the specified player."""

    @abstractmethod
    def get_pieces(self, player: int) -> Set[Move]:
        """Get all pieces on the board for the specified player."""

    @property
    def is_full(self) -> bool:
        return self.num_empty == 0

    @property
    @abstractmethod
    def num_empty(self) -> int:
        """Return the number of empty spaces on the board."""

    @abstractmethod
    def place_piece(self, piece: Move, player: int) -> None:
        """Place a piece on the board for the specified player."""

    def player_score(self, player: int) -> int:
        """Return the number of pieces held by the specified player."""
        return len(self.get_pieces(player))

    @abstractmethod
    def reset(self) -> None:
        """Reset the board to its initial state."""

    def score(self) -> int:
        """Return the current score of the game."""
        return self.player_score(1) - self.player_score(-1)

    @property
    def size(self) -> int:
        return self._size

    @abstractmethod
    def valid_moves(self, player: int) -> ValidMoves:
        """Return a dictionary mapping moves to pieces gained by the given player."""
