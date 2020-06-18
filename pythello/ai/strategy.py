import random
from collections import defaultdict
from copy import deepcopy
from functools import partial
from multiprocessing import Pool

import numpy as np

from pythello.ai.score import greedy_score


class Negamax:
    def __init__(self, depth=4, score=greedy_score, processes=4):
        self.depth = depth
        self.score = score
        self.processes = processes

    def __call__(self, game):
        with Pool(self.processes) as pool:
            scores = pool.map(partial(self.negamax_root, game=game), game.valid)
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


def greedy_move(game):
    num_turned = defaultdict(list)

    for k, v in game.valid.items():
        num_turned[len(v)].append(k)

    return random.choice(num_turned[max(num_turned.keys())])


def random_move(game):
    return random.choice(list(game.valid.keys()))
