from __future__ import annotations

from enum import IntEnum


class Color(IntEnum):
    BLACK = 0
    WHITE = 1

    @property
    def opponent(self) -> Color:
        return Color(self ^ 1)
