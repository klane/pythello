from __future__ import annotations

import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pythello.board import Position
    from pythello.game import Game


def random_move(game: Game) -> Position:
    return random.choice(list(game.valid))
