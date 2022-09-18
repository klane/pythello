from __future__ import annotations

from collections.abc import Callable
from enum import Enum
from typing import Union

from pythello.board import Position
from pythello.game import Game
from pythello.player.greedy import greedy_move
from pythello.player.negamax import Negamax
from pythello.player.random import random_move

AIPlayer = Callable[[Game], Position]
Player = Union[AIPlayer, str]


class PlayerWrapper:
    def __init__(self, player: AIPlayer) -> None:
        self._player = player

    def __call__(self, game: Game) -> Position:
        return self._player(game)


class AI(PlayerWrapper, Enum):
    RANDOM = PlayerWrapper(random_move)
    GREEDY = PlayerWrapper(greedy_move)
    NEGAMAX = PlayerWrapper(Negamax())
