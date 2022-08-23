from sys import stderr
from typing import TextIO

from chibicc.write import write


def parsenum(p: str) -> tuple[int, str]:
    endp = 1
    while p[:endp].isdigit() and endp < len(p):
        endp += 1

    if endp < len(p):
        endp -= 1

    return int(p[:endp]), p[endp:]


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
