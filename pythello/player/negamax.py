from __future__ import annotations

import random
from copy import deepcopy
from functools import partial
from multiprocessing import Pool, cpu_count
from typing import TYPE_CHECKING

from pythello.score import greedy_score

if TYPE_CHECKING:
    from pythello.game import Game
    from pythello.typing import Position, Scorer

CPU_COUNT = cpu_count()
INF = float('inf')


class Negamax:
    def __init__(
        self, depth: int = 4, processes: int = CPU_COUNT, score: Scorer = greedy_score
    ) -> None:
        if depth <= 0:
            raise ValueError('Depth must be strictly positive')

        if not 1 <= processes <= CPU_COUNT:
            raise ValueError(f'Processes must be between 1 and {CPU_COUNT}')

        self.depth = depth
        self.score = score
        self.processes = processes

    def __call__(self, game: Game) -> Position:
        if self.processes > 1:
            with Pool(self.processes) as pool:
                scores = pool.map(partial(self.negamax_root, game=game), game.valid)
        else:
            scores = [self.negamax_root(move, game) for move in game.valid]

        index = random.choice([i for i, s in enumerate(scores) if s == max(scores)])
        return list(game.valid)[index]

    def negamax_root(self, move: Position, game: Game) -> float:
        return -self.negamax(deepcopy(game).move(move), self.depth - 1)

    def negamax(
        self, game: Game, depth: int, alpha: float = -INF, beta: float = INF
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
