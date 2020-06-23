import random
from abc import ABC, abstractmethod
from collections import defaultdict
from copy import deepcopy
from enum import Enum
from functools import partial
from multiprocessing import Pool

import numpy as np

from pythello.ai.score import greedy_score


class AI(ABC):
    @abstractmethod
    def move(self, game):
        """Get next move."""


class Negamax(AI):
    def __init__(self, depth=4, score=greedy_score, processes=4):
        self.depth = depth
        self.score = score
        self.processes = processes

    def move(self, game):
        if self.processes > 1:
            with Pool(self.processes) as pool:
                scores = pool.map(partial(self.negamax_root, game=game), game.valid)
        else:
            scores = [self.negamax_root(move, game) for move in game.valid]

        return list(game.valid)[np.argmax(scores)]

    def negamax_root(self, move, game):
        return -self.negamax(deepcopy(game).move(move), self.depth - 1)

    def negamax(self, game, depth, alpha=-np.inf, beta=np.inf):
        if depth == 0 or len(game.valid) == 0:
            return self.score(game)

        best_score = -np.inf

        for move in game.valid:
            score = -self.negamax(deepcopy(game).move(move), depth - 1, -beta, -alpha)
            best_score = max(best_score, score)
            alpha = max(alpha, score)

            if alpha >= beta:
                break

        return best_score


class Greedy(AI):
    def move(self, game):
        num_turned = defaultdict(list)

        for k, v in game.valid.items():
            num_turned[len(v)].append(k)

        return random.choice(num_turned[max(num_turned.keys())])


class Random(AI):
    def move(self, game):
        return random.choice(list(game.valid.keys()))


class PlayerMeta(type(AI), type(Enum)):
    pass


class Player(AI, Enum, metaclass=PlayerMeta):
    RANDOM = Random()
    GREEDY = Greedy()
    NEGAMAX = Negamax()

    def __new__(cls, *args):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, ai):
        self.ai = ai

    def move(self, game):
        return self.ai.move(game)
