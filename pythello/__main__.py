from __future__ import annotations

import sys
from collections import defaultdict
from typing import TYPE_CHECKING, Dict, Optional

import pygame as pg

from pythello.ai.strategy import Player
from pythello.app import App
from pythello.board import Board
from pythello.game import Othello

if TYPE_CHECKING:
    from pythello.utils.typing import Player as PlayerType

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
        board = Board(game_size)
        game = Othello(player1, player2, board, verbose)
        results: Dict[Optional[PlayerType], int] = defaultdict(int)

        for _ in range(games):
            while not game.is_over:
                game.move_with_pass()

            game.print_results()
            results[game.winner] += 1
            game.reset()

        print({k: v for k, v in sorted(results.items(), key=lambda item: -item[1])})
