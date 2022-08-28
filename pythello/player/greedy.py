from __future__ import annotations

import random
from collections import defaultdict
from typing import TYPE_CHECKING

from pythello.ai.strategy import AI

if TYPE_CHECKING:
    from pythello.game import Game
    from pythello.utils.typing import Position


class Greedy(AI):
    def move(self, game: Game) -> Position:
        num_turned = defaultdict(list)

        for move in game.valid:
            num_turned[len(game.captured(move))].append(move)

        return random.choice(num_turned[max(num_turned.keys())])
