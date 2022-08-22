from __future__ import annotations

from typing import TYPE_CHECKING

from pythello.board import corner_mask, edge_mask, full_mask

if TYPE_CHECKING:
    from pythello.game import GridGame


class EdgeScore:
    def __init__(self, size: int) -> None:
        _corner_mask = corner_mask(size)
        _edge_mask = edge_mask(size, remove_corners=True)
        _interior_mask = (_corner_mask | _edge_mask) ^ full_mask(size)
        self.weighted_masks = {
            _corner_mask: 9,
            _edge_mask: 3,
            _interior_mask: 1,
        }

    def __call__(self, game: GridGame) -> float:
        player = game.board.players[game.value]
        opponent = game.board.players[-game.value]
        score = 0

        for mask, weight in self.weighted_masks.items():
            player_count = bin(player & mask).count('1')
            opponent_count = bin(opponent & mask).count('1')
            score += (player_count - opponent_count) * weight

        return score


def greedy_score(game: GridGame) -> float:
    return game.board.score() * game.value
