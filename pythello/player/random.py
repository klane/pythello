from __future__ import annotations

import random
from typing import TYPE_CHECKING

from pythello.ai.strategy import AI

if TYPE_CHECKING:
    from pythello.game import GridGame
    from pythello.utils.typing import Position


class Random(AI):
    def move(self, game: GridGame) -> Position:
        return random.choice(list(game.valid))
