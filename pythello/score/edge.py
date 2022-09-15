from __future__ import annotations

from typing import TYPE_CHECKING

from pythello.board.mask import corner_mask, edge_mask, interior_mask

if TYPE_CHECKING:
    from pythello.board import Board, Color


class EdgeScore:
    def __init__(self, size: int) -> None:
        _corner_mask = corner_mask(size)
        _edge_mask = edge_mask(size, remove_corners=True)
        _interior_mask = interior_mask(size)
        self.weighted_masks = {
            _corner_mask: 9,
            _edge_mask: 3,
            _interior_mask: 1,
        }

    def __call__(self, board: Board, player: Color) -> float:
        current = board.players[player]
        opponent = board.players[player.opponent]
        score = 0

        for mask, weight in self.weighted_masks.items():
            player_count = bin(current & mask).count('1')
            opponent_count = bin(opponent & mask).count('1')
            score += (player_count - opponent_count) * weight

        return score
