import random
from collections import defaultdict


def greedy_move(game):
    num_turned = defaultdict(list)

    for k, v in game.valid.items():
        num_turned[len(v)].append(k)

    return random.choice(num_turned[max(num_turned.keys())])


def random_move(game):
    return random.choice(list(game.valid.keys()))
