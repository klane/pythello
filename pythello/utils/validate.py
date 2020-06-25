from __future__ import annotations

import inspect
from collections import namedtuple
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pythello.utils.typing import Function

Condition = namedtuple('Condition', ['check', 'message'])


def check(*conditions: Condition) -> Function:
    def decorate(f: Function) -> Function:
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
