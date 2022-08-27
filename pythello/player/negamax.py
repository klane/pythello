from __future__ import annotations

import random
from copy import deepcopy
from functools import partial
from multiprocessing import Pool, cpu_count
from typing import TYPE_CHECKING

from pythello.ai.strategy import AI
from pythello.score import greedy_score
from pythello.utils.validate import Condition, check

if TYPE_CHECKING:
    from pythello.game import GridGame
    from pythello.utils.typing import IntPredicate, Position, Scorer

INF = float('inf')


class Negamax(AI):
    DEPTH_POSITIVE: IntPredicate = lambda depth: depth > 0
    PROCESSES_IN_RANGE: IntPredicate = lambda processes: 1 <= processes <= cpu_count()

    @check(
        Condition(DEPTH_POSITIVE, 'Depth must be strictly positive'),
        Condition(
            PROCESSES_IN_RANGE,
            f'Processes must be between 1 and available cores ({cpu_count()})',
        ),
    )
    def __init__(
        self, depth: int = 4, processes: int = 4, score: Scorer = greedy_score
    ) -> None:
        self.depth = depth
        self.score = score
        self.processes = processes

    def move(self, game: GridGame) -> Position:
        if self.processes > 1:
            with Pool(self.processes) as pool:
                scores = pool.map(partial(self.negamax_root, game=game), game.valid)
        else:
            scores = [self.negamax_root(move, game) for move in game.valid]

        index = random.choice([i for i, s in enumerate(scores) if s == max(scores)])
        return list(game.valid)[index]

    def negamax_root(self, move: Position, game: GridGame) -> float:
        return -self.negamax(deepcopy(game).move(move), self.depth - 1)

    def negamax(
        self, game: GridGame, depth: int, alpha: float = -INF, beta: float = INF
    ) -> float:
        if depth == 0 or game.is_over:
            return self.score(game)

        if not game.has_move:
            children = [deepcopy(game).next_turn()]
        else:
            children = [deepcopy(game).move(move) for move in game.valid]

        score = -INF

        for child in children:
            score = max(score, -self.negamax(child, depth - 1, -beta, -alpha))
            alpha = max(alpha, score)

            if alpha >= beta:
                break

        return score
