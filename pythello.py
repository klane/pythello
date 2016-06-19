from game import GridGame, Othello
from player import Player, AI
from ai import greedy_move, random_move
from gui import GUI

players = 0
size = 8
gui = True
verbose = True

if players == 2:
    player1 = Player()
    player2 = Player()
elif players == 1:
    player1 = Player()
    player2 = AI(greedy_move, 'Greedy AI')
else:
    player1 = AI(greedy_move, 'Greedy AI')
    player2 = AI(random_move, 'Random AI')

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
