from __future__ import annotations

import random
from functools import partial
from multiprocessing import Pool, cpu_count
from typing import TYPE_CHECKING

from pythello.score import Score

if TYPE_CHECKING:
    from pythello.board import Board, Color, Position
    from pythello.game import Game

CPU_COUNT = cpu_count()
INF = float('inf')
SCORER = Score.BALANCED


class Negamax:
    def __init__(self, depth: int = 4, processes: int = CPU_COUNT) -> None:
        if depth <= 0:
            raise ValueError('Depth must be strictly positive')

        if not 1 <= processes <= CPU_COUNT:
            raise ValueError(f'Processes must be between 1 and {CPU_COUNT}')

        self.depth = depth
        self.processes = processes

    def __call__(self, game: Game) -> Position:
        player = game.current_player
        opponent = player.opponent
        valid_moves = list(game.valid)
        boards = [game.board.peek(move, player) for move in valid_moves]
        func = partial(negamax, player=player, opponent=opponent, depth=self.depth - 1)

        if self.processes > 1:
            with Pool(self.processes) as pool:
                scores = pool.map(func, boards)
        else:
            scores = [func(board) for board in boards]

        index = random.choice([i for i, s in enumerate(scores) if s == max(scores)])
        return valid_moves[index]


def negamax(
    board: Board,
    player: Color,
    opponent: Color,
    depth: int,
    alpha: float = -INF,
    beta: float = INF,
) -> float:
    player_moves = board.valid_moves(player)
    opponent_moves = board.valid_moves(opponent)

    if len(player_moves) == 0 and len(opponent_moves) > 0:
        return -negamax(board, opponent, player, depth, -beta, -alpha)

    if depth == 0 or (len(player_moves) == 0 and len(opponent_moves) == 0):
        return SCORER(board, player)

    best = -INF

    for move in player_moves:
        board = board.peek(move, player)
        score = -negamax(board, opponent, player, depth - 1, -beta, -alpha)
        best = max(best, score)
        alpha = max(alpha, score)

        if alpha >= beta:
            break

    return best
