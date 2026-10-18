from scanner import Kind
from spellbook import SPELLBOOK


class Weaving:
    """The translated Python code plus a map of line numbers."""

    def __init__(self, python, line_map):
        self.python = python
        self.line_map = line_map     # python line -> mystika line


def weave(runes):
    """Replace every spell with its Python word using the SPELLBOOK dictionary."""
    pieces = []
    line_map = {}
    py_line = 1

    for rune in runes:
        if rune.kind == Kind.SPELL:
            output = SPELLBOOK[rune.text]
        else:
            output = rune.text
        pieces.append(output)

        if py_line not in line_map:
            line_map[py_line] = rune.line
        extra_lines = output.count("\n")
        for step in range(1, extra_lines + 1):
            line_map[py_line + step] = rune.line + step
        py_line += extra_lines

    return Weaving("".join(pieces), line_map)