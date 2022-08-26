def corner_mask(size: int) -> int:
    top_bottom = int('1' + '0' * (size - 2) + '1', 2)
    corner = 0
    corner |= top_bottom
    corner |= top_bottom << (size**2 - size)
    return corner


def edge_mask(size: int, remove_corners: bool = True) -> int:
    top_bottom = int('1' * size, 2)
    edge = 0
    edge |= top_bottom
    edge |= top_bottom << (size**2 - size)

    for i in range(size - 1):
        edge |= 3 << ((i + 1) * size - 1)

    if remove_corners:
        edge &= ~corner_mask(size)

    return edge


def full_mask(size: int) -> int:
    return int('1' * size**2, 2)


def interior_mask(size: int) -> int:
    return edge_mask(size, remove_corners=False) ^ full_mask(size)


def left_mask(size: int) -> int:
    return int(('1' * (size - 1) + '0') * size, 2)


def right_mask(size: int) -> int:
    return int(('0' + '1' * (size - 1)) * size, 2)
