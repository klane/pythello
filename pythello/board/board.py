from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Set, Union

if TYPE_CHECKING:
    from pythello.utils.typing import Move, ValidMoves


class Board(ABC):
    def __init__(self, size: int):
        if size % 2 != 0 or size <= 0:
            raise ValueError('Enter a positive even integer board dimension')

        self._size = size

    @abstractmethod
    def __mul__(self, other: Union[Board, int]) -> Board:
        """Multiply board by another board or a constant"""

    @abstractmethod
    def get_pieces(self, player: int) -> Set[Move]:
        """Get all pieces on the board for the specified player."""

    @property
    @abstractmethod
    def num_empty(self) -> int:
        """Return the number of empty spaces on the board."""

    @abstractmethod
    def place_piece(self, piece: Move, player: int) -> None:
        """Place a piece on the board for the specified player."""

    @abstractmethod
    def player_score(self, player: int) -> int:
        """Return the number of pieces held by the specified player."""

    @abstractmethod
    def reset(self) -> None:
        """Reset the board to its initial state."""

    @abstractmethod
    def score(self) -> int:
        """Return the current score of the game."""

    @property
    def size(self) -> int:
        return self._size

    @abstractmethod
    def valid_moves(self, player: int) -> ValidMoves:
        """Return a dictionary mapping moves to pieces gained by the given player."""
