# Copyright (C) 2026 BasaltDev
# SPDX-License-Identifier: GPL-3.0-only

from enum import Enum, auto


class TokenType(Enum):
    KEYWORD = auto()
    DATA_TYPE = auto()
    IDENTIFIER = auto()
    STRING = auto()
    INTEGER = auto()
    FLOAT = auto()
    BOOLEAN = auto()

    LEFTPAREN = auto()
    RIGHTPAREN = auto()
    LEFTBRACKET = auto()
    RIGHTBRACKET = auto()
    LEFTBRACE = auto()
    RIGHTBRACE = auto()

    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    BACKSLASH = auto()
    MOD = auto()
    EQUALS = auto()
    NOTEQUALS = auto()
    LESSTHAN = auto()
    GREATERTHAN = auto()
    LESSTHANOREQUAL = auto()
    GREATERTHANOREQUAL = auto()
    AND = auto()
    OR = auto()
    NOT = auto()

    COMPOUNDASSIGNMENT = auto()
    INCREMENT = auto()
    DECREMENT = auto()

    PERIOD = auto()
    COMMA = auto()
    COLON = auto()
    SEMICOLON = auto()
    ASSIGN = auto()


class Token:
    def __init__(self, typ=None, value=None, line=None, col=None, colEnd=None):
        self.type = typ
        self.value = value
        self.line = line
        self.col = col
        self.colEnd = colEnd

    def __repr__(self):
        return f"Token(type={self.type.name}, value={repr(self.value)})"

    def __eq__(self, value):
        if not isinstance(value, (Token, TokenType)):
            return False
        if isinstance(value, TokenType):
            return value == self.type
        return value.type == self.type and value.value == self.value
