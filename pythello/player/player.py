from __future__ import annotations

import random
from collections.abc import Callable
from enum import Enum

from pythello.board import Position
from pythello.game import Game
from pythello.player.greedy import greedy_move
from pythello.player.heuristic import Heuristic
from pythello.player.negamax import Negamax
from pythello.score import Score

AIPlayer = Callable[[Game], Position]
Player = str | AIPlayer


class PlayerWrapper:
    def __init__(self, player: AIPlayer) -> None:
        self._player = player

    def __call__(self, game: Game) -> Position:
        return self._player(game)


class AI(PlayerWrapper, Enum):
    RANDOM = PlayerWrapper(lambda game: random.choice(list(game.valid)))
    GREEDY = PlayerWrapper(greedy_move)
    EDGE = Heuristic(Score.EDGE)
    BALANCED = Heuristic(Score.BALANCED)
    NEGAMAX = Negamax()
