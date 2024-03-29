from __future__ import annotations

Position = int
PositionSet = set[Position]


def position_to_coordinates(position: Position, size: int) -> tuple[int, int]:
    index = f'{position:b}'[::-1].find('1')
    return index // size, index % size


def split_position(position: Position) -> PositionSet:
    return {1 << i for i, c in enumerate(f'{position:b}'[::-1]) if c == '1'}
