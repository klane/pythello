import sys

import pygame as pg

from pythello.ai.strategy import Player
from pythello.app import App
from pythello.board.grid import GridBoard
from pythello.game import GridGame, Othello

app = True
app_size = 600

player1 = Player.GREEDY
player2 = Player.RANDOM
game_size = 8
verbose = True
games = 100

if __name__ == '__main__':
    if app:
        pg.init()
        App(app_size).start()
        pg.quit()
        sys.exit()
    else:
        board = GridBoard(game_size)
        game = Othello(player1, player2, board, verbose)
        results = {player1: 0, player2: 0, GridGame.DRAW: 0}

        for _ in range(games):
            game.play()
            results[game.winner] += 1
            game.reset()

        print(results)
