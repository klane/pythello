from game import GridGame, Othello
from player import Player, GreedyAI
from easyAI import AI_Player, Negamax
from gui import GUI

players = 0
size = 8
gui = True
verbose = False

if players == 2:
    player1 = Player()
    player2 = Player()
elif players == 1:
    player1 = Player()
    player2 = GreedyAI()
else:
    player1 = GreedyAI()
    player2 = AI_Player(Negamax(4, scoring=None, win_score=size**2/2))

game = Othello((player1, player2), size, verbose)

if gui:
    size = 500
    margin = 50
    GUI(game, size, margin).mainloop()
elif players == 0:
    games = 100
    results = {player1: 0, player2: 0, GridGame.DRAW: 0}

    for i in range(games):
        game.play(nmoves=100, verbose=verbose)
        results[game.winner] += 1
        game.reset()

    print(results)
else:
    raise ValueError("Interactive mode only supported with the GUI")
