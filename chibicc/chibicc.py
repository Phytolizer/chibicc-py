from enum import Enum, auto
from sys import stderr
from typing import NoReturn, Optional, TextIO, cast

from chibicc.write import write


class Token:
    class Kind(Enum):
        PUNCT = auto()
        NUM = auto()
        EOF = auto()

    kind: Kind
    _next: Optional["Token"]
    val: int
    loc: str

    def __init__(self, kind: Kind, start: str) -> None:
        self.kind = kind
        self.loc = start
        self._next = None
        self.val = 0

    @property
    def next(self) -> "Token":
        return cast(Token, self._next)

    @next.setter
    def next(self, next: "Token") -> None:
        self._next = next


class Failure(RuntimeError):
    pass


def error(*args, **kwargs) -> NoReturn:
    print(*args, **kwargs, file=stderr)
    raise Failure()


def equal(tok: Token, op: str) -> bool:
    return tok.loc == op


def skip(tok: Token, s: str) -> Token:
    if equal(tok, s):
        return cast(Token, tok.next)

    error(f"expected '{s}' but got '{tok.loc}'")


def get_num(tok: Token) -> int:
    if tok.kind != Token.Kind.NUM:
        error(f"expected number but got '{tok.loc}'")

    return tok.val


def split_at(s: str, i: int) -> tuple[str, str]:
    return s[:i], s[i:]


def parsenum(p: str) -> tuple[str, str]:
    for i, c in enumerate(p):
        if not c.isdigit():
            return split_at(p, i)

    return p, ""


def tokenize(p: str) -> Token:
    head = Token(Token.Kind.NUM, "")
    cur = head

    while len(p) > 0:
        match p[0]:
            case c if c.isspace():
                p = p[1:]
            case c if c.isdigit():
                text, p = parsenum(p)
                cur.next = Token(Token.Kind.NUM, text)
                cur.next.val = int(text)
                cur = cur.next
            case "+" | "-":
                cur.next = Token(Token.Kind.PUNCT, p[0])
                cur = cur.next
                p = p[1:]
            case c:
                error(f"unexpected character '{c}'")

    cur.next = Token(Token.Kind.EOF, "")
    return cast(Token, head.next)


def chibicc(args: list[str], writer: TextIO) -> int:
    if len(args) != 2:
        write(stderr, f"{args[0]}: invalid number of arguments")
        return 1

    p = args[1]
    if len(p) == 0:
        write(stderr, "you can't trick me")
        return 1

    try:
        tok = tokenize(p)
    except Failure:
        return 1

    write(writer, "    .global main")
    write(writer, "main:")
    write(writer, f"    mov ${get_num(tok)}, %rax")
    tok = tok.next
    while tok.kind != Token.Kind.EOF:
        if equal(tok, "+"):
            write(writer, f"    add ${get_num(tok.next)}, %rax")
            tok = tok.next.next
        else:
            tok = skip(tok, "-")
            write(writer, f"    sub ${get_num(tok)}, %rax")
            tok = tok.next

    write(writer, "    ret")
    return 0
