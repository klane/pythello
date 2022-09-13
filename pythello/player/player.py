from __future__ import annotations

from enum import Enum
from functools import partial
from typing import TYPE_CHECKING

from pythello.player.greedy import greedy_move
from pythello.player.negamax import Negamax
from pythello.player.random import random_move

if TYPE_CHECKING:
    from pythello.game import Game
    from pythello.utils.typing import Position


class AI(Enum):
    RANDOM = partial(random_move)
    GREEDY = partial(greedy_move)
    NEGAMAX = Negamax()

    def __call__(self, game: Game) -> Position:
        return self.value(game)
