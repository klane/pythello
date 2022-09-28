from __future__ import annotations

from collections.abc import MutableMapping
from typing import TYPE_CHECKING

from .cache import LRUCache
from .tree import TreeFlag, TreeNode

if TYPE_CHECKING:
    from pythello.board import Board, Color, Position
    from pythello.game import Game
    from pythello.score import Scorer

    TranspositionTable = MutableMapping[tuple[Board, Color], TreeNode]

DEFAULT_DEPTH = 4
INF = float('inf')


class Negamax:
    def __init__(
        self, scorer: Scorer, depth: int = DEFAULT_DEPTH, cache_size: int | None = None
    ) -> None:
        if depth <= 0:
            raise ValueError('Depth must be strictly positive')

        if cache_size is not None and cache_size <= 0:
            raise ValueError('Cache size must be strictly positive or None')

        self.scorer = scorer
        self.depth = depth
        self.cache: TranspositionTable

        if cache_size is not None:
            self.cache = LRUCache(cache_size)
        else:
            self.cache = {}

    def __call__(self, game: Game) -> Position:
        board, player = game.board, game.current_player.color
        negamax(board, player, self.scorer, self.cache, self.depth)
        return self.cache[(board, player)].move


def negamax(
    board: Board,
    player: Color,
    scorer: Scorer,
    cache: TranspositionTable,
    depth: int,
    alpha: float = -INF,
    beta: float = INF,
) -> float:
    alpha_orig = alpha
    node = cache.get((board, player))

    if node is not None and node.depth >= depth:
        if node.flag is TreeFlag.EXACT:
            return node.score
        elif node.flag is TreeFlag.LOWER:
            alpha = max(alpha, node.score)
        elif node.flag is TreeFlag.UPPER:
            beta = min(beta, node.score)

        if alpha >= beta:
            return node.score

    opponent = player.opponent
    player_moves = board.valid_moves(player)
    opponent_moves = board.valid_moves(opponent)

    if len(player_moves) == 0 and len(opponent_moves) > 0:
        return -negamax(board, opponent, scorer, cache, depth, -beta, -alpha)

    if depth == 0 or (len(player_moves) == 0 and len(opponent_moves) == 0):
        return scorer(board, player)

    best_move = -1
    best_score = -INF

    for move in player_moves:
        child = board.peek(move, player)
        score = -negamax(child, opponent, scorer, cache, depth - 1, -beta, -alpha)

        if score > best_score:
            best_move = move
            best_score = score
            alpha = max(alpha, score)

            if alpha >= beta:
                break

    if best_score <= alpha_orig:
        flag = TreeFlag.UPPER
    elif best_score >= beta:
        flag = TreeFlag.LOWER
    else:
        flag = TreeFlag.EXACT

    cache[(board, player)] = TreeNode(best_move, best_score, depth, flag)
    return best_score
