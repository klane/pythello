import random
from collections import defaultdict


class Player(object):
    def __init__(self, name='Player'):
        self.name = name

    def __repr__(self):
        return self.name


class AI(Player):
    def move(self, valid):
        pass


class GreedyAI(AI):
    def __init__(self):
        super().__init__('Greedy AI')

    def move(self, valid):
        num_turned = defaultdict(list)

        for k, v in valid.items():
            num_turned[len(v)].append(k)

        return random.choice(num_turned[max(num_turned.keys())])


class RandomAI(AI):
    def __init__(self):
        super().__init__('Random AI')

    def move(self, valid):
        return random.choice(list(valid.keys()))
