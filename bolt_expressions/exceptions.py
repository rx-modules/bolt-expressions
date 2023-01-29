__all__ = [
    "TypeCheckError",
    "get_exception_chain",
]


class TypeCheckError(Exception):
    """Type incompatibility during type checking"""


def get_exception_chain(exc: BaseException) -> tuple[BaseException]:
    exceptions: list[BaseException] = []

    current_exc = exc

    while current_exc:
        exceptions.append(current_exc)
        current_exc = current_exc.__cause__

    return tuple(exceptions)
