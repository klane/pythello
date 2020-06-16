from pythello.game import GridGame, Othello
from pythello.board.grid import GridBoard
from pythello.player import Player, AI
from pythello.ai.strategy import Negamax, greedy_move
from pythello.ai.score import EdgeScore
from pythello.app import GUI

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
    player2 = AI(Negamax(4, score=EdgeScore(size)), 'Negamax AI')

board = GridBoard(size)
game = Othello(player1, player2, board, verbose)

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
