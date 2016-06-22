import numpy as np
import random
from collections import defaultdict
from copy import deepcopy


class Negamax(object):
    def __init__(self, depth, scoring):
        self.depth = depth
        self.scoring = scoring

    def __call__(self, game):
        return self.negamax(game, self.depth)[1]

    def negamax(self, game, depth, alpha=-np.inf, beta=np.inf):
        if depth == 0 or len(game.valid) == 0:
            return [self.scoring(game)]

        best_val = -np.inf
        best_move = 0

        for move in game.valid:
            child = deepcopy(game)
            child.move(move)
            val = -self.negamax(child, depth - 1, -beta, -alpha)[0]

            if val > best_val:
                best_val = val
                best_move = move

            alpha = max(alpha, val)

            if alpha >= beta:
                break

        return best_val, best_move


def greedy_move(game):
    num_turned = defaultdict(list)

    for k, v in game.valid.items():
        num_turned[len(v)].append(k)

    return random.choice(num_turned[max(num_turned.keys())])


def random_move(game):
    return random.choice(list(game.valid.keys()))
