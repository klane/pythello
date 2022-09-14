from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from pythello.player.greedy import greedy_move
from pythello.player.negamax import Negamax
from pythello.player.random import random_move

if TYPE_CHECKING:
    from pythello.game import Game
    from pythello.utils.typing import AIPlayer, Position


class PlayerWrapper:
    def __init__(self, player: AIPlayer) -> None:
        self._player = player

    def __call__(self, game: Game) -> Position:
        return self._player(game)


class AI(PlayerWrapper, Enum):
    RANDOM = PlayerWrapper(random_move)
    GREEDY = PlayerWrapper(greedy_move)
    NEGAMAX = PlayerWrapper(Negamax())
