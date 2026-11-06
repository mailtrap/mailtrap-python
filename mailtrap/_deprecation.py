import functools
import warnings
from contextvars import ContextVar
from typing import Callable
from typing import Optional
from typing import ParamSpec
from typing import TypeVar

from mailtrap.exceptions import ClientConfigurationError

P = ParamSpec("P")
R = TypeVar("R")
T = TypeVar("T")

_silenced: ContextVar[bool] = ContextVar("_silenced", default=False)


def warn_deprecated(old: str, new: str, stacklevel: int = 3) -> None:
    """
    Emit a DeprecationWarning for a renamed name.

    The default `stacklevel` points at the caller of the function that calls this one,
    so the warning shows the user's line. Python reports a warning once per call site.
    """
    if _silenced.get():
        return
    warnings.warn(
        f"{old} is deprecated and will be removed in a future major release; "
        f"use {new} instead.",
        DeprecationWarning,
        stacklevel=stacklevel,
    )


def build_without_warning(cls: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> T:
    """
    Build a deprecated class without the DeprecationWarning its constructor raises.
    Every warn_deprecated call is silenced while `cls(...)` runs.

    For deprecated properties that have already warned, so a user's call warns once.
    """
    token = _silenced.set(True)
    try:
        return cls(*args, **kwargs)
    finally:
        _silenced.reset(token)


def renamed_kwargs(**old_to_new: str) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Accept the old keyword names of renamed parameters.

    An old keyword is passed on under its new name with a DeprecationWarning; passing
    both raises TypeError. Static type checkers see only the new signature.
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            for old, new in old_to_new.items():
                if old not in kwargs:
                    continue
                if new in kwargs:
                    raise TypeError(
                        f"{func.__qualname__}() got both '{old}' and '{new}'; "
                        f"pass only '{new}'"
                    )
                warn_deprecated(
                    f"{func.__qualname__}({old}=...)", f"{func.__qualname__}({new}=...)"
                )
                kwargs[new] = kwargs.pop(old)
            return func(*args, **kwargs)

        return wrapper

    return decorator


def resolve_renamed_arg(
    owner: str, old: str, old_value: Optional[T], new: str, new_value: Optional[T]
) -> Optional[T]:
    """
    Return the value of a renamed constructor argument whose old name stays in the
    signature, so code passing the old keyword still type-checks.

    Passing the old one warns; passing both with different values raises
    ClientConfigurationError.
    """
    if old_value is None:
        return new_value
    warn_deprecated(f"{owner}({old}=...)", f"{owner}({new}=...)", stacklevel=4)
    if new_value is None:
        return old_value
    if str(new_value) != str(old_value):
        raise ClientConfigurationError(
            f"`{old}` and `{new}` have different values; pass only `{new}`"
        )
    return new_value
