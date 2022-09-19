from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pythello.board import Board, Color, Position
    from pythello.game import Game
    from pythello.score import Scorer

INF = float('inf')


class Negamax:
    def __init__(self, scorer: Scorer, depth: int = 4) -> None:
        if depth <= 0:
            raise ValueError('Depth must be strictly positive')

        self.scorer = scorer
        self.depth = depth

    def __call__(self, game: Game) -> Position:
        best_move, _ = negamax(
            board=game.board,
            player=game.current_player,
            scorer=self.scorer,
            depth=self.depth,
        )

        return best_move


def negamax(
    board: Board,
    player: Color,
    scorer: Scorer,
    depth: int,
    alpha: float = -INF,
    beta: float = INF,
) -> tuple[Position, float]:
    opponent = player.opponent
    player_moves = board.valid_moves(player)
    opponent_moves = board.valid_moves(opponent)

    if len(player_moves) == 0 and len(opponent_moves) > 0:
        _, score = negamax(board, opponent, scorer, depth, -beta, -alpha)
        return None, -score

    if depth == 0 or (len(player_moves) == 0 and len(opponent_moves) == 0):
        return None, scorer(board, player)

    best_move = None
    best_score = -INF

    for move in player_moves:
        child = board.peek(move, player)
        _, score = negamax(child, opponent, scorer, depth - 1, -beta, -alpha)
        score *= -1

        if score > best_score:
            best_move = move
            best_score = score
            alpha = max(alpha, score)

            if alpha >= beta:
                break

    return best_move, best_score
