from __future__ import annotations

import sys
import time
from collections import defaultdict
from typing import TYPE_CHECKING

import pygame as pg

from pythello.app import App
from pythello.board import Board
from pythello.game import Game
from pythello.player import AI

if TYPE_CHECKING:
    from pythello.utils.typing import Player

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
        board = Board(game_size)
        game = Game(player1, player2, board, verbose)
        results: dict[Player | None, int] = defaultdict(int)
        start_time = time.time()

        for _ in range(games):
            while not game.is_over:
                game.move_with_pass()

            game.print_results()
            results[game.winner] += 1
            game.reset()

        print({k: v for k, v in sorted(results.items(), key=lambda item: -item[1])})
        print(time.time() - start_time)
