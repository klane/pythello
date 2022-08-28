from __future__ import annotations

from abc import ABCMeta
from enum import Enum, EnumMeta
from typing import TYPE_CHECKING

from pythello.ai.strategy import AI
from pythello.player.greedy import Greedy
from pythello.player.negamax import Negamax
from pythello.player.random import Random

if TYPE_CHECKING:
    from pythello.game import Game
    from pythello.utils.typing import Position


class PlayerMeta(EnumMeta, ABCMeta):
    pass


class Player(AI, Enum, metaclass=PlayerMeta):
    RANDOM = Random()
    GREEDY = Greedy()
    NEGAMAX = Negamax()

    def __init__(self, ai: AI) -> None:
        self.ai = ai

    def move(self, game: Game) -> Position:
        return self.ai.move(game)
