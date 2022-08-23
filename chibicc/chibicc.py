from enum import Enum, auto
from sys import stderr
from typing import NoReturn, Optional, TextIO, cast

from chibicc.write import write


def split_at(s: str, i: int) -> tuple[str, str]:
    return s[:i], s[i:]


def parse_num(p: str) -> tuple[str, str]:
    for i, c in enumerate(p):
        if not c.isdigit():
            return split_at(p, i)

    return p, ""


class Token:
    class Kind(Enum):
        PUNCT = auto()
        NUM = auto()
        EOF = auto()

    kind: Kind
    _next: Optional["Token"]
    val: int
    begin: int
    end: int

    def __init__(self, kind: Kind, begin: int, end: int) -> None:
        self.kind = kind
        self.begin = begin
        self.end = end
        self._next = None
        self.val = 0

    @property
    def next(self) -> "Token":
        return cast(Token, self._next)

    @next.setter
    def next(self, next: "Token") -> None:
        self._next = next


class Parser:
    current_input: str

    def __init__(self, text):
        self.current_input = text

    class Failure(RuntimeError):
        pass

    def error_at(self, loc: int, *args, **kwargs) -> NoReturn:
        print(self.current_input, file=stderr)
        print(" " * loc, file=stderr, end="")
        print("^ ", file=stderr, end="")
        print(*args, **kwargs, file=stderr)
        raise Parser.Failure()

    def error_tok(self, tok: Token, *args, **kwargs) -> NoReturn:
        self.error_at(tok.begin, *args, **kwargs)

    def equal(self, tok: Token, op: str) -> bool:
        return self.current_input[tok.begin : tok.end] == op

    def skip(self, tok: Token, s: str) -> Token:
        if self.equal(tok, s):
            return cast(Token, tok.next)

        self.error_tok(tok, f"expected '{s}'")

    def get_num(self, tok: Token) -> int:
        if tok.kind != Token.Kind.NUM:
            self.error_tok(tok, "expected number")

        return tok.val

    def tokenize(self) -> Token:
        i = 0
        head = Token(Token.Kind.NUM, 0, 0)
        cur = head

        while i < len(self.current_input):
            match self.current_input[i]:
                case c if c.isspace():
                    i += 1
                case c if c.isdigit():
                    text, _ = parse_num(self.current_input[i:])
                    i += len(text)
                    cur.next = Token(Token.Kind.NUM, i, i + len(text))
                    cur.next.val = int(text)
                    cur = cur.next
                case "+" | "-":
                    cur.next = Token(Token.Kind.PUNCT, i, i + 1)
                    cur = cur.next
                    i += 1
                case c:
                    self.error_at(i, "invalid token")

        cur.next = Token(Token.Kind.EOF, i, i)
        return cast(Token, head.next)


def chibicc(args: list[str], writer: TextIO) -> int:
    if len(args) != 2:
        write(stderr, f"{args[0]}: invalid number of arguments")
        return 1

    text = args[1]
    if len(text) == 0:
        write(stderr, "you can't trick me")
        return 1

    p = Parser(text)

    try:
        tok = p.tokenize()
    except Parser.Failure:
        return 1

    write(writer, "    .global main")
    write(writer, "main:")
    write(writer, f"    mov ${p.get_num(tok)}, %rax")
    tok = tok.next
    while tok.kind != Token.Kind.EOF:
        if p.equal(tok, "+"):
            write(writer, f"    add ${p.get_num(tok.next)}, %rax")
            tok = tok.next.next
        else:
            tok = p.skip(tok, "-")
            write(writer, f"    sub ${p.get_num(tok)}, %rax")
            tok = tok.next

    write(writer, "    ret")
    return 0
