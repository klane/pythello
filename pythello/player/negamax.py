from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, NamedTuple

if TYPE_CHECKING:
    from pythello.board import Board, Color, Position
    from pythello.game import Game
    from pythello.score import Scorer

INF = float('inf')
TRANSPOSITION_TABLE: dict[tuple[Board, Color], TreeNode] = {}


class TreeFlag(Enum):
    LOWER = 1
    EXACT = 2
    UPPER = 3


class TreeNode(NamedTuple):
    move: Position
    score: float
    depth: int
    flag: TreeFlag


class Negamax:
    def __init__(self, scorer: Scorer, depth: int = 4) -> None:
        if depth <= 0:
            raise ValueError('Depth must be strictly positive')

        self.scorer = scorer
        self.depth = depth

    def __call__(self, game: Game) -> Position:
        board, player = game.board, game.current_player
        negamax(board, player, self.scorer, self.depth)
        return TRANSPOSITION_TABLE[(board, player)].move


def negamax(
    board: Board,
    player: Color,
    scorer: Scorer,
    depth: int,
    alpha: float = -INF,
    beta: float = INF,
) -> float:
    alpha_orig = alpha
    entry = TRANSPOSITION_TABLE.get((board, player))

    if entry is not None and entry.depth >= depth:
        if entry.flag is TreeFlag.EXACT:
            return entry.score
        elif entry.flag is TreeFlag.LOWER:
            alpha = max(alpha, entry.score)
        elif entry.flag is TreeFlag.UPPER:
            beta = min(beta, entry.score)

        if alpha >= beta:
            return entry.score

    opponent = player.opponent
    player_moves = board.valid_moves(player)
    opponent_moves = board.valid_moves(opponent)

    if len(player_moves) == 0 and len(opponent_moves) > 0:
        return -negamax(board, opponent, scorer, depth, -beta, -alpha)

    if depth == 0 or (len(player_moves) == 0 and len(opponent_moves) == 0):
        return scorer(board, player)

    best_move = -1
    best_score = -INF

    for move in player_moves:
        child = board.peek(move, player)
        score = -negamax(child, opponent, scorer, depth - 1, -beta, -alpha)

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

    TRANSPOSITION_TABLE[(board, player)] = TreeNode(best_move, best_score, depth, flag)
    return best_score
