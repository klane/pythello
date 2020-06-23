from pythello.ai.strategy import Player
from pythello.board.grid import GridBoard
from pythello.game import GridGame, Othello

players = 0
size = 8
gui = True
verbose = True

if players == 2:
    player1 = Player.HUMAN
    player2 = Player.HUMAN
elif players == 1:
    player1 = Player.HUMAN
    player2 = Player.GREEDY
else:
    player1 = Player.GREEDY
    player2 = Player.NEGAMAX

board = GridBoard(size)
game = Othello(player1, player2, board, verbose)

if gui:
    size = 600
elif players == 0:
    games = 100
    results = {player1: 0, player2: 0, GridGame.DRAW: 0}

    for _ in range(games):
        game.play()
        results[game.winner] += 1
        game.reset()

    print(results)
else:
    raise ValueError("Interactive mode only supported with the GUI")
