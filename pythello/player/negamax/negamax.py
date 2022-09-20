from __future__ import annotations

from collections import OrderedDict
from collections.abc import Iterator, MutableMapping
from enum import Enum
from typing import TYPE_CHECKING, Generic, NamedTuple, TypeVar

if TYPE_CHECKING:
    from pythello.board import Board, Color, Position
    from pythello.game import Game
    from pythello.score import Scorer

INF = float('inf')
KT = TypeVar('KT')
VT = TypeVar('VT')


class LRUCache(MutableMapping[KT, VT], Generic[KT, VT]):
    def __init__(self, capacity: int) -> None:
        self._cache = OrderedDict[KT, VT]()
        self._capacity = capacity

    def __delitem__(self, key: KT) -> None:
        self._cache.__delitem__(key)

    def __iter__(self) -> Iterator[KT]:
        return self._cache.__iter__()

    def __getitem__(self, key: KT) -> VT:
        self._cache.move_to_end(key, last=True)
        return self._cache[key]

    def __len__(self) -> int:
        return len(self._cache)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({list(self._cache.items())})'

    def __setitem__(self, key: KT, value: VT) -> None:
        self._cache[key] = value

        if len(self._cache) > self._capacity:
            self._cache.popitem(last=False)


class TreeFlag(Enum):
    LOWER = 1
    EXACT = 2
    UPPER = 3


class TreeNode(NamedTuple):
    move: Position
    score: float
    depth: int
    flag: TreeFlag


if TYPE_CHECKING:
    TranspositionTable = MutableMapping[tuple[Board, Color], TreeNode]


class Negamax:
    def __init__(
        self, scorer: Scorer, depth: int = 4, cache_size: int | None = None
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
        board, player = game.board, game.current_player
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
    entry = cache.get((board, player))

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
