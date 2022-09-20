from __future__ import annotations

from collections import OrderedDict
from collections.abc import Iterator, MutableMapping
from typing import Generic, TypeVar

KT = TypeVar('KT')
VT = TypeVar('VT')


class LRUCache(MutableMapping[KT, VT], Generic[KT, VT]):
    def __init__(self, capacity: int) -> None:
        self._cache = OrderedDict[KT, VT]()
        self._capacity = capacity

    def __delitem__(self, key: KT) -> None:
        self._cache.__delitem__(key)

    def __getitem__(self, key: KT) -> VT:
        self._cache.move_to_end(key, last=True)
        return self._cache[key]

    def __iter__(self) -> Iterator[KT]:
        return self._cache.__iter__()

    def __len__(self) -> int:
        return len(self._cache)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({list(self._cache.items())})'

    def __setitem__(self, key: KT, value: VT) -> None:
        self._cache[key] = value

        if len(self._cache) > self._capacity:
            self._cache.popitem(last=False)
