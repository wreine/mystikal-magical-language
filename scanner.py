from spellbook import SPELLBOOK

SIGNS = "+-*/=<>!:(),.[]{};%^&|~"
NO_METHODS = ["def", "class", "lambda", "return", "yield"]
NO_ADVANCED = ["import", "from", "global", "nonlocal", "async", "await", "with", "del", "assert"]


class Kind:
    """The kinds of rune (token). Plain text labels."""
    SPELL = "SPELL"      # a magic word from the spellbook
    NAME = "NAME"        # an ordinary name
    NUMBER = "NUMBER"
    TEXT = "TEXT"        # string literal
    SIGN = "SIGN"        # operator / punctuation
    NOTE = "NOTE"        # comment
    GAP = "GAP"          # whitespace (kept so indentation survives)


class Rune:
    """One piece (token) of the source code."""

    def __init__(self, kind, text, line, col):
        self.kind = kind
        self.text = text
        self.line = line
        self.col = col


class ScanOutcome:
    """Result of scanning: either runes or a problem message."""

    def __init__(self, runes, problem):
        self.runes = runes
        self.problem = problem


class MystikaError(Exception):
    """Base class for every Mystika error."""


class ScanError(MystikaError):
    def __init__(self, line, col, message):
        super().__init__(message)
        self.line = line
        self.col = col
        self.message = message


def is_word_char(c):
    return c.isalnum() or c == "_"


def is_not_newline(c):
    return c != "\n"


class Cursor:
    """A finger moving through the source text (encapsulation: state stays inside)."""

    def __init__(self, source):
        self.src = source
        self.pos = 0
        self.line = 1
        self.col = 1

    def peek(self, ahead=0):
        """Look at a character without moving."""
        i = self.pos + ahead
        if i < len(self.src):
            return self.src[i]
        return ""

    def take(self):
        """Read one character and move forward."""
        ch = self.src[self.pos]
        self.pos += 1
        if ch == "\n":
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        return ch

    def take_while(self, test):
        """Keep taking characters while test(character) is True."""
        start = self.pos
        while self.peek() != "" and test(self.peek()):
            self.take()
        return self.src[start:self.pos]

    def at_end(self):
        return self.pos >= len(self.src)


def read_text(cur):
    """Read a quoted string (single, double or triple-quoted)."""
    start_line = cur.line
    start_col = cur.col
    quote = cur.peek()
    begin = cur.pos
    triple = cur.src.startswith(quote * 3, cur.pos)

    if triple:
        for _ in range(3):
            cur.take()
        while True:
            if cur.at_end():
                raise ScanError(start_line, start_col, "Triple-quoted text was never closed")
            if cur.peek() == "\\":
                cur.take()
                if not cur.at_end():
                    cur.take()
            elif cur.src.startswith(quote * 3, cur.pos):
                for _ in range(3):
                    cur.take()
                break
            else:
                cur.take()
    else:
        cur.take()
        while True:
            ch = cur.peek()
            if ch == "" or ch == "\n":
                raise ScanError(start_line, start_col, "Text was never closed")
            if ch == "\\":
                cur.take()
                if cur.peek() == "":
                    raise ScanError(start_line, start_col, "Text was never closed")
                cur.take()
            elif ch == quote:
                cur.take()
                break
            else:
                cur.take()
    return cur.src[begin:cur.pos]


def read_number(cur):
    begin = cur.pos
    cur.take_while(str.isdigit)
    if cur.peek() == "." and cur.peek(1).isdigit():
        cur.take()
        cur.take_while(str.isdigit)
    return cur.src[begin:cur.pos]


def check_forbidden(runes):
    """Return a problem text if the source uses something Mystika does not allow."""
    for rune in runes:
        message = ""
        if rune.kind == Kind.NAME and rune.text in NO_METHODS:
            message = ("Bawal gumawa ng sariling kapangyarihan ('" + rune.text +
                       "'). Walang method, function o class sa Mystika.")
        elif rune.kind == Kind.NAME and rune.text in NO_ADVANCED:
            message = "Bawal na spell ang '" + rune.text + "'. Hindi ito kasama sa wikang Mystika."
        elif rune.kind == Kind.SIGN and rune.text == ".":
            message = "Bawal ang tuldok na tumatawag ng method. Walang method sa Mystika."

        if message != "":
            return ("[Bawal na Spell] Line " + str(rune.line) + ", column " +
                    str(rune.col) + ": " + message)
    return None


def scan(source):
    """Turn source text into runes. Problems come back as text, never as a crash."""
    if not isinstance(source, str):
        return ScanOutcome(None, "[Scanner] Source must be text")

    cur = Cursor(source)
    runes = []

    try:
        while not cur.at_end():
            line = cur.line
            col = cur.col
            ch = cur.peek()

            if ch.isspace():
                runes.append(Rune(Kind.GAP, cur.take_while(str.isspace), line, col))
            elif ch == "#":
                runes.append(Rune(Kind.NOTE, cur.take_while(is_not_newline), line, col))
            elif ch.isalpha() or ch == "_":
                word = cur.take_while(is_word_char)
                if word in SPELLBOOK:
                    runes.append(Rune(Kind.SPELL, word, line, col))
                else:
                    runes.append(Rune(Kind.NAME, word, line, col))
            elif ch.isdigit():
                runes.append(Rune(Kind.NUMBER, read_number(cur), line, col))
            elif ch == '"' or ch == "'":
                runes.append(Rune(Kind.TEXT, read_text(cur), line, col))
            elif ch in SIGNS:
                runes.append(Rune(Kind.SIGN, cur.take(), line, col))
            else:
                raise ScanError(line, col, "Unknown rune " + repr(ch))
    except ScanError as err:
        return ScanOutcome(None, "[Scanner] Line " + str(err.line) + ", column " +
                           str(err.col) + ": " + err.message)

    problem = check_forbidden(runes)
    if problem is not None:
        return ScanOutcome(None, problem)
    return ScanOutcome(runes, None)