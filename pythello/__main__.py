from __future__ import annotations

import sys
import time

import pygame as pg

from pythello.app import App
from pythello.board import Board
from pythello.game import Game
from pythello.player import AI

app = True
app_size = 600

player1 = AI.GREEDY
player2 = AI.RANDOM
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
        start_time = time.time()
        board = Board(game_size)
        results = Game.series(board, player1, player2, games, verbose)

        print({k: v for k, v in sorted(results.items(), key=lambda item: -item[1])})
        print(time.time() - start_time)
