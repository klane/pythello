from __future__ import annotations

import random
from typing import TYPE_CHECKING

from pythello.ai.strategy import AI

if TYPE_CHECKING:
    from pythello.game import Game
    from pythello.utils.typing import Position


class Random(AI):
    def move(self, game: Game) -> Position:
        return random.choice(list(game.valid))
