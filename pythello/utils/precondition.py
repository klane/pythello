from __future__ import annotations

import inspect
from typing import TYPE_CHECKING, Any, NamedTuple, TypeVar

if TYPE_CHECKING:
    from collections.abc import Callable

    from pythello.utils.typing import Function, Predicate

T = TypeVar('T')


class Condition(NamedTuple):
    check: Predicate
    message: str


class FunctionWrapper:
    def __init__(
        self, function: Function[T], condition: Predicate, message: str
    ) -> None:
        self._function = function
        self._condition = Condition(condition, message)

    def __call__(self, *args: tuple[Any], **kwargs: dict[str, Any]) -> T:
        function = self._function
        conditions = {self._condition}

        while isinstance(function, FunctionWrapper):
            conditions.add(function._condition)
            function = function._function

        signature = inspect.signature(function)
        bound_args = signature.bind(*args, **kwargs)
        bound_args.apply_defaults()
        function_args = bound_args.arguments

        for condition in conditions:
            signature = inspect.signature(condition.check)
            condition_args = [function_args[param] for param in signature.parameters]

            if not condition.check(*condition_args):
                raise ValueError(condition.message)

        return function(*args, **kwargs)


def precondition(
    condition: Predicate, message: str
) -> Callable[[Function[T]], Function[T]]:
    def decorator(function: Function[T]) -> Function[T]:
        return FunctionWrapper(function, condition, message)

    return decorator
