from sys import stderr
from typing import TextIO

from chibicc.write import write


def split_at(s: str, i: int) -> tuple[str, str]:
    return s[:i], s[i:]


def parsenum(p: str) -> tuple[str, str]:
    endp = 0
    while endp < len(p) and p[endp].isdigit():
        endp += 1

    return split_at(p, endp)


def chibicc(args: list[str], writer: TextIO) -> int:
    if len(args) != 2:
        write(stderr, f"{args[0]}: invalid number of arguments")
        return 1

    p = args[1]
    if len(p) == 0:
        write(stderr, "you can't trick me")
        return 1

    write(writer, "    .globl main")
    write(writer, "main:")
    val, p = parsenum(p)
    write(writer, f"    movq ${val}, %rax")
    while len(p) > 0:
        match p[0]:
            case "+":
                p = p[1:]
                val, p = parsenum(p)
                write(writer, f"    add ${val}, %rax")
            case "-":
                p = p[1:]
                val, p = parsenum(p)
                write(writer, f"    sub ${val}, %rax")
            case c:
                write(stderr, f"ERROR: unexpected character '{c}'")
                return 1

    write(writer, "    ret")
    return 0
