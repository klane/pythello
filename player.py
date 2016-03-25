import random
from collections import defaultdict


class Player(object):
    def __init__(self, color, name='Player'):
        self.color = color
        self.name = name

    def __repr__(self):
        return self.name


class AI(Player):
    def move(self, valid):
        pass


class GreedyAI(AI):
    def __init__(self, color):
        super().__init__(color, 'Greedy AI')

    def move(self, valid):
        num_turned = defaultdict(list)

        for k, v in valid.items():
            num_turned[len(v)].append(k)

        return random.choice(num_turned[max(num_turned.keys())])


class RandomAI(AI):
    def __init__(self, color):
        super().__init__(color, 'Random AI')

    def move(self, valid):
        return random.choice(list(valid.keys()))
