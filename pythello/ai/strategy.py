from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pythello.game import Game
    from pythello.utils.typing import Position


class AI(ABC):
    @abstractmethod
    def move(self, game: Game) -> Position:
        """Get next move."""
