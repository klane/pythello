import numpy as np
import random
from collections import defaultdict
from copy import deepcopy


class Negamax(object):
    def __init__(self, depth, scoring):
        self.depth = depth
        self.scoring = scoring

    def __call__(self, game):
        best_move = None
        best_score = -np.inf

        for move in game.valid:
            child = deepcopy(game)
            child.move(move)
            score = -self.negamax(child, self.depth-1)

            if score > best_score:
                best_move = move
                best_score = score

        return best_move

    def negamax(self, game, depth, alpha=-np.inf, beta=np.inf):
        if depth == 0 or len(game.valid) == 0:
            return self.scoring(game)

        best_score = -np.inf

        for move in game.valid:
            child = deepcopy(game)
            child.move(move)
            score = -self.negamax(child, depth-1, -beta, -alpha)
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
