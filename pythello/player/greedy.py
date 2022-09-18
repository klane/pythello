from __future__ import annotations

import random
from collections import defaultdict
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pythello.board import Position
    from pythello.game import Game


def greedy_move(game: Game) -> Position:
    num_turned = defaultdict(list)

    for move in game.valid:
        num_turned[len(game.captured(move))].append(move)

    return random.choice(num_turned[max(num_turned.keys())])
