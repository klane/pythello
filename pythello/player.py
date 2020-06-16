class Player(object):
    def __init__(self, name='Player'):
        self.name = name

    def __repr__(self):
        return self.name


class AI(object):
    def __init__(self, strategy, name='AI'):
        self.name = name
        self.strategy = strategy

    def __repr__(self):
        return self.name

    def move(self, game):
        return self.strategy(game)
