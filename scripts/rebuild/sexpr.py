"""Minimal S-expression reader/writer for KiCad files."""
from __future__ import annotations

import re

TOKEN = re.compile(r'\(|\)|"(?:\\.|[^"\\])*"|[^\s()]+')


class Sym(str):
    """Unquoted atom."""


def parse(text: str):
    stack: list[list] = [[]]
    for tok in TOKEN.findall(text):
        if tok == "(":
            stack.append([])
        elif tok == ")":
            done = stack.pop()
            stack[-1].append(done)
        elif tok.startswith('"'):
            stack[-1].append(bytes(tok[1:-1], "utf-8").decode("unicode_escape") if "\\" in tok else tok[1:-1])
        else:
            stack[-1].append(Sym(tok))
    return stack[0]


def q(value: str) -> str:
    return '"' + str(value).replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'


def dump(node, indent: int = 0) -> str:
    if isinstance(node, list):
        if not node:
            return "()"
        simple = all(not isinstance(n, list) for n in node)
        if simple:
            return "(" + " ".join(dump(n) for n in node) + ")"
        pad = "\t" * (indent + 1)
        head = []
        rest = node
        while rest and not isinstance(rest[0], list):
            head.append(dump(rest[0]))
            rest = rest[1:]
        out = "(" + " ".join(head)
        for child in rest:
            out += "\n" + pad + dump(child, indent + 1)
        return out + "\n" + "\t" * indent + ")"
    if isinstance(node, Sym):
        return str(node)
    if isinstance(node, (int, float)):
        return fmt_num(node)
    return q(node)


def fmt_num(v: float) -> str:
    if isinstance(v, int):
        return str(v)
    s = f"{v:.4f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def find(node: list, key: str):
    for child in node:
        if isinstance(child, list) and child and child[0] == key:
            return child
    return None


def find_all(node: list, key: str):
    return [c for c in node if isinstance(c, list) and c and c[0] == key]
