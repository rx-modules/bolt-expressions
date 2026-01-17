__all__ = [
    "TypeCheckError",
    "TypeCheckDiagnostic",
    "get_exception_chain",
]


from typing import Any


class TypeCheckError(Exception):
    """Type incompatibility during type checking"""


class TypeCheckDiagnostic(Exception):
    """Diagnostic error raised by the type checker."""


def get_exception_chain(exc: BaseException) -> tuple[BaseException, ...]:
    exceptions: list[BaseException] = []

    current_exc = exc

    while current_exc:
        exceptions.append(current_exc)
        current_exc = current_exc.__cause__

    return tuple(exceptions)
