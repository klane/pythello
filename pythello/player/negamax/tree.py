from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, NamedTuple

if TYPE_CHECKING:
    from pythello.board import Position


class TreeFlag(Enum):
    LOWER = 1
    EXACT = 2
    UPPER = 3


class TreeNode(NamedTuple):
    move: Position
    score: float
    depth: int
    flag: TreeFlag
