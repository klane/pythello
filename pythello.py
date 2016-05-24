from game import GridGame, Othello
from player import Player, GreedyAI, RandomAI
from gui import GUI

players = 0
size = 8
gui = True
verbose = True

if players == 2:
    player1 = Player('black')
    player2 = Player('white')
elif players == 1:
    player1 = Player('black')
    player2 = GreedyAI('white')
else:
    player1 = GreedyAI('black')
    player2 = RandomAI('white')

game = Othello(player1, player2, size, verbose)

if gui:
    size = 500
    margin = 50
    GUI(game, size, margin).mainloop()
elif players == 0:
    games = 100
    results = {player1: 0, player2: 0, GridGame.DRAW: 0}

    for i in range(games):
        game.play()
        results[game.winner] += 1
        game.reset()

    print(results)
else:
    raise ValueError("Interactive mode only supported with the GUI")
