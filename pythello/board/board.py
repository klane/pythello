from abc import ABC, abstractmethod


class Board(ABC):
    def __init__(self, size):
        if size % 2 != 0 or size <= 0:
            raise ValueError('Enter a positive even integer board dimension')

        self._size = size

    @abstractmethod
    def get_pieces(self, player):
        """Get all pieces on the board for the specified player."""

    @property
    @abstractmethod
    def num_empty(self):
        """Return the number of empty spaces on the board."""

    @abstractmethod
    def place_piece(self, piece, player):
        """Place a piece on the board for the specified player."""

    @abstractmethod
    def player_score(self, player):
        """Return the number of pieces held by the specified player."""

    @abstractmethod
    def reset(self):
        """Reset the board to its initial state."""

    @abstractmethod
    def score(self):
        """Return the current score of the game."""

    @property
    def size(self):
        return self._size

    @abstractmethod
    def valid_moves(self, player):
        """Return a dictionary mapping valid moves to the pieces gained by the specified player."""
