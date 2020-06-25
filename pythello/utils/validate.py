from __future__ import annotations

import inspect
from functools import wraps
from typing import TYPE_CHECKING, Any, Callable, NamedTuple

if TYPE_CHECKING:
    from pythello.utils.typing import Function


class Condition(NamedTuple):
    check: Callable[..., bool]
    message: str


def check(*conditions: Condition) -> Callable[[Function], Function]:
    def decorate(f: Function) -> Function:
        @wraps(f)
        def g(*args: Any, **kwargs: Any) -> Any:
            fargs = inspect.getcallargs(f, *args, **kwargs)

            for c in conditions:
                sig = inspect.signature(c.check)
                cargs = [fargs[param] for param in sig.parameters]

                if not c.check(*cargs):
                    raise ValueError(c.message)

            return f(*args, **kwargs)

        return g

    return decorate
