from __future__ import annotations

import random
from abc import ABC, ABCMeta, abstractmethod
from collections import defaultdict
from copy import deepcopy
from enum import Enum, EnumMeta
from functools import partial
from multiprocessing import Pool, cpu_count
from typing import TYPE_CHECKING, Any

from pythello.ai.score import greedy_score
from pythello.utils.validate import Condition, check

if TYPE_CHECKING:
    from pythello.game import GridGame
    from pythello.utils.typing import IntPredicate, Move, Scorer

INF = float('inf')


class AI(ABC):
    @abstractmethod
    def move(self, game: GridGame) -> Move:
        """Get next move."""


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
    ):
        self.depth = depth
        self.score = score
        self.processes = processes

    def move(self, game: GridGame) -> Move:
        if self.processes > 1:
            with Pool(self.processes) as pool:
                scores = pool.map(partial(self.negamax_root, game=game), game.valid)
        else:
            scores = [self.negamax_root(move, game) for move in game.valid]

        index = random.choice([i for i, s in enumerate(scores) if s == max(scores)])
        return list(game.valid)[index]

    def negamax_root(self, move: Move, game: GridGame) -> float:
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


class Greedy(AI):
    def move(self, game: GridGame) -> Move:
        num_turned = defaultdict(list)

        for k, v in game.valid.items():
            num_turned[len(v)].append(k)

        return random.choice(num_turned[max(num_turned.keys())])


class Random(AI):
    def move(self, game: GridGame) -> Move:
        return random.choice(list(game.valid.keys()))


class PlayerMeta(EnumMeta, ABCMeta):
    pass


class Player(AI, Enum, metaclass=PlayerMeta):
    RANDOM = Random()
    GREEDY = Greedy()
    NEGAMAX = Negamax()

    def __new__(cls, *args: Any) -> Any:
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, ai: AI):
        self.ai = ai

    def move(self, game: GridGame) -> Move:
        return self.ai.move(game)
