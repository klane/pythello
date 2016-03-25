from game import GridGame, Othello
from player import GreedyAI, RandomAI

size = 8
games = 100
verbose = False

player1 = GreedyAI('black')
player2 = RandomAI('white')

results = {player1: 0, player2: 0, GridGame.DRAW: 0}
game = Othello(size, player1, player2, verbose)

for i in range(games):
    game.play()
    results[game.winner] += 1
    game.reset()

print(results)
