from typing import TextIO


def write(writer: TextIO, *args, **kwargs) -> None:
    print(*args, **kwargs, file=writer)
